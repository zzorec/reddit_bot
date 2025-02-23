import logging
import os
import sys
import threading
from typing import Final

import praw
from dotenv import load_dotenv, find_dotenv

from reddit_bot.config import config
from reddit_bot.util import reddit_comment_util, reddit_submission_util, reddit_match_thread_util, reddit_sidebar_util
from reddit_bot.util.logging_util import logger


def run_inter_bot() -> None:
    logger.info("Starting Inter bot!")

    if find_dotenv():
        load_dotenv()  # Load environment variables from .env file if it exists.
        logging.info("Loaded environment variables from .env file.")
    else:
        logging.warning("No .env file found. Using Linux environment variables.")

    # Check environment variables.
    required_env_vars: Final[list[str]] = ["RAPID_API_KEY", "REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD", "REDDIT_USER_AGENT"]
    missing_env_vars = []

    for var in required_env_vars:
        value = os.environ.get(var) if os.environ.get(var) is not None else os.getenv(var)

        if value is None:
            missing_env_vars.append(var)
        else:
            if var in os.environ:
                logging.info(f"Using {var} from Linux environment variable.")
            else:
                logging.info(f"Using {var} from .env file.")

    if missing_env_vars:
        for env_var in missing_env_vars:
            logging.error(f"Environment variable {env_var} is not set!")
        sys.exit(1)  # Exit the program if any of the required environment variables are missing

    # Creates a Reddit instance.
    reddit_instance = praw.Reddit(
        client_id=os.environ.get("REDDIT_CLIENT_ID") or os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_CLIENT_SECRET") or os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.environ.get("REDDIT_USER_AGENT") or os.getenv("REDDIT_USER_AGENT"),
        username=os.environ.get("REDDIT_USERNAME") or os.getenv("REDDIT_USERNAME"),
        password=os.environ.get("REDDIT_PASSWORD") or os.getenv("REDDIT_PASSWORD")
    )

    # Sets Rapid API headers.
    config.FootballRapidApi.FOOTBALL_RAPID_API_HEADERS = {
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
        "x-rapidapi-key": os.environ.get("RAPID_API_KEY") or os.getenv("RAPID_API_KEY")
    }

    # Create a thread with a comment stream. It will immediately pick up any new comment in the comment stream.
    t1 = threading.Thread(target=reddit_comment_util.process_comments_organizer, args=(reddit_instance,))
    t1.start()
    logging.info("Started thread 1 for process_comments_organizer.")

    # Create a thread with submission processing. Unlike with comments, this is not implemented with native streaming capability due to inability to implement removal flair feature. It works by fetching batches of latest posts.
    t2 = threading.Thread(target=reddit_submission_util.process_submissions_organizer, args=(reddit_instance,))
    t2.start()
    logging.info("Started thread 2 for process_submissions_organizer.")

    # Create a thread with upcoming match thread analyzer that will check for any upcoming games and create pre-match and match threads.
    t3 = threading.Thread(target=reddit_match_thread_util.match_threads_creator, args=(reddit_instance,))
    t3.start()
    logging.info("Started thread 3 for match_threads_creator.")

    # Create a thread for updating match threads when a match is live.
    t4 = threading.Thread(target=reddit_match_thread_util.match_threads_updater, args=(reddit_instance,))
    t4.start()
    logging.info("Started thread 4 for match_threads_updater.")

    # Create a thread for updating subreddit's sidebar.
    t5 = threading.Thread(target=reddit_sidebar_util.sidebar_updater, args=(reddit_instance,))
    t5.start()
    logging.info("Started thread 5 for sidebar_updater.")


def main() -> None:
    run_inter_bot()


if __name__ == "__main__":
    main()
