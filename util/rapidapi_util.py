from json import JSONDecodeError

import requests

from reddit_bot.config import config
from reddit_bot.data import resources
from reddit_bot.util.date_util import format_time, format_date
from reddit_bot.util.format_util import extract_cup_fixture
from reddit_bot.util.logging_util import logger


def fetch_next_game():  # Fetches info about next game.
    request_url = config.FootballRapidApi.get_next_team_fixtures_url(1)
    logger.info(f"Football Rapid API: Fetched next game.")
    try:
        return requests.get(request_url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS).json()["response"][0]
    except (IndexError, KeyError, JSONDecodeError):
        logger.info("Fetch next games method hasn't returned any values as no games available.")
        return None


def get_club_world_cup_standings(comment) -> None:
    # Add Club World Cup table.
    cwc_url = config.FootballRapidApi.get_table_by_league_id_url(config.FootballRapidApi.FOOTBALL_RAPID_API_CLUB_WORLD_CUP_ID)
    logger.info(f"Football Rapid API: Fetched league table for: {config.FootballRapidApi.FOOTBALL_RAPID_API_CLUB_WORLD_CUP_ID} (comment command).")
    cwc_response = requests.get(cwc_url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS)
    comment_response = ""
    if cwc_response.status_code == 200:
        cwc_response_json = cwc_response.json()
        if cwc_response_json["response"]:

            # Find club's specific group in group stages.
            cwc_groups = cwc_response_json['response'][0]['league']['standings']
            cwc_inter_group_id = 0
            for group_index, group in enumerate(cwc_groups):
                for team_data in group:
                    if team_data['team']['id'] == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID:
                        cwc_inter_group_id = group_index

            table = cwc_response_json["response"][0]["league"]["standings"][cwc_inter_group_id]
            comment_response += "\n 🏆 **Club World Cup** 🏆\n\n"
            comment_response += "\n### Group stage\n"
            comment_response += "| # | Team | PL | GD | Pts |\n"
            comment_response += "|:-:|:--|:-:|:-:|:-:|\n"
            for team in table:
                if team["team"]["id"] == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID:
                    comment_response += f"| **{team['rank']}** | **{team['team']['name']}** | **{team['all']['played']}** | **{team['goalsDiff']}** | **{team['points']}** |\n"
                else:
                    comment_response += f"| {team['rank']} | {team['team']['name']} | {team['all']['played']} | {team['goalsDiff']} | {team['points']} |\n"
    else:
        logger.warning("Failed to fetch FIFA Club World Cup group stages data from Rapid Football API for comment reply.")

    # Add Club World Cup knockout stages.
    cwc_knockout_url = config.FootballRapidApi.get_fixtures_by_league_id_url(config.FootballRapidApi.FOOTBALL_RAPID_API_CLUB_WORLD_CUP_ID)
    logger.info("Football Rapid API: Fetched Club World Cup KO fixtures standings for comment command.")
    cwc_knockout_response = requests.get(cwc_knockout_url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS)

    if cwc_knockout_response.status_code == 200:
        cwc_knockout_response_json = cwc_knockout_response.json()
        if len(cwc_knockout_response_json.get("response", [])) > 3:
            comment_response += "\n### Knockout stages\n\n"
            comment_response += "**Date**|**Opponent**|**Result**|**Round**|\n"
            comment_response += ":-:|:-:|:-:|:-:|\n"
    else:
        cwc_knockout_response_json = {}
        logger.warning("Failed to fetch FIFA Club World Cup knockout stages data from Rapid Football API for comment reply.")

    fixtures = [fixture for fixture in cwc_knockout_response_json.get("response", [])]
    fixtures_info = [extract_cup_fixture(fixture) for fixture in fixtures]

    for fixture in fixtures_info:
        if "group stage" not in fixture["round"].lower():
            if fixture["result"] == "":
                fixture_result = ""
            else:
                fixture_result = f"**{fixture['result']} {fixture['goalsHomeTeam']}-{fixture['goalsAwayTeam']}**"
            comment_response += f"{format_date(fixture['date'], True, False)}|{fixture['isAway']}{fixture['opponent']}|{fixture_result}|{fixture['round']}\n"

    # Reply to comment.
    logger.info(f"Replied with FIFA Club World Cup standings information to comment: {str(comment.author).lower()}")
    if comment_response:
        comment.reply(comment_response)
    else:
        comment.reply(resources.CommentReplies.CLUB_WORLD_CUP_NO_INFO_FOR_THIS_SEASON)


