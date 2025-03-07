### Running the bot

Bot can be executed by running Python file `bot.py`.

Following environment variables need to be set in order for the bot to work:

* `REDDIT_CLIENT_ID` - Reddit API client ID.
* `REDDIT_CLIENT_SECRET` - Reddit API client secret.
* `REDDIT_USERNAME` - Bot's Reddit username.
* `REDDIT_PASSWORD` - Bot's Reddit password.
* `REDDIT_SUBREDDIT_NAME` - Subreddit name, where the bot will run.
* `REDDIT_APPROVED_USER_LIST` - List of approved users on subreddit (comma delimited).
* `RAPIDAPI_API_KEY` - Rapid API key for API Football.

These can be set as operating system environment variables or in a `.env` file in the root directory of the project.

---

> **Reddit API**

Interaction with Reddit API is done with praw library: https://praw.readthedocs.io/

> **Football data**

All the football data comes from RapidAPI api-football: https://rapidapi.com/api-sports/api/api-football.

League and cup IDs are changed every season by Rapid API Football service and need to be updated in `config.py` for every season.

`bruno` folder contains a Bruno collection for manually testing and researching all the Rapid API requests that are made by the bot. 

> **How it runs**

When bot is started, it will spin up 5 threads:

* `process_comments_organizer` opens a native praw component stream that will automatically stream any new comments made on the subreddit and check whether any actions have to be performed inside method `process_comments`.
* `process_submissions_organizer` will fetch the latest batch of submissions every 30 (configurable) seconds and check whether any actions have to be performed inside method `process_submissions`. While a native praw streaming component exists, batch processing was implemented because follow-up
  actions after flair assignment weren't working correctly with streaming.
* `match_threads_creator` will check Football Rapid API every 30 (configurable) minutes to see when the next game is. If the game is less than a day away, it will create a pre-match thread. If it's less than an hour away, it will create a live match thread. Pre-match and Match thread creation and
  handling is done in methods `create_pre_match_thread`and `create_live_match_thread`.
* `match_threads_updater` will update the match thread submission every 180 (configurable) seconds when a match is live. This is only executed when variable `liveMatchThreadCreated` is True. Match thread updates are done with method `update_match_thread`. When match is finished,
  method `create_post_match_thread` will be automatically invoked.
* `sidebar_updater` will update the subreddit's sidebar configuration every 4 (configurable) hours. This is for old subreddit design, where sidebar contains information about upcoming games as well as league/cup tables.

> **How to avoid processing comments and submissions multiple times**

In order to avoid re-processing submissions and comments multiple times, they are being "saved" by the FCInterMilan bot user. Submissions and comments saved by the user are then filtered out in processing to avoid processing them multiple times.

> **Submission flairs**

Flairs are assigned to submissions based on flair ID in order for the correct styling to be applied. While it's possible, assigning flairs by text should be avoided, as it wouldn't apply correct design on new/mobile reddit layout. Flair ID can be found in Reddit mod settings, under Flair section.

---

### Hosting

Bot is running on a Google Cloud VM environment for 24/7 availability on Debian Linux. It's being run as a systemd service, so it can be started, stopped, and restarted with `systemctl` commands.
