import requests

from reddit_bot.config import config
from reddit_bot.util.date_util import format_date
from reddit_bot.util.logging_util import logger


def extract_cup_fixture(fixture: dict) -> dict:
    response = {
        "isAway": "@" if fixture["teams"]["home"]["id"] != config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID else "",
        "opponent": fixture["teams"]["away"]["name"] if fixture["teams"]["home"]["id"] == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID else fixture["teams"]["home"]["name"],
        "date": fixture["fixture"]["date"],
        "goalsHomeTeam": fixture["goals"]["home"],
        "goalsAwayTeam": fixture["goals"]["away"],
        "round": "RO32" if fixture["league"]["round"] == "Round of 32" else "RO16" if fixture["league"]["round"] == "Round of 16" else "QF" if fixture["league"]["round"] == "Quarter-finals" else "SF" if fixture["league"]["round"] == "Semi-finals" else fixture["league"]["round"],
    }
    if fixture["fixture"]["status"]["short"] not in ["FT", "AET", "PEN", "ABD", "PST", "SUSP", "CANC"]:
        response["result"] = ""
        return response
    elif fixture["fixture"]["status"]["short"] in ["ABD", "PST", "SUSP"]:
        response["result"] = "P-P"
        response["goalsHomeTeam"] = ""
        response["goalsAwayTeam"] = ""
    elif fixture["fixture"]["status"]["short"] in ["FT", "AET", "PEN"]:
        if fixture["goals"]["home"] == fixture["goals"]["away"]:
            response["result"] = "D"
        elif fixture["teams"]["home"]["id"] == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID and fixture["goals"]["home"] > fixture["goals"]["away"]:
            response["result"] = "W"
        elif fixture["teams"]["away"]["id"] == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID and fixture["goals"]["home"] < fixture["goals"]["away"]:
            response["result"] = "W"
        else:
            response["result"] = "L"
    return response


def add_league_table(content: str, league_id: int, league_name: str) -> str:
    league_url = config.FootballRapidApi.get_table_by_league_id_url(league_id)
    response = requests.get(league_url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS)
    logger.info(f"Football Rapid API: Fetched league table for: {league_name}.")
    if response.status_code == 200:
        response_json = response.json()
        response_data = response_json.get("response", [])
        if response_data:
            standings = response_data[0].get("league", {}).get("standings", [])
            if standings:

                # Find club's specific group in group stages.
                cwc_inter_group_id = 0
                for group_index, group in enumerate(standings):
                    for team_data in group:
                        if team_data['team']['id'] == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID:
                            cwc_inter_group_id = group_index

                table = standings[cwc_inter_group_id]
                content += f"\n### {league_name}\n"
                content += "| # | Team | PL | GD | Pts |\n"
                content += "|:-:|:--|:-:|:-:|:-:|\n"
                for team in table:
                    team_info = f"| {team['rank']} | {team['team']['name']} | {team['all']['played']} | {team['goalsDiff']} | {team['points']} |\n"
                    if team["team"]["id"] == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID:
                        team_info = f"| **{team['rank']}** | **{team['team']['name']}** | **{team['all']['played']}** | **{team['goalsDiff']}** | **{team['points']}** |\n"
                    content += team_info
            else:
                logger.warning(f"No standings data available for {league_name}.")
        else:
            logger.warning(f"No response data available for {league_name}.")
    else:
        logger.warning(f"Failed to fetch {league_name} data from Rapid Football API.")
    return content


def add_knockout_stages(content: str, competition_id: int, competition_name: str) -> str:
    knockout_url = config.FootballRapidApi.get_fixtures_by_league_id_url(competition_id)
    response = requests.get(knockout_url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS)
    logger.info(f"Football Rapid API: Fetched {competition_name} KO fixtures.")
    if response.status_code == 200:
        fixtures = response.json().get("response", [])
        fixtures_info = [extract_cup_fixture(fixture) for fixture in fixtures]
        ko_fixtures = ""
        for fixture in fixtures_info:
            if "league stage" not in fixture["round"].lower() and "group stage" not in fixture["round"].lower():
                fixture_result = f"**{fixture['result']} {fixture['goalsHomeTeam']}-{fixture['goalsAwayTeam']}**" if fixture["result"] else ""
                ko_fixtures += f"{format_date(fixture['date'], True, False)}|{fixture['isAway']}{fixture['opponent']}|{fixture_result}|{fixture['round']}\n"
        if ko_fixtures:
            if competition_name != "Champions League":
                content += f"\n### {competition_name}\n\n"
            else:
                content += f"\n\n\n"
            content += "**Date**|**Opponent**|**Result**|**Round**|\n"
            content += ":-:|:-:|:-:|:-:|\n"
            content += ko_fixtures
    else:
        logger.warning(f"Failed to fetch {competition_name} data from Rapid Football API.")
    return content


if __name__ == "__main__":
    pass
