import time
from datetime import timedelta, datetime

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
            return

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

        if remaining_until_next_game < timedelta(minutes=60) and not variables.MatchThreadVariables.live_match_thread_created:  # If less than an hour away from a match, create pre-match thread.
            logger.info(f"Creating a live-match discussion thread for: {match_teams}")
            try:
                create_live_match_thread(reddit_instance, None, next_match)
            except Exception:
                logger.exception("Error while scheduler tried to create a new pre-match discussion thread.")
        time.sleep(config.Reddit.MATCH_THREAD_CHECK_INTERVAL)  # Wait 30 minutes before checking again.


def create_pre_match_thread(reddit_instance, comment, next_match) -> None:
    variables.MatchThreadVariables.pre_match_thread_created = True
    subreddit = reddit_instance.subreddit(config.Reddit.SUBREDDIT_NAME)

    next_game_info_json = next_match or fetch_next_game()

    # Define title.
    submission_title = "[Pre-Match Discussion Thread] " + next_game_info_json["teams"]["home"]["name"] + " vs " + next_game_info_json["teams"]["away"]["name"] + " (" + next_game_info_json["league"]["name"] + ", " + next_game_info_json["league"]["round"].replace("Regular Season -", "Matchday") + ")"

    # Check if pre-match thread already exists.
    existing_submissions = subreddit.new(limit=50)
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
        submission_content += "^(This bot feature is still in beta, information could be inaccurate.)\n\n"
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
        submission_content += "^(H2H statistics may include only fixtures from recent years and may not represent overall historical data.)\n\n"

        home_team = next_game_info_json["teams"]["home"]["name"]
        away_team = next_game_info_json["teams"]["away"]["name"]
        total_played = len(h2h_data_fixtures)
        home_wins = sum(1 for match in h2h_data_fixtures if match["teams"]["home"]["id"] == next_game_info_json["teams"]["home"]["id"] and match["teams"]["home"]["winner"])
        away_wins = sum(1 for match in h2h_data_fixtures if match["teams"]["away"]["id"] == next_game_info_json["teams"]["away"]["id"] and match["teams"]["away"]["winner"])
        draws = total_played - (home_wins + away_wins)

        submission_content += f"| Total Played | {home_team} Win | Draw | {away_team} Win |\n"
        submission_content += "|:-:|:-:|:-:|:-:|\n"
        submission_content += f"| {total_played} | {home_wins} | {draws} | {away_wins} |\n"

        filtered_fixtures = [match for match in h2h_data_fixtures if match["fixture"]["status"]["short"] == "FT"]
        sorted_fixtures = sorted(filtered_fixtures, key=lambda match: match["fixture"]["timestamp"], reverse=True)

        if sorted_fixtures:
            submission_content += "### Latest Results\n\n"
            submission_content += "| Home | Score | Away | Date | Competition |\n"
            submission_content += "|:-:|:-:|:-:|:-:|:-:|\n"

        for index, match in enumerate(sorted_fixtures):
            if index > 8:
                break
            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            home_goals = match["goals"]["home"]
            away_goals = match["goals"]["away"]
            date = format_date(match["fixture"]["date"], True, True)
            competition = match["league"]["name"]

            if home_goals > away_goals:
                submission_content += f"| **{home}** | {home_goals}:{away_goals} | {away} | {date} | {competition} |\n"
            elif home_goals < away_goals:
                submission_content += f"| {home} | {home_goals}:{away_goals} | **{away}** | {date} | {competition} |\n"
            else:
                submission_content += f"| {home} | {home_goals}:{away_goals} | {away} | {date} | {competition} |\n"

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
    existing_submissions = subreddit.new(limit=50)
    for existing_submission in existing_submissions:
        if submission_title == existing_submission.title:
            if comment is not None:
                comment.reply(resources.CommentReplies.MATCH_DISCUSSION_EXISTS + existing_submission.url + ".")
            return

    # Prepare thread contents.
    submission_content = ""
    if next_game_info_json["fixture"]["status"]["long"] == "Match Finished":
        submission_content += f"# Full Time: {next_game_info_json['teams']['home']['name']} {next_game_info_json['goals']['home']}-{next_game_info_json['goals']['away']} {next_game_info_json['teams']['away']['name']}\n\n"
    elif next_game_info_json["fixture"]["status"]["long"] == "Halftime":
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
    # Get information about game
    url = config.FootballRapidApi.get_fixture_by_id_url(variables.MatchThreadVariables.live_match_football_api_id)
    logger.info("Football Rapid API: Fetched fixture details for updating match thread.")
    game_info_json = requests.get(url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS).json()["response"][0]

    # Sometimes fetching the data from API doesn't contain events data - retry logic added to try to handle that.
    retry_count = 0
    if game_info_json["fixture"]["status"]["elapsed"] > 0 and variables.MatchThreadVariables.live_match_events_already_existed:  # Only perform check if game has actually started and events exist.
        while not game_info_json.get("events"):
            logger.warning("Fetched game data for live match thread doesn't contain events, retrying...")
            time.sleep(10)
            game_info_json = requests.get(url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS).json()["response"][0]
            retry_count += 1
            if retry_count > 2:
                logger.warning("Reached max retries while trying to fetch events data for live match thread.")
                break

    # Generate match thread content.
    submission_content = "\n\n---\n\n"
    if game_info_json["fixture"]["status"]["long"] == "Match Finished":
        submission_content += f"# Full Time: {game_info_json['teams']['home']['name']} {game_info_json['goals']['home']}-{game_info_json['goals']['away']} {game_info_json['teams']['away']['name']}\n\n"
    elif game_info_json["fixture"]["status"]["long"] == "Halftime":
        submission_content += f"# Half Time: {game_info_json['teams']['home']['name']} {game_info_json['goals']['home']}-{game_info_json['goals']['away']} {game_info_json['teams']['away']['name']}\n\n"
    else:
        submission_content += f"# {game_info_json['fixture']['status']['elapsed']}′: {game_info_json['teams']['home']['name']} {game_info_json['goals']['home']}-{game_info_json['goals']['away']} {game_info_json['teams']['away']['name']}\n\n"
    goals_home = ""
    goals_away = ""
    if game_info_json.get("events"):
        variables.MatchThreadVariables.live_match_events_already_existed = True  # Set the flag to True to enable retry logic if events are not included in API response data.
        for event in game_info_json["events"]:
            if event.get("type") == "Goal" and event.get("detail") != "Missed Penalty":
                if event.get("team")["id"] == game_info_json["teams"]["home"]["id"]:
                    goals_home += f" {event['player']['name']} ({event['time']['elapsed']}′)"
                elif event.get("team")["id"] == game_info_json["teams"]["away"]["id"]:
                    goals_away += f" {event['player']['name']} ({event['time']['elapsed']}′)"
    else:
        logger.warning("Live match thread: couldn't extract team goals, no 'events' information in JSON data.")
    if goals_home:
        submission_content += f" **{game_info_json['teams']['home']['name']}:** {goals_home}.\n\n"
    if goals_away:
        submission_content += f" **{game_info_json['teams']['away']['name']}:** {goals_away}.\n\n"
    submission_content += "\n\n---\n\n"
    if game_info_json["fixture"].get("venue"):
        submission_content += f"**Venue:** {game_info_json['fixture']['venue']['name']}\n\n"
    if game_info_json["fixture"].get("referee"):
        submission_content += f"**Referee:** {game_info_json['fixture']['referee']}\n\n"
    try:
        if (game_info_json.get("lineups") and game_info_json["lineups"][0].get("team") and game_info_json["lineups"][0].get("startXI")
                and game_info_json["lineups"][0].get("substitutes") and game_info_json["lineups"][1].get("team") and game_info_json["lineups"][1].get("startXI")
                and game_info_json["lineups"][1].get("substitutes")):
            submission_content += "\n\n---\n\n"
            home_line_up = game_info_json["lineups"][0]
            away_line_up = game_info_json["lineups"][1]
            submission_content += "### Lineups\n\n"
            home_line_up["start"] = ", ".join(start["player"]["name"] for start in home_line_up["startXI"])
            home_line_up["subs"] = ", ".join(sub["player"]["name"] for sub in home_line_up["substitutes"])
            submission_content += f"#### {game_info_json['teams']['home']['name']}\n\n"
            submission_content += f" **Starting XI:** {home_line_up['start']}\n\n"
            submission_content += f" **Substitutes:** {home_line_up['subs']}\n\n"
            if home_line_up.get("coach"):
                submission_content += f" **Coach:** {home_line_up['coach']['name']}\n\n"
            away_line_up["start"] = ", ".join(start["player"]["name"] for start in away_line_up["startXI"])
            away_line_up["subs"] = ", ".join(sub["player"]["name"] for sub in away_line_up["substitutes"])
            submission_content += f"#### {game_info_json['teams']['away']['name']}\n\n"
            submission_content += f" **Starting XI:** {away_line_up['start']}\n\n"
            submission_content += f" **Substitutes:** {away_line_up['subs']}\n\n"
            if away_line_up.get("coach"):
                submission_content += f" **Coach:** {away_line_up['coach']['name']}\n\n"
        else:
            logger.warning("Live match thread: couldn't extract team lineups, no 'lineups' information in JSON data.")
    except KeyError:
        logger.error("Error while parsing team lineups in match updateMatchThread() method: ")

    events = game_info_json["events"]
    if events:
        submission_content += "\n\n---\n\n"
        submission_content += "### Match Events\n\n"
        submission_content += "| Min | Event |\n"
        submission_content += "|:-:|:--|\n"
        for event in events:
            if event["type"] == "Goal" and event["detail"] == "Missed Penalty":
                submission_content += f"| {event['time']['elapsed']}′ | ❌ **Missed Penalty ({event['team']['name']}):** {event['player']['name']}. |\n"
            elif event["type"] == "Goal" and event["team"]["id"] == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID:
                submission_content += f"| {event['time']['elapsed']}′ | ⚽ **GOAAAAAAAL (Inter): {event['player']['name']}{'' if not event['assist'] else ', assist by ' + event['assist']['name']}{'' if event['detail'] != 'Penalty' else ' (Penalty)'}. Forza Inter!** ⚫🔵 |\n"
            elif event["type"] == "Goal":
                submission_content += f"| {event['time']['elapsed']}′ | ⚽ **Goal ({event['team']['name']}): {event['player']['name']}{'' if not event['assist'] else ', assist by ' + event['assist']['name']}{'' if event['detail'] != 'Penalty' else ' (Penalty)'}.** |\n"
            elif event["type"] == "Card" and event["detail"] == "Yellow Card":
                submission_content += f"| {event['time']['elapsed']}′ | **🟨 Yellow card ({event['team']['name']}):** {event['player']['name']}. |\n"
            elif event["type"] == "Card" and event["detail"] == "Red Card":
                submission_content += f"| {event['time']['elapsed']}′ | **🟥 Red card ({event['team']['name']}):** {event['player']['name']}. |\n"
            elif event["type"] == "subst":
                submission_content += f"| {event['time']['elapsed']}′ | **🔄 Sub ({event['team']['name']}):** {event['player']['name']} replaces {event['assist']['name']}. |\n"
    else:
        logger.warning("Live match thread: couldn't extract game events, no 'events' information in JSON data.")

    if game_info_json.get("statistics"):
        submission_content += "\n\n---\n\n"
        submission_content += "### Match Stats\n\n"
        stats_home = game_info_json["statistics"][0]["statistics"]
        stats_away = game_info_json["statistics"][1]["statistics"]
        submission_content += f"| {game_info_json['teams']['home']['name']} |  | {game_info_json['teams']['away']['name']} |\n"
        submission_content += "|:-:|:-:|:-:|\n"
        for stat in stats_home:
            if stat["type"] == "Ball Possession":
                submission_content += f"| {stat['value']} | Ball Possession | {next(s['value'] for s in stats_away if s['type'] == 'Ball Possession')} |\n"
            elif stat["type"] == "Total Shots":
                submission_content += f"| {stat['value']} | Total Shots | {next(s['value'] for s in stats_away if s['type'] == 'Total Shots')} |\n"
            elif stat["type"] == "Shots on Goal":
                submission_content += f"| {stat['value']} | Shots On-Goal | {next(s['value'] for s in stats_away if s['type'] == 'Shots on Goal')} |\n"
            elif stat["type"] == "Shots off Goal":
                submission_content += f"| {stat['value']} | Shots Off-Goal | {next(s['value'] for s in stats_away if s['type'] == 'Shots off Goal')} |\n"
            elif stat["type"] == "Blocked Shots":
                submission_content += f"| {stat['value']} | Blocked Shots | {next(s['value'] for s in stats_away if s['type'] == 'Blocked Shots')} |\n"
            elif stat["type"] == "Shots insidebox":
                submission_content += f"| {stat['value']} | Shots Inside Box | {next(s['value'] for s in stats_away if s['type'] == 'Shots insidebox')} |\n"
            elif stat["type"] == "Shots outsidebox":
                submission_content += f"| {stat['value']} | Shots Outside Box | {next(s['value'] for s in stats_away if s['type'] == 'Shots outsidebox')} |\n"
            elif stat["type"] == "Fouls":
                submission_content += f"| {stat['value']} | Fouls | {next(s['value'] for s in stats_away if s['type'] == 'Fouls')} |\n"
            elif stat["type"] == "Corner Kicks":
                submission_content += f"| {stat['value']} | Corner Kicks | {next(s['value'] for s in stats_away if s['type'] == 'Corner Kicks')} |\n"
            elif stat["type"] == "Offsides":
                submission_content += f"| {stat['value']} | Offsides | {next(s['value'] for s in stats_away if s['type'] == 'Offsides')} |\n"
            elif stat["type"] == "Yellow Cards":
                submission_content += f"| {stat['value']} | Yellow Cards | {next(s['value'] for s in stats_away if s['type'] == 'Yellow Cards')} |\n"
            elif stat["type"] == "Red Cards":
                submission_content += f"| {stat['value']} | Red Cards | {next(s['value'] for s in stats_away if s['type'] == 'Red Cards')} |\n"
            elif stat["type"] == "Total passes":
                submission_content += f"| {stat['value']} | Total passes | {next(s['value'] for s in stats_away if s['type'] == 'Total passes')} |\n"
            elif stat["type"] == "Passes accurate":
                submission_content += f"| {stat['value']} | Accurate passes | {next(s['value'] for s in stats_away if s['type'] == 'Passes accurate')} |\n"
            elif stat["type"] == "Passes %":
                submission_content += f"| {stat['value']} | Passing accuracy | {next(s['value'] for s in stats_away if s['type'] == 'Passes %')} |\n"
    else:
        logger.warning("Live match thread: couldn't extract statistics, no 'statistics' information in JSON data.")
    submission_content += "\n\n---\n\n"
    submission_content = submission_content.replace("None", "0")

    # Update existing match thread.
    reddit_instance.submission(id=variables.MatchThreadVariables.live_match_reddit_submission_id).edit(submission_content)
    logger.info("Updated live match thread for match ID: " + str(variables.MatchThreadVariables.live_match_football_api_id))

    # When game is done, create the post-match discussion thread.
    if game_info_json["fixture"]["status"]["long"] == "Match Finished":
        # Set post-match discussion thread title and content
        variables.MatchThreadVariables.post_match_thread_title = "[Post-Match Discussion Thread] " + game_info_json["teams"]["home"]["name"] + " " + str(game_info_json["goals"]["home"]) + ":" + str(game_info_json["goals"]["away"]) + " " + game_info_json["teams"]["away"][
            "name"] + " (" + game_info_json["league"]["name"] + ", " + str(game_info_json["league"]["round"]).replace("Regular Season -", "Matchday") + ")"
        variables.MatchThreadVariables.post_match_thread_content = submission_content
        create_post_match_thread(reddit_instance, None)


def create_post_match_thread(reddit_instance, comment=None):
    subreddit = reddit_instance.subreddit(config.Reddit.SUBREDDIT_NAME)

    # Check if match thread already exists.
    existing_submissions = subreddit.new(limit=50)
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
