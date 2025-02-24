import os
from typing import Final

from dotenv import load_dotenv

load_dotenv()


class FootballRapidApi:
    # IDs for leagues and cups change need to be changed every season - next time for season 2025/26.
    FOOTBALL_RAPID_API_INTER_CLUB_ID: Final[int] = 505  # This ID doesn't change.
    FOOTBALL_RAPID_API_SERIE_A_ID: Final[int] = 6374
    FOOTBALL_RAPID_API_CHAMPIONS_LEAGUE_ID: Final[int] = 6281
    FOOTBALL_RAPID_API_EUROPA_LEAGUE_ID: Final[int] = 6283
    FOOTBALL_RAPID_API_CONFERENCE_LEAGUE_ID: Final[int] = 6282
    FOOTBALL_RAPID_API_COPPA_ITALIA_ID: Final[int] = 6421
    FOOTBALL_RAPID_API_SUPERCOPPA_ID: Final[int] = 6825
    FOOTBALL_RAPID_API_CLUB_WORLD_CUP_ID: Final[int] = 6922

    FOOTBALL_RAPID_API_HEADERS: Final[dict[str, str]] = {
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
        "x-rapidapi-key": os.environ.get("RAPID_API_KEY")
    }

    FOOTBALL_RAPID_API_BASE_ENDPOINT: Final[str] = "https://api-football-v1.p.rapidapi.com"
    FOOTBALL_RAPID_API_TEAM_FIXTURES_ENDPOINT: Final[str] = FOOTBALL_RAPID_API_BASE_ENDPOINT + "/v2/fixtures/team/"
    FOOTBALL_RAPID_API_LEAGUE_TABLE_ENDPOINT: Final[str] = FOOTBALL_RAPID_API_BASE_ENDPOINT + "/v2/leagueTable/"
    FOOTBALL_RAPID_API_INJURIES_WITH_FIXTURE_ENDPOINT: Final[str] = FOOTBALL_RAPID_API_BASE_ENDPOINT + "/v3/injuries?fixture={}"
    FOOTBALL_RAPID_API_H2H_ENDPOINT: Final[str] = FOOTBALL_RAPID_API_BASE_ENDPOINT + "/v2/fixtures/h2h/"
    FOOTBALL_RAPID_API_FIXTURES_ENDPOINT: Final[str] = FOOTBALL_RAPID_API_BASE_ENDPOINT + "/v2/fixtures/id/"


class Reddit:
    # Reddit config.
    SUBREDDIT_NAME: Final[str] = os.environ.get("REDDIT_SUBREDDIT_NAME")
    BOT_REDDIT_USER: Final[str] = os.environ.get("REDDIT_USERNAME")
    APPROVED_USERS: Final[list[str]] = [user.strip() for user in os.environ.get("REDDIT_APPROVED_USER_LIST").split(",") if user.strip()]

    # Processing timings.
    MATCH_THREAD_CHECK_INTERVAL: Final[int] = 1800  # In seconds - every 30 minutes.
    MATCH_THREAD_UPDATE_INTERVAL: Final[int] = 120  # In seconds - every 2 minutes.
    SIDEBAR_UPDATE_INTERVAL: Final[int] = 14400  # In seconds - every 4 hours.
    SUBMISSION_CHECK_INTERVAL: Final[int] = 30  # In seconds.
    SUBMISSION_CHECK_BATCH_SIZE: Final[int] = 50  # Number of submissions to check in each batch.


if __name__ == "__main__":
    pass
