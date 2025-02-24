import os
import sys
import threading
from typing import Final

import praw
from dotenv import load_dotenv, find_dotenv

from reddit_bot.util import reddit_comment_util, reddit_submission_util, reddit_match_thread_util, reddit_sidebar_util
from reddit_bot.util.logging_util import logger


def run_inter_bot() -> None:
    logger.info("Starting Inter bot!")

    if find_dotenv():
        load_dotenv()  # Load environment variables from .env file if it exists.
        logger.info("Loaded environment variables from .env file.")
    else:
        logger.warning("No .env file found. Using Linux environment variables.")

    # Check environment variables.
    required_env_vars: Final[list[str]] = ["RAPID_API_KEY", "REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD", "REDDIT_USER_AGENT", "REDDIT_SUBREDDIT_NAME", "REDDIT_APPROVED_USER_LIST"]
    missing_env_vars = []

    for var in required_env_vars:
        value = os.environ.get(var) if os.environ.get(var) is not None else os.getenv(var)

        if value is None:
            missing_env_vars.append(var)
        else:
            if var in os.environ:
                logger.info(f"Using {var} from Linux environment variable.")
            else:
                logger.info(f"Using {var} from .env file.")

    if missing_env_vars:
        for env_var in missing_env_vars:
            logger.error(f"Environment variable {env_var} is not set!")
        sys.exit(1)  # Exit the program if any of the required environment variables are missing

    # Creates a Reddit instance.
    reddit_instance = praw.Reddit(
        client_id=os.environ.get("REDDIT_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
        user_agent=os.environ.get("REDDIT_USER_AGENT"),
        username=os.environ.get("REDDIT_USERNAME"),
        password=os.environ.get("REDDIT_PASSWORD")
    )

    # Create a thread with a comment stream. It will immediately pick up any new comment in the comment stream.
    t1 = threading.Thread(target=reddit_comment_util.process_comments_organizer, args=(reddit_instance,))
    t1.start()
    logger.info("Started thread 1 for process_comments_organizer.")

    # Create a thread with submission processing. Unlike with comments, this is not implemented with native streaming capability due to inability to implement removal flair feature. It works by fetching batches of latest posts.
    t2 = threading.Thread(target=reddit_submission_util.process_submissions_organizer, args=(reddit_instance,))
    t2.start()
    logger.info("Started thread 2 for process_submissions_organizer.")

    # Create a thread with upcoming match thread analyzer that will check for any upcoming games and create pre-match and match threads.
    t3 = threading.Thread(target=reddit_match_thread_util.match_threads_creator, args=(reddit_instance,))
    t3.start()
    logger.info("Started thread 3 for match_threads_creator.")

    # Create a thread for updating match threads when a match is live.
    t4 = threading.Thread(target=reddit_match_thread_util.match_threads_updater, args=(reddit_instance,))
    t4.start()
    logger.info("Started thread 4 for match_threads_updater.")

    # Create a thread for updating subreddit's sidebar.
    t5 = threading.Thread(target=reddit_sidebar_util.sidebar_updater, args=(reddit_instance,))
    t5.start()
    logger.info("Started thread 5 for sidebar_updater.")


def main() -> None:
    run_inter_bot()


if __name__ == "__main__":
    main()
