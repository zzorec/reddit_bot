import re
import time

from praw.exceptions import RedditAPIException
from prawcore import RequestException, ServerError, Forbidden, BadJSON

from reddit_bot.config import config
from reddit_bot.data import resources, variables
from reddit_bot.util.logging_util import logger
from reddit_bot.util.rapidapi_util import get_injuries_and_suspensions, get_next_match, get_serie_a_standings, getCoppaItaliaStandings, get_champions_league_standings, get_club_world_cup_standings
from reddit_bot.util.reddit_match_thread_util import create_pre_match_thread, create_live_match_thread, create_post_match_thread
from reddit_bot.util.reddit_sidebar_util import update_sidebar


def process_comments_organizer(reddit_instance) -> None:  # Open comments stream and check for new comments.
    subreddit = reddit_instance.subreddit(config.Reddit.SUBREDDIT_NAME)
    logger.info("Opening comments stream.")
    comment_stream = subreddit.stream.comments()
    try:
        for comment in comment_stream:
            try:
                _process_comments(reddit_instance, comment)
            except (RequestException, ServerError, Forbidden, RedditAPIException, BadJSON) as e:  # This error handling is needed because sometimes, Reddit API will error out and would stop the processing thread.
                logger.warning(f"{e} - Error communicating with Reddit when processing comments!")
    except (RequestException, ServerError, Forbidden, ValueError) as e:  # This error handling is needed because sometimes, Reddit API will error out and would stop the processing thread.
        logger.error(f"{e} - Error communicating with Reddit when handling comment stream!")
        time.sleep(60)
        process_comments_organizer(reddit_instance)  # Retry.