def get_champions_league_standings(comment) -> None:
    # Add Champions League table.
    cl_url = config.FootballRapidApi.get_table_by_league_id_url(config.FootballRapidApi.FOOTBALL_RAPID_API_CHAMPIONS_LEAGUE_ID)
    logger.info(f"Football Rapid API: Fetched league table for: {config.FootballRapidApi.FOOTBALL_RAPID_API_CHAMPIONS_LEAGUE_ID} (comment command).")
    cl_response = requests.get(cl_url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS)
    comment_response = ""
    if cl_response.status_code == 200:
        cl_response_json = cl_response.json()
        if cl_response_json["response"]:
            table = cl_response_json["response"][0]["league"]["standings"][0]
            comment_response += "\n 🏆 **Champions League** 🏆\n\n"
            comment_response += "\n### Group stage\n"
            comment_response += "| # | Team | PL | GD | Pts |\n"
            comment_response += "|:-:|:--|:-:|:-:|:-:|\n"
            for team in table:
                if team["team"]["id"] == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID:
                    comment_response += f"| **{team['rank']}** | **{team['team']['name']}** | **{team['all']['played']}** | **{team['goalsDiff']}** | **{team['points']}** |\n"
                else:
                    comment_response += f"| {team['rank']} | {team['team']['name']} | {team['all']['played']} | {team['goalsDiff']} | {team['points']} |\n"
    else:
        logger.warning("Failed to fetch Champions League group stages data from Rapid Football API for comment reply.")

    # Add Champions League knockout stages.
    cl_knockout_url = config.FootballRapidApi.get_fixtures_by_league_id_url(config.FootballRapidApi.FOOTBALL_RAPID_API_CHAMPIONS_LEAGUE_ID)
    logger.info("Football Rapid API: Fetched CL KO fixtures standings for comment command.")
    cl_knockout_response = requests.get(cl_knockout_url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS)

    if cl_knockout_response.status_code == 200:
        cl_knockout_response_json = cl_knockout_response.json()
        if len(cl_knockout_response_json["response"]) > 8:
            comment_response += "\n### Knockout stages\n\n"
            comment_response += "**Date**|**Opponent**|**Result**|**Round**|\n"
            comment_response += ":-:|:-:|:-:|:-:|\n"
    else:
        cl_knockout_response_json = {}
        logger.warning("Failed to fetch Champions League knockout stages data from Rapid Football API for comment reply.")

    fixtures = [fixture for fixture in cl_knockout_response_json.get("response", [])]
    fixtures_info = [extract_cup_fixture(fixture) for fixture in fixtures]

    for fixture in fixtures_info:
        if "league stage" not in fixture["round"].lower():
            if fixture["result"] == "":
                fixture_result = ""
            else:
                fixture_result = f"**{fixture['result']} {fixture['goalsHomeTeam']}-{fixture['goalsAwayTeam']}**"
            comment_response += f"{format_date(fixture['date'], True, False)}|{fixture['isAway']}{fixture['opponent']}|{fixture_result}|{fixture['round']}\n"

    # Reply to comment.
    logger.info(f"Replied with Champions League standings information to comment: {str(comment.author).lower()}")
    if comment_response:
        comment.reply(comment_response)
    else:
        comment.reply(resources.CommentReplies.CHAMPIONS_LEAGUE_NO_INFO_FOR_THIS_SEASON)


def getCoppaItaliaStandings(comment) -> None:
    coppa_italia_url = config.FootballRapidApi.get_fixtures_by_league_id_url(config.FootballRapidApi.FOOTBALL_RAPID_API_COPPA_ITALIA_ID)
    logger.info("Football Rapid API: Fetched Coppa Italia standings for comment command.")
    coppa_italia_response = requests.get(coppa_italia_url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS)
    comment_response = ""
    if coppa_italia_response.status_code == 200:
        coppa_italia_response_json = coppa_italia_response.json()
        if coppa_italia_response_json["response"]:
            comment_response += "\n 🏆 **Coppa Italia** 🏆\n\n"
            comment_response += "**Date**|**Opponent**|**Result**|**Round**|\n"
            comment_response += ":-:|:-:|:-:|:-:|\n"
    else:
        coppa_italia_response_json = {}
        logger.warning("Failed to fetch Coppa Italia data from Rapid Football API for comment reply.")

    fixtures = coppa_italia_response_json.get("response", [])
    fixtures_info = [extract_cup_fixture(fixture) for fixture in fixtures]

    for fixture in fixtures_info:
        if fixture["result"] == "":
            fixture_result = ""
        else:
            fixture_result = f"**{fixture['result']} {fixture['goalsHomeTeam']}-{fixture['goalsAwayTeam']}**"
        comment_response += f"{format_date(fixture['date'], True, False)}|{fixture['isAway']}{fixture['opponent']}|{fixture_result}|{fixture['round']}\n"

    # Reply to comment.
    logger.info(f"Replied with Coppa Italia standings information to comment: {str(comment.author).lower()}")
    if comment_response:
        comment.reply(comment_response)
    else:
        comment.reply(resources.CommentReplies.COPPA_ITALIA_NO_INFO_FOR_THIS_SEASON)


