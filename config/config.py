import os
from typing import Final

from dotenv import load_dotenv

from reddit_bot.util.date_util import get_active_season

load_dotenv()


class FootballRapidApi:
    FOOTBALL_RAPID_API_INTER_CLUB_ID: Final[int] = 505
    FOOTBALL_RAPID_API_SERIE_A_ID: Final[int] = 135
    FOOTBALL_RAPID_API_CHAMPIONS_LEAGUE_ID: Final[int] = 2
    FOOTBALL_RAPID_API_EUROPA_LEAGUE_ID: Final[int] = 3
    FOOTBALL_RAPID_API_CONFERENCE_LEAGUE_ID: Final[int] = 848
    FOOTBALL_RAPID_API_COPPA_ITALIA_ID: Final[int] = 137
    FOOTBALL_RAPID_API_SUPERCOPPA_ID: Final[int] = 547
    FOOTBALL_RAPID_API_CLUB_WORLD_CUP_ID: Final[int] = 15

    FOOTBALL_RAPID_API_HEADERS: Final[dict[str, str]] = {
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
        "x-rapidapi-key": os.environ.get("RAPID_API_KEY")
    }

    FOOTBALL_RAPID_API_BASE_ENDPOINT: Final[str] = "https://api-football-v1.p.rapidapi.com"
    FOOTBALL_RAPID_API_V3_FIXTURES_ENDPOINT: Final[str] = FOOTBALL_RAPID_API_BASE_ENDPOINT + "/v3/fixtures?league={}&season={}&team={}"
    FOOTBALL_RAPID_API_V3_NEXT_TEAM_FIXTURES_ENDPOINT: Final[str] = FOOTBALL_RAPID_API_BASE_ENDPOINT + "/v3/fixtures?team={}&next={}"
    FOOTBALL_RAPID_API_V3_LAST_TEAM_FIXTURES_ENDPOINT: Final[str] = FOOTBALL_RAPID_API_BASE_ENDPOINT + "/v3/fixtures?team={}&last={}"
    FOOTBALL_RAPID_API_V3_INJURIES_ENDPOINT: Final[str] = FOOTBALL_RAPID_API_BASE_ENDPOINT + "/v3/injuries?fixture={}"
    FOOTBALL_RAPID_API_V3_LEAGUE_TABLE_ENDPOINT: Final[str] = FOOTBALL_RAPID_API_BASE_ENDPOINT + "/v3/standings?league={}&season={}"
    FOOTBALL_RAPID_API_V3_H2H_ENDPOINT: Final[str] = FOOTBALL_RAPID_API_BASE_ENDPOINT + "/v3/fixtures/headtohead?h2h={}-{}"
    FOOTBALL_RAPID_API_V3_FIXTURE_BY_ID_ENDPOINT: Final[str] = FOOTBALL_RAPID_API_BASE_ENDPOINT + "/v3/fixtures?id={}"

    @staticmethod
    def get_fixtures_by_league_id_url(league_id: int) -> str:
        return FootballRapidApi.FOOTBALL_RAPID_API_V3_FIXTURES_ENDPOINT.format(league_id, get_active_season(), FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID)

    @staticmethod
    def get_next_team_fixtures_url(next_matches: int) -> str:
        return FootballRapidApi.FOOTBALL_RAPID_API_V3_NEXT_TEAM_FIXTURES_ENDPOINT.format(FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID, next_matches)

    @staticmethod
    def get_last_team_fixtures_url(last_matches: int) -> str:
        return FootballRapidApi.FOOTBALL_RAPID_API_V3_LAST_TEAM_FIXTURES_ENDPOINT.format(FootballRapidApi.FOOTBALL_RAPID_API_INTER_CLUB_ID, last_matches)

    @staticmethod
    def get_injuries_by_fixture_id_url(fixture_id: int) -> str:
        return FootballRapidApi.FOOTBALL_RAPID_API_V3_INJURIES_ENDPOINT.format(fixture_id)

    @staticmethod
    def get_table_by_league_id_url(league_id: int) -> str:
        return FootballRapidApi.FOOTBALL_RAPID_API_V3_LEAGUE_TABLE_ENDPOINT.format(league_id, get_active_season())

    @staticmethod
    def get_h2h_by_team_id_url(home_team: int, away_team: int) -> str:
        return FootballRapidApi.FOOTBALL_RAPID_API_V3_H2H_ENDPOINT.format(home_team, away_team)

    @staticmethod
    def get_fixture_by_id_url(fixture_id: int) -> str:
        return FootballRapidApi.FOOTBALL_RAPID_API_V3_FIXTURE_BY_ID_ENDPOINT.format(fixture_id)


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