def _process_comments(reddit_instance, comment) -> None:
    # Ignore comments that has been saved (meaning already processed) or made by the bot itself.
    if comment.author == config.Reddit.BOT_REDDIT_USER or comment.saved:
        return

    # Convert values to lowercase for easier handling.
    comment_body = comment.body.lower()
    comment_author = str(comment.author).lower()

    logger.info("Processing comment by user: " + comment_author + ".")

    # Perform actions for various bot commands.

    if "forza inter" in comment_body:
        logger.info("Command forza inter triggered by: " + comment_author)
        comment.reply(resources.CommentReplies.FORZA_INTER)

    elif "🚬🗿" in comment_body:
        logger.info("Command 🚬🗿 triggered by: " + comment_author)
        comment.reply(resources.CommentReplies.SMOKE_STATUE)

    elif re.search(resources.Regex.SWEAR_KEYWORDS, comment_body, re.IGNORECASE):
        logger.info("Command for swear keywords triggered by: " + comment_author)
        comment.reply(resources.CommentReplies.SWEAR_WORD)

    elif re.search(resources.Regex.OTHER_SUBREDDIT_KEYWORDS, comment_body, re.IGNORECASE):
        logger.info("Command for other subreddits triggered by: " + comment_author)
        comment.reply(resources.CommentReplies.OTHER_SUBREDDITS)

    elif "!inter amala" in comment_body:
        logger.info("Command !inter amala triggered by: " + comment_author)
        comment.reply(resources.CommentReplies.AMALA)

    elif "!inter bells" in comment_body:
        logger.info("Command !inter bells triggered by: " + comment_author)
        comment.reply(resources.CommentReplies.INTER_BELLS)

    elif "!inter comemai" in comment_body or "!inter juve" in comment_body or "!inter juventus" in comment_body:
        logger.info("Command !inter cocomemai triggered by: " + comment_author)
        comment.reply(resources.CommentReplies.COME_MAI)

    elif "!inter marotta" in comment_body:
        logger.info("Command !inter marotta triggered by: " + comment_author)
        comment.reply(resources.CommentReplies.MAROTTA)

    elif "!inter marco" in comment_body:
        logger.info("Command !inter marco triggered by: " + comment_author)
        comment.reply(resources.CommentReplies.MARCO)

    elif "!inter tiamocampionato" in comment_body or "!inter campionato" in comment_body or "!inter tiamo" in comment_body:
        logger.info("Command !inter tiamocampionato triggered by: " + comment_author)
        comment.reply(resources.CommentReplies.TI_AMO)

    elif "!inter about" in comment_body:
        logger.info("Command !inter about triggered by: " + comment_author)
        comment.reply(resources.CommentReplies.ABOUT)

    elif "!inter injuries" in comment_body or "!inter suspensions" in comment_body:
        logger.info("Command !inter injuries/suspensions triggered by: " + comment_author)
        get_injuries_and_suspensions(comment)

    elif "!inter next" in comment_body:
        logger.info("Command !inter next triggered by: " + comment_author)
        get_next_match(comment)

    elif "!inter seriea" in comment_body:
        logger.info("Command !inter seriea triggered by: " + comment_author)
        get_serie_a_standings(comment)

    elif "!inter coppaitalia" in comment_body or "!inter coppa" in comment_body:
        logger.info("Command !inter coppaitalia triggered by: " + comment_author)
        getCoppaItaliaStandings(comment)

    elif "!inter clubworldcup" in comment_body or "!inter cwc" in comment_body:
        logger.info("Command !inter clubworldcup triggered by: " + comment_author)
        get_club_world_cup_standings(comment)

    elif "!inter championsleague" in comment_body or "!inter cl" in comment_body:
        logger.info("Command !inter championsleague triggered by: " + comment_author)
        get_champions_league_standings(comment)

    elif "!inter toggletransferdetection" in comment_body and comment_author in config.Reddit.APPROVED_USERS:
        logger.info("Command !inter toggletransferdetection triggered by: " + comment_author)
        if comment_author in config.Reddit.APPROVED_USERS:
            old_value = variables.BotSettings.transfer_news_detection
            if old_value is True:
                variables.BotSettings.transfer_news_detection = False
                comment.reply(resources.CommentReplies.TRANSFER_DETECTION_TURNED_OFF)
            else:
                variables.BotSettings.transfer_news_detection = True
                comment.reply(resources.CommentReplies.TRANSFER_DETECTION_TURNED_ON)
        else:
            comment.reply(resources.CommentReplies.INSUFFICIENT_PERMISSIONS)

    elif "!inter transferdetectionstatus" in comment_body and comment_author in config.Reddit.APPROVED_USERS:
        logger.info("Command !inter transferdetectionstatus triggered by: " + comment_author)
        if comment_author in config.Reddit.APPROVED_USERS:
            if variables.BotSettings.transfer_news_detection:
                comment.reply(resources.CommentReplies.TRANSFER_DETECTION_ENABLED)
            else:
                comment.reply(resources.CommentReplies.TRANSFER_DETECTION_DISABLED)
        else:
            comment.reply(resources.CommentReplies.INSUFFICIENT_PERMISSIONS)

    elif "!inter pre" in comment_body:
        logger.info("Command !inter pre triggered by: " + comment_author)
        if comment_author in config.Reddit.APPROVED_USERS:
            create_pre_match_thread(reddit_instance, comment, None)
        else:
            comment.reply(resources.CommentReplies.INSUFFICIENT_PERMISSIONS)

    elif "!inter live" in comment_body:
        logger.info("Command !inter live triggered by: " + comment_author)
        if comment_author in config.Reddit.APPROVED_USERS:
            create_live_match_thread(reddit_instance, comment, None)
        else:
            comment.reply(resources.CommentReplies.INSUFFICIENT_PERMISSIONS)

    elif "!inter post" in comment_body:
        logger.info("Command !inter post triggered by: " + comment_author)
        if comment_author in config.Reddit.APPROVED_USERS:
            create_post_match_thread(comment)
        else:
            comment.reply(resources.CommentReplies.INSUFFICIENT_PERMISSIONS)

    elif "!inter sidebar" in comment_body:
        logger.info("Command !inter sidebar triggered by: " + comment_author)
        if comment_author in config.Reddit.APPROVED_USERS:
            update_sidebar(reddit_instance)
            comment.reply(resources.CommentReplies.SIDEBAR)
        else:
            comment.reply(resources.CommentReplies.INSUFFICIENT_PERMISSIONS)

    elif "!inter" in comment_body:
        logger.info("Invalid command [" + comment_body + "] triggered by: " + comment_author)
        comment.reply(resources.CommentReplies.NO_RESPONSE)

    comment.save()  # Prevent future processing of the same comment.


if __name__ == "__main__":
    pass
