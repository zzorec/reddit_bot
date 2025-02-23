import re
import time

from praw.models import Submission
from prawcore import RequestException, ServerError, Forbidden

from reddit_bot.config import config
from reddit_bot.data import resources, variables
from reddit_bot.util.logging_util import logger


def create_submission(reddit_instance, submission_title, submission_content) -> Submission:
    subreddit = reddit_instance.subreddit(config.Reddit.SUBREDDIT_NAME)

    # Post the submission.
    submission = subreddit.submit(
        title=submission_title,
        selftext=submission_content,
        send_replies=False
    )

    # Set 'Match Thread' flair, sticky the submission, set default sorting to New.
    submission.flair.select(flair_template_id=resources.SubmissionFlairs.MATCH_THREAD)
    submission.mod.sticky(state=True, bottom=True)
    submission.mod.suggested_sort(sort="new")

    # Return submission so that it can be referenced in other methods later on.
    return submission


def process_submissions_organizer(reddit_instance) -> None:
    subreddit = reddit_instance.subreddit(config.Reddit.SUBREDDIT_NAME)
    while True:
        logger.debug("Fetching latest submissions and processing them.")
        try:
            submissions = subreddit.new(limit=config.Reddit.SUBMISSION_CHECK_BATCH_SIZE)
            for submission in submissions:
                _process_submissions(submission)
        except (RequestException, ServerError, Forbidden, ValueError) as e:  # This error handling is needed because sometimes, Reddit API will error out and would stop the processing thread.
            logger.warning(f"{e} - Error communicating with Reddit when processing submissions!")
        time.sleep(config.Reddit.SUBMISSION_CHECK_INTERVAL)