def get_serie_a_standings(comment) -> None:
    # Get league information.
    request_url = config.FootballRapidApi.get_table_by_league_id_url(config.FootballRapidApi.FOOTBALL_RAPID_API_SERIE_A_ID)
    logger.info(f"Football Rapid API: Fetched league table for: {config.FootballRapidApi.FOOTBALL_RAPID_API_SERIE_A_ID} (comment command).")
    response_json = requests.get(request_url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS).json()

    table = response_json["response"][0]["league"]["standings"][0]

    # Build response comment - Reddit table.
    response = "\n 🏆 **Serie A** 🏆\n\n"
    response += "| # | Team | Games | W | D | L | +/- | GD | Points | Form |\n"
    response += "|:-:|:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|\n"

    for team in table:
        if team["team"]["id"] == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID:
            response += f"| **{team['rank']}** | **{team['team']['name']}** | **{team['all']['played']}** | **{team['all']['win']}** | **{team['all']['draw']}** | **{team['all']['lose']}** | **{team['all']['goals']['for']}:{team['all']['goals']['against']}** | **{team['goalsDiff']}** | **{team['points']}** | **{team['form']}** |\n"
        else:
            response += f"| {team['rank']} | {team['team']['name']} | {team['all']['played']} | {team['all']['win']} | {team['all']['draw']} | {team['all']['lose']} | {team['all']['goals']['for']}:{team['all']['goals']['against']} | {team['goalsDiff']} | {team['points']} | {team['form']} |\n"

    # Reply to comment.
    logger.info(f"Replied with Serie A standings information to comment: {str(comment.author).lower()}")
    comment.reply(response)


def get_injuries_and_suspensions(comment) -> None:
    # Get next match ID, find injuries for that match.
    injuries_request_url = config.FootballRapidApi.get_injuries_by_fixture_id_url(fetch_next_game()["fixture"]["id"])
    logger.info("Football Rapid API: Fetched injuries for comment command.")
    injuries_response_json = requests.get(injuries_request_url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS).json()
    # Response if no injuries are found.
    if not injuries_response_json["response"]:
        comment.reply(resources.CommentReplies.INJURIES_NOT_FOUND)
        return

    # Create reddit table for list of injuries.
    response = "List of players risking missing next game:\n\n"
    response += "| Player | Injury | Impact | Team |\n"
    response += "|:--|:-:|:-:|:-:|\n"

    # Populate injuries.
    for injury in injuries_response_json["response"]:
        response += "| {} | {} | {} | {} |\n".format(injury["player"]["name"], injury["player"]["reason"], injury["player"]["type"], injury["team"]["name"])

    # Post the response.
    logger.info(f"Replied with injuries/suspensions information to comment: {str(comment.author).lower()}")
    comment.reply(response)


def get_next_match(comment) -> None:
    # Get next match information.
    next_match = fetch_next_game()
    if not next_match:
        logger.info("No next match available.")
        return

    response = f"\n\n **{next_match['teams']['home']['name']}** vs **{next_match['teams']['away']['name']}**"

    # Get round information
    match_round = next_match['league'].get("round", None)
    if match_round:
        match_round = match_round.replace("Regular Season - ", "")

    # Build the response.
    if next_match['fixture'].get("date", None):
        response += f"\n\n **Date:** {format_date(next_match['fixture']['date'], False, True)}"
    if next_match['fixture'].get("date", None):
        response += f"\n\n **Time:** {format_time(next_match['fixture']['date'])} (GMT+1)"
    if next_match['fixture']['venue'].get("name", None):
        response += f"\n\n **Venue:** {next_match['fixture']['venue']['name']}"
    if next_match['league'].get("name", None):
        response += f"\n\n **Competition:** {next_match['league']['name']}"
    if match_round and next_match['league']['name'] == "Serie A":
        response += f"\n\n **Matchday:** {match_round}"
    if match_round and next_match['league']['name'] != "Serie A":
        response += f"\n\n **Round:** {match_round}"

    # Reply to comment.
    logger.info("Replied with next match information to comment: " + str(comment.author).lower())
    comment.reply(response)


if __name__ == "__main__":
    pass
