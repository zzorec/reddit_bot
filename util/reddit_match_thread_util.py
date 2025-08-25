import re
import time
from datetime import timedelta, datetime
from json import JSONDecodeError
from typing import Final

import pytz
import requests
from prawcore import RequestException, ServerError, Forbidden

from reddit_bot.config import config
from reddit_bot.data import resources, variables
from reddit_bot.util.date_util import format_date, format_time
from reddit_bot.util.format_util import add_league_table, add_knockout_stages
from reddit_bot.util.logging_util import logger
from reddit_bot.util.rapidapi_util import fetch_next_game
from reddit_bot.util.reddit_submission_util import create_submission


# Create pre-match discussion thread one day before match and match discussion thread one hour before match.
def match_threads_creator(reddit_instance) -> None:
    while True:
        next_match = fetch_next_game()  # Get information about next game.

        if not next_match:  # In case no information is available for next game.
            logger.info("Match thread organizer didn't find any upcoming games.")
            time.sleep(config.Reddit.MATCH_THREAD_CHECK_INTERVAL)  # Wait 30 minutes before checking again.
            continue

        logger.info("Checking next matches for creation of match threads.")

        # Get date of next match and subtract remaining time.
        match_date = datetime.fromisoformat(next_match["fixture"]["date"].replace("Z", "+00:00")).astimezone(pytz.timezone("Europe/Rome"))
        remaining_until_next_game = match_date - datetime.now(pytz.timezone("Europe/Rome"))

        match_teams = f"{next_match['teams']['home']['name']} - {next_match['teams']['away']['name']}"

        if remaining_until_next_game < timedelta(days=1) and not variables.MatchThreadVariables.pre_match_thread_created:  # If less than a day away from a match, create pre-match thread.
            logger.info(f"Creating a pre-match discussion thread for: {match_teams}")
            try:
                create_pre_match_thread(reddit_instance, None, next_match)
            except Exception:
                logger.exception("Error while scheduler tried to create a new pre-match discussion thread.")

        if remaining_until_next_game < timedelta(minutes=60) and not variables.MatchThreadVariables.live_match_thread_created:  # If less than an hour away from a match, create live-match thread.
            logger.info(f"Creating a live-match discussion thread for: {match_teams}")
            try:
                create_live_match_thread(reddit_instance, None, next_match)
            except Exception:
                logger.exception("Error while scheduler tried to create a new live-match discussion thread.")
        time.sleep(config.Reddit.MATCH_THREAD_CHECK_INTERVAL)  # Wait 30 minutes before checking again.