def _process_submissions(submission) -> None:
    # Ignore submissions that are posted by the bot.
    if submission.author and submission.author.name == config.Reddit.BOT_REDDIT_USER:
        return

    logger.debug("Processing submission: " + submission.title)  # Currently disabled, too much spam in the logs.

    # Get submission title and URL.
    title = submission.title.lower()
    text = submission.selftext.lower()
    url = submission.url.lower() if submission.url else None

    # Remove submissions and add explanatory comment if the submission was tagged with "Removed" flairs by moderators.
    if submission.link_flair_text == "Removed - Rules":
        comment = submission.reply(resources.SubmissionReplies.REMOVED_RULES)
        if comment and comment.id:
            comment.mod.distinguish(sticky=True)
        submission.mod.remove(spam=True)
        logger.info("Removed post due to rules: " + submission.title)

    if submission.link_flair_text == "Removed - Duplicate":
        comment = submission.reply(resources.SubmissionReplies.REMOVED_DUPLICATE)
        if comment and comment.id:
            comment.mod.distinguish(sticky=True)
        submission.mod.remove(spam=True)
        logger.info("Removed post due to duplication: " + submission.title)

    if submission.link_flair_text == "Removed - Weekly Free Talk Thread":
        comment = submission.reply(resources.SubmissionReplies.REMOVED_WEEKLY_FREE_TALK_THREAD)
        if comment and comment.id:
            comment.mod.distinguish(sticky=True)
        submission.mod.remove(spam=True)
        logger.info("Removed post due to weekly free talk thread content: " + submission.title)

    if submission.link_flair_text == "Removed - Source":
        comment = submission.reply(resources.SubmissionReplies.REMOVED_SOURCE)
        if comment and comment.id:
            comment.mod.distinguish(sticky=True)
        submission.mod.remove(spam=True)
        logger.info("Removed post due to source issues: " + submission.title)

    if submission.link_flair_text == "Removed - Match Thread":
        comment = submission.reply(resources.SubmissionReplies.REMOVED_MATCH_THREAD)
        if comment and comment.id:
            comment.mod.distinguish(sticky=True)
        submission.mod.remove(spam=True)
        logger.info("Removed post due to match thread content: " + submission.title)

    if submission.link_flair_text == "Removed - Low Effort":
        comment = submission.reply(resources.SubmissionReplies.REMOVED_LOW_EFFORT)
        if comment and comment.id:
            comment.mod.distinguish(sticky=True)
        submission.mod.remove(spam=True)
        logger.info("Removed post due to low effort: " + submission.title)

    # Post the transfer reliability tier list comment when a submission is tagged as 'Transfer Market' by moderators.

    if submission.link_flair_text == "Transfer Market" and not submission.saved:
        comment = submission.reply(resources.SubmissionReplies.MOD_FLAIR_TRANSFER_MARKET)
        if comment and comment.id:
            comment.mod.distinguish(sticky=True)
        submission.save()  # This is necessary to prevent multiple actions being performed by the bot on a single submission. Saved submissions are then filtered out in the future.
        logger.info("Added transfer reliability tier list to transfer market post: " + submission.title)

    # Flair or remove submissions if they match certain content.
    if url and not submission.link_flair_text:

        # Remove Discord promotions/questions.
        if (url and "discord.gg" in url) or (text and "discord.gg" in text) or "discord" in title:
            submission.mod.flair(flair_template_id=resources.SubmissionFlairs.REMOVED_RULES)
            comment = submission.reply(resources.SubmissionReplies.DISCORD)
            if comment and comment.id:
                comment.mod.distinguish(sticky=True)
            submission.mod.remove(spam=True)
            logger.info("Removed post due to Discord keywords: " + submission.title)

        # Remove Twitter/X posts.
        if url and "x.com" in url:
            submission.mod.flair(flair_template_id=resources.SubmissionFlairs.REMOVED_RULES)
            comment = submission.reply(resources.SubmissionReplies.TWITTER)
            if comment and comment.id:
                comment.mod.distinguish(sticky=True)
            submission.mod.remove(spam=True)
            logger.info("Removed post due to X/Twitter link: " + submission.title)

        # Tag transfer news with flair and add comment.
        if variables.BotSettings.transfer_news_detection and not submission.saved and ((url and re.search(resources.Regex.TRANSFER_KEYWORDS, url, re.IGNORECASE)) or re.search(resources.Regex.TRANSFER_KEYWORDS, title, re.IGNORECASE)):
            submission.mod.flair(flair_template_id=resources.SubmissionFlairs.TRANSFER_MARKET)
            comment = submission.reply(resources.SubmissionReplies.IDENTIFIED_TRANSFER_MARKET)
            if comment and comment.id:
                comment.mod.distinguish(sticky=True)
            submission.save()  # This is necessary to prevent multiple actions being performed by the bot on a single submission. Saved submissions are then filtered out in the future.
            logger.info("Added flair to post due to transfer market content: " + submission.title)

        # Remove ticket question threads.
        if re.search(resources.Regex.TICKET_KEYWORDS, title, re.IGNORECASE) or (text and re.search(resources.Regex.TICKET_KEYWORDS, text, re.IGNORECASE)):
            submission.mod.flair(flair_template_id=resources.SubmissionFlairs.REMOVED_RULES)
            comment = submission.reply(resources.SubmissionReplies.TICKETS)
            if comment and comment.id:
                comment.mod.distinguish(sticky=True)
            submission.mod.remove(spam=True)
            logger.info("Removed post due to tickets keywords: " + submission.title)

        # Remove spam threads.
        if (url and re.search(resources.Regex.SPAM_KEYWORDS, url, re.IGNORECASE)) or (text and re.search(resources.Regex.SPAM_KEYWORDS, text, re.IGNORECASE)) or re.search(resources.Regex.SPAM_KEYWORDS, title, re.IGNORECASE):
            submission.mod.flair(flair_template_id=resources.SubmissionFlairs.REMOVED_RULES)
            comment = submission.reply(resources.SubmissionReplies.SPAM)
            if comment and comment.id:
                comment.mod.distinguish(sticky=True)
            submission.mod.remove(spam=True)
            logger.info("Removed post due to spam keywords: " + submission.title)


if __name__ == "__main__":
    pass
