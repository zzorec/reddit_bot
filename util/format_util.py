import requests

from reddit_bot.config import config
from reddit_bot.util.date_util import format_date
from reddit_bot.util.logging_util import logger


def extract_cup_fixture(fixture: dict) -> dict:
    response = {
        "isAway": "@" if fixture["homeTeam"]["team_id"] != config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID else "",
        "opponent": fixture["awayTeam"]["team_name"] if fixture["homeTeam"]["team_id"] == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID else fixture["homeTeam"]["team_name"],
        "date": fixture["event_date"],
        "goalsHomeTeam": fixture["goalsHomeTeam"],
        "goalsAwayTeam": fixture["goalsAwayTeam"],
        "round": "RO32" if fixture["round"] == "Round of 32" else "RO16" if fixture["round"] == "Round of 16" else "QF" if fixture["round"] == "Quarter-finals" else "SF" if fixture["round"] == "Semi-finals" else fixture["round"],
    }
    if fixture["status"] not in ["Match Finished", "Match Abandoned", "Match Postponed"]:
        response["result"] = ""
        return response
    elif fixture["status"] in ["Match Abandoned", "Match Postponed"]:
        response["result"] = "P-P"
        response["goalsHomeTeam"] = ""
        response["goalsAwayTeam"] = ""
    elif fixture["status"] == "Match Finished":
        if fixture["goalsHomeTeam"] == fixture["goalsAwayTeam"]:
            response["result"] = "D"
        elif fixture["homeTeam"]["team_id"] == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID and fixture["goalsHomeTeam"] > fixture["goalsAwayTeam"]:
            response["result"] = "W"
        elif fixture["awayTeam"]["team_id"] == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID and fixture["goalsHomeTeam"] < fixture["goalsAwayTeam"]:
            response["result"] = "W"
        else:
            response["result"] = "L"
    return response


def add_league_table(content: str, league_id: int, league_name: str) -> str:
    league_url = f"{config.FootballRapidApi.FOOTBALL_RAPID_API_LEAGUE_TABLE_ENDPOINT}{league_id}"
    response = requests.get(league_url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS)
    logger.info(f"Football Rapid API: Fetched league table for: {league_name}.")
    if response.status_code == 200:
        standings = response.json().get("api", {}).get("standings", [])
        if standings:
            table = standings[0]
            content += f"\n### {league_name}\n"
            content += "| # | Team | PL | GD | Pts |\n"
            content += "|:-:|:--|:-:|:-:|:-:|\n"
            for team in table:
                team_info = f"| {team['rank']} | {team['teamName']} | {team['all']['matchsPlayed']} | {team['goalsDiff']} | {team['points']} |\n"
                if team["team_id"] == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID:
                    team_info = f"| **{team['rank']}** | **{team['teamName']}** | **{team['all']['matchsPlayed']}** | **{team['goalsDiff']}** | **{team['points']}** |\n"
                content += team_info
        else:
            logger.warning(f"No standings data available for {league_name}.")
    else:
        logger.warning(f"Failed to fetch {league_name} data from Rapid Football API.")
    return content


def add_knockout_stages(content: str, competition_id: int, competition_name: str) -> str:
    knockout_url = f"{config.FootballRapidApi.FOOTBALL_RAPID_API_TEAM_FIXTURES_ENDPOINT}{config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID}/{competition_id}"
    response = requests.get(knockout_url, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS)
    logger.info(f"Football Rapid API: Fetched {competition_name} KO fixtures.")
    if response.status_code == 200:
        fixtures = response.json().get("api", {}).get("fixtures", [])
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