def create_pre_match_thread(reddit_instance, comment, next_match) -> None:
    variables.MatchThreadVariables.pre_match_thread_created = True
    subreddit = reddit_instance.subreddit(config.Reddit.SUBREDDIT_NAME)

    next_game_info_json = next_match or fetch_next_game()

    # Define title.
    submission_title = "[Pre-Match Discussion Thread] " + next_game_info_json["teams"]["home"]["name"] + " vs " + next_game_info_json["teams"]["away"]["name"] + " (" + next_game_info_json["league"]["name"] + ", " + next_game_info_json["league"]["round"].replace("Regular Season -", "Matchday") + ")"

    # Check if pre-match thread already exists.
    existing_submissions = subreddit.new(limit=config.Reddit.SUBMISSION_CHECK_BATCH_SIZE)
    for existing_submission in existing_submissions:
        if submission_title == existing_submission.title:
            if comment is not None:
                comment.reply(f"{resources.CommentReplies.PRE_MATCH_DISCUSSION_EXISTS}{existing_submission.url}.")
            return

    # Prepare thread contents - details.
    submission_content = "---\n\n## 📋 Match Info 📋\n\n"
    if next_game_info_json["fixture"].get("date"):
        submission_content += f"\n- **Date:** {format_date(next_game_info_json['fixture']['date'], False, True)}"
        submission_content += f"\n- **Time:** {format_time(next_game_info_json['fixture']['date'])} (GMT+1)"
    if next_game_info_json["fixture"]["venue"].get("name"):
        submission_content += f"\n- **Venue:** {next_game_info_json['fixture']['venue']['name']}"
    if next_game_info_json.get("league"):
        submission_content += f"\n- **Competition:** {next_game_info_json['league']['name']}"
    if next_game_info_json["league"]["name"] == "Serie A":
        submission_content += f"\n- **Matchday:** {next_game_info_json['league']['round'].replace('Regular Season - ', '')}"
    if next_game_info_json["league"]["name"] != "Serie A" and next_game_info_json["league"]["name"] != "Friendlies Clubs":
        submission_content += f"\n- **Round:** {next_game_info_json['league']['round']}"
    submission_content += "\n\n---\n\n"

    if next_game_info_json["league"]["name"] == "Serie A":
        submission_content = add_league_table(submission_content, next_game_info_json["league"]["id"], "Serie A")
        submission_content += "\n\n---\n\n"

    if next_game_info_json["league"]["name"] == "UEFA Champions League":
        submission_content = add_league_table(submission_content, next_game_info_json["league"]["id"], "Champions League")
        submission_content = add_knockout_stages(submission_content, next_game_info_json["league"]["id"], "Champions League")
        submission_content += "\n\n---\n\n"

    if next_game_info_json["league"]["name"] == "FIFA Club World Cup":
        submission_content = add_league_table(submission_content, next_game_info_json["league"]["id"], "Club World Cup")
        submission_content = add_knockout_stages(submission_content, next_game_info_json["league"]["id"], "Club World Cup")
        submission_content += "\n\n---\n\n"

    if next_game_info_json["league"]["name"] == "Coppa Italia":
        submission_content = add_knockout_stages(submission_content, next_game_info_json["league"]["id"], "Coppa Italia")
        submission_content += "\n\n---\n\n"

    # Prepare thread contents - injuries.
    injuries_url = config.FootballRapidApi.get_injuries_by_fixture_id_url(next_game_info_json["fixture"]["id"])
    logger.info("Football Rapid API: Fetched injuries for pre-match thread.")
    injuries_json = requests.get(injuries_url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS).json()
    injuries_data = injuries_json.get("response", [])
    if injuries_data:
        submission_content += "## 🏥 Injured/Suspended Players 🏥\n\n"
        submission_content += "^(*This bot feature is still in beta, information could be inaccurate.*)\n\n"
        submission_content += "| Player | Reason | Status | Team |\n"
        submission_content += "|:--|:-:|:-:|:-:|\n"
        for item in injuries_data:
            submission_content += f"| {item['player']['name']} | {item['player']['reason']} | {item['player']['type']} | {item['team']['name']} |\n"
        submission_content += "\n\n---\n\n"

    # Prepare thread contents - head-2-head.
    h2h_url = config.FootballRapidApi.get_h2h_by_team_id_url(next_game_info_json['teams']['home']['id'], next_game_info_json['teams']['away']['id'])
    logger.info("Football Rapid API: Fetched head-2-head for pre-match thread.")
    h2h_json = requests.get(h2h_url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS).json()
    h2h_data_fixtures = h2h_json.get("response", [])

    if h2h_data_fixtures:
        submission_content += "## ⚔️ Head-to-Head ⚔️\n\n"
        submission_content += "### Statistics\n\n"
        submission_content += "^(*H2H statistics may include only fixtures from recent years and may not represent overall historical data.*)\n\n"

        home_team = next_game_info_json["teams"]["home"]["name"]
        away_team = next_game_info_json["teams"]["away"]["name"]

        # Only consider completed matches for statistics
        completed_matches = [match for match in h2h_data_fixtures if match["fixture"]["status"]["short"] in ["FT", "AET", "PEN"]]

        total_played = len(completed_matches)
        home_wins = 0
        away_wins = 0
        draws = 0

        for match in completed_matches:
            home_id = match["teams"]["home"]["id"]
            away_id = match["teams"]["away"]["id"]
            home_goals = match["goals"]["home"]
            away_goals = match["goals"]["away"]

            if home_goals == away_goals:
                draws += 1
            elif home_goals > away_goals:
                if home_id == next_game_info_json["teams"]["home"]["id"]:
                    home_wins += 1
                else:
                    away_wins += 1
            else:
                if away_id == next_game_info_json["teams"]["away"]["id"]:
                    away_wins += 1
                else:
                    home_wins += 1

        submission_content += f"| Total Played | {home_team} Win | Draw | {away_team} Win |\n"
        submission_content += "|:-:|:-:|:-:|:-:|\n"
        submission_content += f"| {total_played} | {home_wins} | {draws} | {away_wins} |\n"

        sorted_fixtures = sorted(completed_matches, key=lambda match: match["fixture"]["timestamp"], reverse=True)[:8]

        if sorted_fixtures:
            submission_content += "\n### Latest Results\n\n"
            submission_content += "| Home | Score | Away | Date | Competition |\n"
            submission_content += "|:-:|:-:|:-:|:-:|:-:|\n"

            for match in sorted_fixtures:
                home = match["teams"]["home"]["name"]
                away = match["teams"]["away"]["name"]
                home_goals = match["goals"]["home"]
                away_goals = match["goals"]["away"]
                date = format_date(match["fixture"]["date"], True, True)
                competition = match["league"]["name"]

                if home_goals > away_goals:
                    submission_content += f"| **{home}** | {home_goals}-{away_goals} | {away} | {date} | {competition} |\n"
                elif home_goals < away_goals:
                    submission_content += f"| {home} | {home_goals}-{away_goals} | **{away}** | {date} | {competition} |\n"
                else:
                    submission_content += f"| {home} | {home_goals}-{away_goals} | {away} | {date} | {competition} |\n"

        submission_content += "\n\n---\n\n"

    # Create pre-match discussion thread
    submission = create_submission(reddit_instance, submission_title, submission_content)
    logger.info(f"Created pre-match discussion thread: {submission_title} ({next_game_info_json['fixture']['id']})")

    # Reply to comment if it exists.
    if comment is not None:
        comment.reply(f"{resources.CommentReplies.PRE_MATCH_DISCUSSION_CREATED}{submission.url}.")


