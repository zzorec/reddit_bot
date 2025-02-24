import time

import requests
from prawcore import RequestException, ServerError, Forbidden

from reddit_bot.config import config
from reddit_bot.data import variables, resources
from reddit_bot.util.date_util import format_date
from reddit_bot.util.format_util import add_league_table, add_knockout_stages
from reddit_bot.util.logging_util import logger


def sidebar_updater(reddit_instance) -> None:
    while True:
        try:
            logger.info("Updating subreddit sidebar.")
            update_sidebar(reddit_instance)
        except (RequestException, ServerError, Forbidden) as e:  # This error handling is needed because sometimes, Reddit API will error out and would stop the processing thread.
            logger.warning(f"{e} - Error communicating with Reddit when updating sidebar!")
        time.sleep(config.Reddit.SIDEBAR_UPDATE_INTERVAL)


def update_sidebar(reddit_instance) -> None:
    # Don't update if a match is live.
    if variables.MatchThreadVariables.live_match_thread_created:
        return

    subreddit = reddit_instance.subreddit(config.Reddit.SUBREDDIT_NAME)

    # Start building sidebar content with about section.
    sidebar_content = resources.Sidebar.ABOUT

    # Get last 3 fixtures
    url_last_fixtures = f"{config.FootballRapidApi.FOOTBALL_RAPID_API_TEAM_FIXTURES_ENDPOINT}{config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID}/last/3"
    response_last_fixtures = requests.get(url_last_fixtures, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS)
    logger.info("Football Rapid API: Fetched last 3 fixtures for sidebar.")
    if response_last_fixtures.status_code == 200:
        response_last_fixtures_json = response_last_fixtures.json()
        last_fixtures = response_last_fixtures_json.get("api", {}).get("fixtures", [])
        last_fixtures.reverse()
        sidebar_content += "\n### Fixtures\n\n"
        sidebar_content += "**Date**|**Opponent**|**Result**|**Comp**|\n"
        sidebar_content += ":-:|:-:|:-:|:-:|\n"
        for i in range(len(last_fixtures)):
            match_data = format_match(last_fixtures[i])
            if match_data["result"] == "P-P":
                sidebar_content += f"{match_data['date']}|{match_data['isAway']}{match_data['opponent']}|{match_data['result']}|{match_data['league']}\n"
            else:
                sidebar_content += f"{match_data['date']}|{match_data['isAway']}{match_data['opponent']}|{match_data['result']} {last_fixtures[i]['goalsHomeTeam']}-{last_fixtures[i]['goalsAwayTeam']}|{match_data['league']}\n"

        # Get next 3 fixtures
        url_next_fixtures = f"{config.FootballRapidApi.FOOTBALL_RAPID_API_TEAM_FIXTURES_ENDPOINT}{config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID}/next/3"
        response_next_fixtures = requests.get(url_next_fixtures, headers=config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS)
        logger.info("Football Rapid API: Fetched next 3 fixtures for sidebar.")
        if response_next_fixtures.status_code == 200:
            response_next_fixtures_json = response_next_fixtures.json()
            next_fixtures = response_next_fixtures_json.get("api", {}).get("fixtures", [])
            for i in range(len(next_fixtures)):
                match_data = format_match(next_fixtures[i])
                sidebar_content += f"{match_data['date']}|{match_data['isAway']}{match_data['opponent']}||{match_data['league']}\n"
        else:
            logger.warning("Failed to fetch next fixtures data from Rapid Football API for sidebar update.")
    else:
        logger.warning("Failed to fetch last fixtures data from Rapid Football API for sidebar update.")

    # Add Serie A table.
    sidebar_content = add_league_table(sidebar_content, config.FootballRapidApi.FOOTBALL_RAPID_API_SERIE_A_ID, "Serie A")

    # Add Champions League table and knockout stages
    sidebar_content = add_league_table(sidebar_content, config.FootballRapidApi.FOOTBALL_RAPID_API_CHAMPIONS_LEAGUE_ID, "Champions League")
    sidebar_content = add_knockout_stages(sidebar_content, config.FootballRapidApi.FOOTBALL_RAPID_API_CHAMPIONS_LEAGUE_ID, "Champions League")

    # Add Coppa Italia fixtures
    sidebar_content = add_knockout_stages(sidebar_content, config.FootballRapidApi.FOOTBALL_RAPID_API_COPPA_ITALIA_ID, "Coppa Italia")

    # Add Supercoppa Italiana fixtures
    if config.FootballRapidApi.FOOTBALL_RAPID_API_SUPERCOPPA_ID:
        sidebar_content = add_knockout_stages(sidebar_content, config.FootballRapidApi.FOOTBALL_RAPID_API_SUPERCOPPA_ID, "Supercoppa Italiana")

    # Add Club World Cup table and knockout stages
    sidebar_content = add_league_table(sidebar_content, config.FootballRapidApi.FOOTBALL_RAPID_API_CLUB_WORLD_CUP_ID, "Club World Cup")
    sidebar_content = add_knockout_stages(sidebar_content, config.FootballRapidApi.FOOTBALL_RAPID_API_CLUB_WORLD_CUP_ID, "Club World Cup")

    # Append other sections.
    sidebar_content += resources.Sidebar.FILTER
    sidebar_content += resources.Sidebar.LINKS
    sidebar_content += resources.Sidebar.COMMUNITIES
    sidebar_content += resources.Sidebar.WIKI
    sidebar_content += resources.Sidebar.PODCASTS
    sidebar_content += resources.Sidebar.SUBREDDITS

    # Submit sidebar changes.
    subreddit.mod.update(description=sidebar_content)
    logger.info("Updated subreddit sidebar.")


def format_match(match: dict) -> dict:
    response = {
        "isAway": "@" if match["homeTeam"]["team_id"] != config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID else "",
        "result": "",
        "date": format_date(match["event_date"], True, False),
        "opponent": match["awayTeam"]["team_name"] if match["homeTeam"]["team_id"] == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID else match["homeTeam"]["team_name"],
        "league": "Serie A" if match["league"]["name"] == "Serie A" else
        "CL" if match["league"]["name"] == "UEFA Champions League" else
        "EL" if match["league"]["name"] == "UEFA Europa League" else
        "ECL" if match["league"]["name"] == "UEFA Europa Conference League" else
        "CWC" if match["league"]["name"] == "FIFA Club World Cup" else
        "Friendly" if match["league"]["name"] == "Friendlies Clubs" else
        match["league"]["name"]
    }
    if match["status"] not in ["Match Finished", "Match Abandoned", "Match Postponed"]:
        return response
    elif match["status"] in ["Match Abandoned", "Match Postponed"]:
        response["result"] = "P-P"
    elif match["status"] == "Match Finished":
        if match["goalsHomeTeam"] == match["goalsAwayTeam"]:
            response["result"] = "D"
        elif match["homeTeam"]["team_id"] == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID and match["goalsHomeTeam"] > match["goalsAwayTeam"]:
            response["result"] = "W"
        elif match["awayTeam"]["team_id"] == config.FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID and match["goalsHomeTeam"] < match["goalsAwayTeam"]:
            response["result"] = "W"
        else:
            response["result"] = "L"
    return response


if __name__ == "__main__":
    pass
