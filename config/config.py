from typing import Final


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

    FOOTBALL_RAPID_API_HEADERS: [dict[str, str]]  # This will be set in bot.py.

    FOOTBALL_RAPID_API_BASE_ENDPOINT: Final[str] = "https://api-football-v1.p.rapidapi.com"
    FOOTBALL_RAPID_API_TEAM_FIXTURES_ENDPOINT: Final[str] = FOOTBALL_RAPID_API_BASE_ENDPOINT + "/v2/fixtures/team/"
    FOOTBALL_RAPID_API_LEAGUE_TABLE_ENDPOINT: Final[str] = FOOTBALL_RAPID_API_BASE_ENDPOINT + "/v2/leagueTable/"
    FOOTBALL_RAPID_API_INJURIES_WITH_FIXTURE_ENDPOINT: Final[str] = FOOTBALL_RAPID_API_BASE_ENDPOINT + "/v3/injuries?fixture={}"
    FOOTBALL_RAPID_API_H2H_ENDPOINT: Final[str] = FOOTBALL_RAPID_API_BASE_ENDPOINT + "/v2/fixtures/h2h/"
    FOOTBALL_RAPID_API_FIXTURES_ENDPOINT: Final[str] = FOOTBALL_RAPID_API_BASE_ENDPOINT + "/v2/fixtures/id/"


class Reddit:
    # Reddit config.
    SUBREDDIT_NAME: Final[str] = "FCInterMilan"
    BOT_REDDIT_USER: Final[str] = "FCInterMilan"
    APPROVED_USERS: Final[list[str]] = ["cerozz", "mangowhymango", "dr_gonzo__", "phil_996", "roaming_dinosaur", "cheezravioli"]

    # Processing timings.
    MATCH_THREAD_CHECK_INTERVAL: Final[int] = 1800  # In seconds - every 30 minutes.
    MATCH_THREAD_UPDATE_INTERVAL: Final[int] = 120  # In seconds - every 2 minutes.
    SIDEBAR_UPDATE_INTERVAL: Final[int] = 14400  # In seconds - every 4 hours.
    SUBMISSION_CHECK_INTERVAL: Final[int] = 30  # In seconds.
    SUBMISSION_CHECK_BATCH_SIZE: Final[int] = 50  # Number of submissions to check in each batch.


if __name__ == "__main__":
    pass