def create_live_match_thread(reddit_instance, comment, next_match):
    variables.MatchThreadVariables.live_match_thread_created = True
    subreddit = reddit_instance.subreddit(config.Reddit.SUBREDDIT_NAME)

    if next_match is None:
        next_game_info_json = fetch_next_game()  # Get info for next game.
    else:
        next_game_info_json = next_match  # Next match information was already provided by matchThreadsCreator.

    # Define matchId to update the thread mid-game.
    variables.MatchThreadVariables.live_match_football_api_id = int(next_game_info_json["fixture"]["id"])

    # Define title.
    submission_title = "[Match Thread] " + next_game_info_json["teams"]["home"]["name"] + " vs " + next_game_info_json["teams"]["away"]["name"] + " (" + next_game_info_json["league"]["name"] + ", " + next_game_info_json["league"]["round"].replace("Regular Season -", "Matchday") + ")"

    # Check if match thread already exists.
    existing_submissions = subreddit.new(limit=config.Reddit.SUBMISSION_CHECK_BATCH_SIZE)
    for existing_submission in existing_submissions:
        if submission_title == existing_submission.title:
            if comment is not None:
                comment.reply(resources.CommentReplies.MATCH_DISCUSSION_EXISTS + existing_submission.url + ".")
            return

    # Prepare thread contents.
    submission_content = ""
    if next_game_info_json["fixture"]["status"]["short"] in ["FT", "AET", "PEN"]:
        submission_content += f"# Full Time: {next_game_info_json['teams']['home']['name']} {next_game_info_json['goals']['home']}-{next_game_info_json['goals']['away']} {next_game_info_json['teams']['away']['name']}\n\n"
    elif next_game_info_json["fixture"]["status"]["short"] == "HT":
        submission_content += f"# Half Time: {next_game_info_json['teams']['home']['name']} {next_game_info_json['goals']['home']}-{next_game_info_json['goals']['away']} {next_game_info_json['teams']['away']['name']}\n\n"
    else:
        submission_content += f"# {next_game_info_json['fixture']['status']['elapsed']}′: {next_game_info_json['teams']['home']['name']} {next_game_info_json['goals']['home']}-{next_game_info_json['goals']['away']} {next_game_info_json['teams']['away']['name']}\n\n"

    goals_home = ""
    goals_away = ""
    if next_game_info_json.get("events"):
        for event in next_game_info_json["events"]:
            if event.get("type", "") == "Goal" and event.get("team_id", "") == next_game_info_json["teams"]["home"]["id"]:
                goals_home += f" {event.get('player', '')} ({event.get('elapsed', '')}′)"
            elif event.get("type", "") == "Goal" and event.get("team_id", "") == next_game_info_json["teams"]["away"]["id"]:
                goals_away += f" {event.get('player', '')} ({event.get('elapsed', '')}′)"

    if goals_home:
        submission_content += f" **{next_game_info_json['teams']['home']['name']}:** {goals_home}.\n\n"
    if goals_away:
        submission_content += f" **{next_game_info_json['teams']['away']['name']}:** {goals_away}.\n\n"

    submission_content += "\n\n---\n\n"
    if next_game_info_json["fixture"].get("venue"):
        submission_content += f"**Venue:** {next_game_info_json['fixture']['venue']['name']}\n\n"
    submission_content += "\n\n---\n\n"
    submission_content = submission_content.replace("None", "0")

    # Create match thread and set ongoing match thread ID.
    submission = create_submission(reddit_instance, submission_title, submission_content)
    logger.info("Created match thread: " + submission_title + "(" + str(next_game_info_json["fixture"]["id"]) + ")")
    variables.MatchThreadVariables.live_match_reddit_submission_id = submission.id

    # Reply to comment if it exists.
    if comment is not None:
        comment.reply(resources.CommentReplies.MATCH_DISCUSSION_CREATED + submission.url + ".")


