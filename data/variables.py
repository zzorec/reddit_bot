# Global variables that are changed during runtime to bot behavior. Don't touch.

class MatchThreadVariables:
    # Blocks multiple pre-match thread creation. When a pre-match thread is created, it is set to True, blocking further creation. When post-match thread is posted, it is again set to false for the next game.
    pre_match_thread_created: bool = False

    # Blocks multiple live-match thread creation. When live-match thread is created, it is set to True, blocking further creation. When post-match thread is posted, it is again set to false for the next game.
    # When this flag is set to True, it will trigger match thread updates.
    live_match_thread_created: bool = False

    # Football Rapid API's ID of live match that is in progress. This will be set once the game starts and unset when the game is done.
    live_match_football_api_id: int = None

    # Reddit ID of live match thread that is in progress. This will be set once the match thread is created and unset when post-match discussion thread is created.
    live_match_reddit_submission_id: str = ""

    # Sometimes Football Rapid API will return JSON data without "events" sub-document.
    # Match thread update method contains retry logic. This flag enables / disables retry logic if match events already existed in previous API responses, but are no longer present in current API responses.
    # This flag is needed because otherwise it would unnecessarily retry the calls even when no match events have occurred yet.
    live_match_events_already_existed: bool = False

    # Title of post-match discussion thread. This will be set during live match thread and unset after post-match discussion thread is created.
    post_match_thread_title: str = ""

    # Contents of post-match discussion thread. This will be set during live match thread and unset after post-match discussion thread is created.
    post_match_thread_content: str = ""


class BotSettings:
    # If enabled, bot will automatically tag transfer market submissions with flair and add a news reliability tier comment.
    transfer_news_detection: bool = False


if __name__ == "__main__":
    pass