def match_threads_updater(reddit_instance):
    # Live game in progress, update it.
    while True:
        if variables.MatchThreadVariables.live_match_thread_created:
            time.sleep(config.Reddit.MATCH_THREAD_UPDATE_INTERVAL)
            try:
                update_match_thread(reddit_instance)
            except (RequestException, ServerError, Forbidden) as e:  # This error handling is needed because sometimes, Reddit API will error out and would stop the processing thread.
                logger.warning(f"{e} - Error communicating with Reddit when updating match thread!")


def update_match_thread(reddit_instance):
    def get_safe_name_str(name, default="Unknown"):  # Helper function to safely get any name with consistent handling
        MOJIBAKE_MAP: Final[dict[str, str]] = {
            'Ã‡': 'Ç', 'Ã§': 'ç', 'Ã¼': 'ü', 'Ã¤': 'ä', 'Ã¶': 'ö', 'ÃŸ': 'ß',
            'Ã©': 'é', 'Ã¨': 'è', 'Ãª': 'ê', 'Ã«': 'ë', 'Ã¡': 'á', 'Ã ': 'à',
            'Ã¢': 'â', 'Ã£': 'ã', 'Ã±': 'ñ', 'Ã³': 'ó', 'Ã²': 'ò', 'Ã´': 'ô',
            'Ãµ': 'õ', 'Ã¸': 'ø', 'Ã¥': 'å', 'Ã‰': 'É', 'Ãœ': 'Ü', 'Ã–': 'Ö',
            'Ã„': 'Ä', 'â€™': "'", 'â€“': '-', 'Ã®': 'î', 'Ã¯': 'ï', 'Ã¬': 'ì',
            'Ã­': 'í', 'Ã¿': 'ÿ', 'Ã½': 'ý', 'Å¡': 'š', 'Å¾': 'ž', 'Ä‡': 'ć',
            'Å‚': 'ł', 'Ä™': 'ę', 'Å„': 'ń', 'Åº': 'ź', 'Ä…': 'ą', 'Ä': 'č',
            'Å¥': 'ť', 'ÄŸ': 'ğ', 'Ä±': 'ı', 'ÅŸ': 'ş'
        }
        MOJIBAKE_REGEX: Final[re.Pattern] = re.compile('|'.join(map(re.escape, MOJIBAKE_MAP)))
        MOJIBAKE_MARKERS: Final[tuple[str, ...]] = ('Ã', 'Â', 'Ä')

        if name is None or name == "null":
            return default
        if isinstance(name, bytes):
            name = name.decode('utf-8', errors='replace')
        else:
            name = str(name)
        if any(marker in name for marker in MOJIBAKE_MARKERS):
            name = MOJIBAKE_REGEX.sub(lambda m: MOJIBAKE_MAP[m.group(0)], name)
            if any(marker in name for marker in MOJIBAKE_MARKERS):
                try:
                    name = name.encode('latin1').decode('utf-8')
                except UnicodeDecodeError:
                    pass
        return name

    # Get information about game
    url = config.FootballRapidApi.get_fixture_by_id_url(variables.MatchThreadVariables.live_match_football_api_id)
    logger.info("Football Rapid API: Fetched fixture details for updating match thread.")
    try:
        response = requests.get(url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS).json()
        game_info_json = response["response"][0]
    except (KeyError, IndexError, JSONDecodeError) as e:
        logger.error(f"Failed to parse API response: {str(e)}")
        return

    # Retry logic for events data.
    retry_count = 0
    elapsed_time = game_info_json.get("fixture", {}).get("status", {}).get("elapsed")

    # Only perform check if game has actually started and events should exist
    if elapsed_time is not None and elapsed_time > 0 and variables.MatchThreadVariables.live_match_events_already_existed:
        while not game_info_json.get("events"):
            logger.warning("Fetched game data for live match thread doesn't contain events, retrying...")
            time.sleep(10)
            try:
                response = requests.get(url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS).json()
                game_info_json = response["response"][0]
            except (KeyError, IndexError) as e:
                logger.error(f"Failed to parse API response during retry: {str(e)}")
                break
            retry_count += 1
            if retry_count > 2:
                logger.warning("Reached max retries while trying to fetch events data for live match thread.")
                break

    # Generate match thread content
    submission_content = "\n\n---\n\n"

    # Handle different match statuses
    status_short = game_info_json.get("fixture", {}).get("status", {}).get("short", "")
    home_goals = game_info_json.get("goals", {}).get("home", 0) or 0
    away_goals = game_info_json.get("goals", {}).get("away", 0) or 0

    # Get safe team names
    home_team_name = get_safe_name_str(game_info_json['teams']['home'].get('name', 'Home Team'))
    away_team_name = get_safe_name_str(game_info_json['teams']['away'].get('name', 'Away Team'))

    if status_short in ["FT", "AET", "PEN"]:
        submission_content += f"# Full Time: {home_team_name} {home_goals}-{away_goals} {away_team_name}\n\n"
    elif status_short == "HT":
        submission_content += f"# Half Time: {home_team_name} {home_goals}-{away_goals} {away_team_name}\n\n"
    elif elapsed_time is not None:
        submission_content += f"# {elapsed_time}′: {home_team_name} {home_goals}-{away_goals} {away_team_name}\n\n"
    else:
        submission_content += f"# {home_team_name} vs {away_team_name} - Match Not Started\n\n"

    # Process goals
    goals_home = ""
    goals_away = ""
    if game_info_json.get("events"):
        variables.MatchThreadVariables.live_match_events_already_existed = True  # Set the flag to True to enable retry logic if events are not included in API response data.

        goals_home_list = []
        goals_away_list = []

        for event in game_info_json["events"]:
            try:
                if event.get("type") == "Goal" and event.get("detail") != "Missed Penalty":
                    team_id = event.get("team", {}).get("id")
                    player_name = get_safe_name_str(event.get("player", {}).get("name", "Unknown Player"))
                    time_elapsed = event.get("time", {}).get("elapsed", "?")

                    goal_entry = f"{player_name} ({time_elapsed}′)"

                    if team_id == game_info_json["teams"]["home"]["id"]:
                        goals_home_list.append(goal_entry)
                    elif team_id == game_info_json["teams"]["away"]["id"]:
                        goals_away_list.append(goal_entry)
            except Exception as e:
                logger.error(f"Error processing event: {str(e)}")
                continue
        goals_home = ", ".join(goals_home_list)
        goals_away = ", ".join(goals_away_list)

    else:
        logger.warning("Live match thread: couldn't extract team goals, no 'events' information in JSON data.")

    if goals_home:
        submission_content += f" **{home_team_name}:** {goals_home}.\n\n"
    if goals_away:
        submission_content += f" **{away_team_name}:** {goals_away}.\n\n"

    submission_content += "\n\n---\n\n"

    # Add venue and referee info with safe name handling
    venue_name = game_info_json.get("fixture", {}).get("venue", {}).get("name")
    if venue_name:
        submission_content += f"**Venue:** {get_safe_name_str(venue_name)}\n\n"

    referee_name = game_info_json.get("fixture", {}).get("referee")
    if referee_name:
        submission_content += f"**Referee:** {get_safe_name_str(referee_name)}\n\n"

    # Process lineups
    try:
        lineups = game_info_json.get("lineups", [])
        if (len(lineups) >= 2 and
                lineups[0].get("team") and lineups[0].get("startXI") and lineups[0].get("substitutes") and
                lineups[1].get("team") and lineups[1].get("startXI") and lineups[1].get("substitutes")):
            submission_content += "\n\n---\n\n"
            home_line_up = lineups[0]
            away_line_up = lineups[1]
            submission_content += "### Lineups\n\n"

            # Process home lineup
            try:
                home_line_up["start"] = ", ".join(
                    get_safe_name_str(player.get("player", {}).get("name", "Unknown Player"))
                    for player in home_line_up["startXI"]
                )
                home_line_up["subs"] = ", ".join(
                    get_safe_name_str(sub.get("player", {}).get("name", "Unknown Player"))
                    for sub in home_line_up["substitutes"]
                )
                submission_content += f"#### {home_team_name}\n\n"
                submission_content += f" **Starting XI:** {home_line_up['start']}\n\n"
                submission_content += f" **Substitutes:** {home_line_up['subs']}\n\n"
                if home_line_up.get("coach", {}).get("name"):
                    submission_content += f" **Coach:** {get_safe_name_str(home_line_up['coach']['name'])}\n\n"
            except Exception as e:
                logger.error(f"Error processing home lineup: {str(e)}")

            # Process away lineup
            try:
                away_line_up["start"] = ", ".join(
                    get_safe_name_str(player.get("player", {}).get("name", "Unknown Player"))
                    for player in away_line_up["startXI"]
                )
                away_line_up["subs"] = ", ".join(
                    get_safe_name_str(sub.get("player", {}).get("name", "Unknown Player"))
                    for sub in away_line_up["substitutes"]
                )
                submission_content += f"#### {away_team_name}\n\n"
                submission_content += f" **Starting XI:** {away_line_up['start']}\n\n"
                submission_content += f" **Substitutes:** {away_line_up['subs']}\n\n"
                if away_line_up.get("coach", {}).get("name"):
                    submission_content += f" **Coach:** {get_safe_name_str(away_line_up['coach']['name'])}\n\n"
            except Exception as e:
                logger.error(f"Error processing away lineup: {str(e)}")
        else:
            logger.warning("Live match thread: couldn't extract team lineups, incomplete 'lineups' information in JSON data.")
    except Exception as e:
        logger.error(f"Error while parsing team lineups: {str(e)}")

    # Process events
    events = game_info_json.get("events", [])
    if events:
        submission_content += "\n\n---\n\n"
        submission_content += "### Match Events\n\n"
        submission_content += "| Min | Event |\n"
        submission_content += "|:-:|:--|\n"

        for event in events:
            try:
                event_type = event.get("type")
                time_elapsed = event.get("time", {}).get("elapsed", "?")
                team_name = get_safe_name_str(event.get("team", {}).get("name", "Unknown Team"))
                player_name = get_safe_name_str(event.get("player", {}).get("name", "Unknown Player"))
                assist_name = get_safe_name_str(event.get("assist", {}).get("name")) if event.get("assist") else None
                detail = event.get("detail", "")

                if event_type == "Goal" and detail == "Missed Penalty":
                    submission_content += f"| {time_elapsed}′ | ❌ **Missed Penalty ({team_name}):** {player_name}. |\n"
                elif event_type == "Goal" and event.get("team", {}).get("id") == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID:
                    assist_text = f", assist by {assist_name}" if assist_name and assist_name != "Unknown" else ""
                    penalty_text = " (Penalty)" if detail == "Penalty" else ""
                    submission_content += f"| {time_elapsed}′ | ⚽ **GOAAAAAAAL (Inter): {player_name}{assist_text}{penalty_text}. Forza Inter!** ⚫🔵 |\n"
                elif event_type == "Goal":
                    assist_text = f", assist by {assist_name}" if assist_name and assist_name != "Unknown" else ""
                    penalty_text = " (Penalty)" if detail == "Penalty" else ""
                    submission_content += f"| {time_elapsed}′ | ⚽ **Goal ({team_name}): {player_name}{assist_text}{penalty_text}.** |\n"
                elif event_type == "Card" and detail == "Yellow Card":
                    submission_content += f"| {time_elapsed}′ | **🟨 Yellow card ({team_name}):** {player_name}. |\n"
                elif event_type == "Card" and detail == "Red Card":
                    submission_content += f"| {time_elapsed}′ | **🟥 Red card ({team_name}):** {player_name}. |\n"
                elif event_type == "subst" and assist_name:
                    submission_content += f"| {time_elapsed}′ | **🔄 Sub ({team_name}):** {assist_name} replaces {player_name}. |\n"
            except Exception as e:
                logger.error(f"Error processing event: {str(e)}")
                continue
    else:
        logger.warning("Live match thread: couldn't extract game events, no 'events' information in JSON data.")

    # Process statistics
    if game_info_json.get("statistics"):
        try:
            submission_content += "\n\n---\n\n"
            submission_content += "### Match Stats\n\n"

            stats_home = game_info_json["statistics"][0].get("statistics", [])
            stats_away = game_info_json["statistics"][1].get("statistics", [])

            submission_content += f"| {home_team_name} |  | {away_team_name} |\n"
            submission_content += "|:-:|:-:|:-:|\n"

            stat_mapping = {
                "Ball Possession": "Ball Possession",
                "Total Shots": "Total Shots",
                "Shots on Goal": "Shots On-Goal",
                "Shots off Goal": "Shots Off-Goal",
                "Blocked Shots": "Blocked Shots",
                "Shots insidebox": "Shots Inside Box",
                "Shots outsidebox": "Shots Outside Box",
                "Fouls": "Fouls",
                "Corner Kicks": "Corner Kicks",
                "Offsides": "Offsides",
                "Yellow Cards": "Yellow Cards",
                "Red Cards": "Red Cards",
                "Total passes": "Total passes",
                "Passes accurate": "Accurate passes",
                "Passes %": "Passing accuracy"
            }

            for stat_type, display_name in stat_mapping.items():
                home_value = next((s.get("value", "0") for s in stats_home if s.get("type") == stat_type), "0")
                away_value = next((s.get("value", "0") for s in stats_away if s.get("type") == stat_type), "0")
                submission_content += f"| {home_value} | {display_name} | {away_value} |\n"
        except Exception as e:
            logger.error(f"Error processing statistics: {str(e)}")
    else:
        logger.warning("Live match thread: couldn't extract statistics, no 'statistics' information in JSON data.")

    submission_content += "\n\n---\n\n"
    submission_content = submission_content.replace("None", "0")

    # Update existing match thread
    try:
        reddit_instance.submission(id=variables.MatchThreadVariables.live_match_reddit_submission_id).edit(submission_content)
        logger.info("Updated live match thread for match ID: " + str(variables.MatchThreadVariables.live_match_football_api_id))
    except Exception as e:
        logger.error(f"Failed to update Reddit submission: {str(e)}")

    # Create post-match thread if game is finished
    if status_short in ["FT", "AET", "PEN"]:
        try:
            round_info = game_info_json.get("league", {}).get("round", "").replace("Regular Season -", "Matchday")
            league_name = get_safe_name_str(game_info_json.get("league", {}).get("name", ""))

            variables.MatchThreadVariables.post_match_thread_title = (
                f"[Post-Match Discussion Thread] {home_team_name} "
                f"{home_goals}:{away_goals} {away_team_name} "
                f"({league_name}, {round_info})"
            )
            variables.MatchThreadVariables.post_match_thread_content = submission_content
            create_post_match_thread(reddit_instance, None)
        except Exception as e:
            logger.error(f"Failed to prepare post-match thread: {str(e)}")


def create_post_match_thread(reddit_instance, comment=None):
    subreddit = reddit_instance.subreddit(config.Reddit.SUBREDDIT_NAME)

    # Check if match thread already exists.
    existing_submissions = subreddit.new(limit=config.Reddit.SUBMISSION_CHECK_BATCH_SIZE)
    for existing_submission in existing_submissions:
        if variables.MatchThreadVariables.post_match_thread_title == existing_submission.title:
            if comment is not None:
                comment.reply(resources.CommentReplies.POST_MATCH_DISCUSSION_EXISTS + existing_submission.url + ".")
            return

    # Create post-match discussion thread
    submission = create_submission(reddit_instance, variables.MatchThreadVariables.post_match_thread_title, variables.MatchThreadVariables.post_match_thread_content)
    logger.info("Created post-match discussion thread: " + str(variables.MatchThreadVariables.post_match_thread_title))

    # Reply to comment if it exists.
    if comment is not None:
        comment.reply(resources.CommentReplies.POST_MATCH_DISCUSSION_CREATED + submission.url + ".")

    # Reset pre-match and live match thread flags and post-match title and content so that they're ready for next game.
    variables.MatchThreadVariables.pre_match_thread_created = False
    variables.MatchThreadVariables.live_match_thread_created = False
    variables.MatchThreadVariables.live_match_events_already_existed = False
    variables.MatchThreadVariables.live_match_football_api_id = None
    variables.MatchThreadVariables.live_match_reddit_submission_id = ""
    variables.MatchThreadVariables.post_match_thread_title = ""
    variables.MatchThreadVariables.post_match_thread_content = ""


if __name__ == "__main__":
    pass
