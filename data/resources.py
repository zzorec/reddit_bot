from typing import Final


class SubmissionFlairs:
    TRANSFER_MARKET: Final[str] = "9648c212-f10d-11ec-beb3-a222d0ba51ab"
    MATCH_THREAD: Final[str] = "bbbb0b52-7da6-11e7-904e-0ed4840b0fde"
    REMOVED_RULES: Final[str] = "f257600c-fca0-11eb-9563-c6d64032f350"


class Regex:
    TRANSFER_KEYWORDS: Final[
        str] = r"(romano|marzio|pedulla|james benge|ben jacobs|ornstein|plettenberg|barzaghi|bendoni|marchetti|calico mercato|matt law|sky|biasin|moretto|schira|togna|gazzetta|gds|repubblica|sportitalia|corriere|cds|giornale|messaggero|fcinternews|stampa|sport mediaset|tuttomercato|guarro|aouna|marca|mari)"
    TICKET_KEYWORDS: Final[str] = r"(tickets|ticket)"
    OTHER_SUBREDDIT_KEYWORDS: Final[str] = r"(r/acmilan|r/juve)"
    SWEAR_KEYWORDS: Final[str] = r"(retard)"
    SPAM_KEYWORDS: Final[str] = r"(crypto|airdrop|air drop|layerzero|l0|laroza)"


class CommentReplies:
    FORZA_INTER: Final[str] = "Sempre! ⚫🔵"
    SMOKE_STATUE: Final[str] = "🚬🤖"
    SWEAR_WORD: Final[
        str] = "🤖 Beep Boop...I detected some not so nice words in your comment. Keep in mind to be respectful and civil when discussing on the subreddit. Offensive behaviour may lead to temporary or even permanent bans.\n\n---\n\n^(I am a bot. If you would like to know more about me, you can visit our wiki article Inter Bot Commands) ^[HERE](https://www.reddit.com/r/FCInterMilan/wiki/bot-commands). ^(If you think there was a mistake, please contact us using Mod Mail. Thank you!)"
    OTHER_SUBREDDITS: Final[str] = "Remember that trolling/taunting other club's fans in their own subreddits will result in a permanent ban.\n\nKeep the banter here! ✌️🤖"
    AMALA: Final[str] = "🖤💙🖤💙🖤💙🖤\n\nAmala!\n\nPazza Inter amala!\n\nE' una gioia infinita\n\nche dura una vita\n\nPazza Inter amala!\n\n🖤💙🖤💙🖤💙🖤\n\n---\n\n^https://www.youtube.com/watch?v=EWV-aiDvoYo"
    COME_MAI: Final[str] = "🎹 🕺 🎹 🕺 🎹 🎵\n\nCo... Come mai!\n\nCo... Come mai!\n\nLa Champions League tu non la vinci mai!\n\n 🎹 🕺 🎹 🕺 🎹 🎵\n\n---\n\n^https://www.youtube.com/watch?v=FN7V5ez-fhc"
    INTER_BELLS: Final[str] = "❄️ ❄️ ❄️ ❄️ ❄️\n\n🔔 Inter bells! 🔔\n\n🔔 Inter bells! 🔔\n\n🔔 Inter all the way! 🔔\n\n❄️ ❄️ ❄️ ❄️ ❄️\n\n---\n\n^https://www.youtube.com/watch?v=mIC3Q1OwJ18"
    MARCO: Final[str] = "['Being an Inter fan is not stressful at all.'](https://i.redd.it/zg4hzcvhcn261.png)\n\n — Marco, 23 years old. 👴🫀🏥"
    MAROTTA: Final[str] = "Let him cook! 👩‍🍳"
    TI_AMO: Final[
        str] = "🎵 💸 🦓 💸 🦓 💸 🎵\n\nTi amo, ti amo campionato\n\nperché non sei falsato,\n\nanche se inizialmente era sembrato\n\nin realtà non sei falsato.\n\nL'ha detto Umberto Agnelli\n\nl'han detto tanti critici di calcio\n\nl'ha detto tanta gente, insomma: non sei falsato.\n\n🎵 💸 🦓 💸 🦓 💸 🎵\n\n---\n\n^https://www.youtube.com/watch?v=vuAjnaCdNzk"
    ABOUT: Final[str] = "🤖 Hey there! I am FCInterMilan's official subreddit bot. If you would like to know more about me, you can visit our wiki article Inter Bot Commands [HERE](https://www.reddit.com/r/FCInterMilan/wiki/bot-commands) or you can contact the mod team via Mod Mail. Thank you!"
    INJURIES_NOT_FOUND: Final[str] = "🤖 Beep Boop... Sorry. I couldn't find any missing players for next game."
    INSUFFICIENT_PERMISSIONS: Final[str] = "🤖 Beep Boop... Insufficient permissions, this command is reserved for Mod team only."
    SIDEBAR: Final[str] = "🤖 Beep Boop... Updating subreddit sidebar."
    TRANSFER_DETECTION_ENABLED: Final[str] = "Automatic transfer market submission detection is currently turned ON."
    TRANSFER_DETECTION_DISABLED: Final[str] = "Automatic transfer market submission detection is currently turned OFF."
    TRANSFER_DETECTION_TURNED_ON: Final[str] = "Transfer market submission detection status has been changed. It is now turned ON."
    TRANSFER_DETECTION_TURNED_OFF: Final[str] = "Transfer market submission detection status has been changed. It is now turned OFF."
    NO_RESPONSE: Final[
        str] = "🤖 Beep Boop... It seems like I don't have a response for that command yet. If you would like to see the list of available commands, you can visit our wiki article Inter Bot Commands [HERE](https://www.reddit.com/r/FCInterMilan/wiki/bot-commands) or you can contact the mod team via Mod Mail to submit a request for a new command. Thank you!"
    PRE_MATCH_DISCUSSION_EXISTS: Final[str] = "🤖 Beep Boop... Pre-match discussion thread already exists here: "
    PRE_MATCH_DISCUSSION_CREATED: Final[str] = "🤖 Beep Boop... Created pre-match discussion thread here: "
    MATCH_DISCUSSION_EXISTS: Final[str] = "🤖 Beep Boop... Match discussion thread already exists here: "
    MATCH_DISCUSSION_CREATED: Final[str] = "🤖 Beep Boop... Created match discussion thread here: "
    POST_MATCH_DISCUSSION_EXISTS: Final[str] = "🤖 Beep Boop... Created post-match discussion thread here: "
    POST_MATCH_DISCUSSION_CREATED: Final[str] = "🤖 Beep Boop... Post-match discussion thread already exists here: "
    CHAMPIONS_LEAGUE_NO_INFO_FOR_THIS_SEASON: Final[str] = "🤖 Beep Boop... No fixtures have been played in Champions League this season so far."
    CLUB_WORLD_CUP_NO_INFO_FOR_THIS_SEASON: Final[str] = "🤖 Beep Boop... No fixtures have been played in FIFA Club World Cup this season so far."
    COPPA_ITALIA_NO_INFO_FOR_THIS_SEASON: Final[str] = "🤖 Beep Boop... No fixtures have been played in Coppa Italia this season so far."


class SubmissionReplies:
    REMOVED_RULES: Final[
        str] = "🤖 Your post has been removed as it may have broken one of our [Community Rules](https://www.reddit.com/r/FCInterMilan/wiki/rules-and-moderation).\n\n---\n\n^(I am a bot. If you would like to know more about me, you can visit our wiki article Inter Bot Commands) ^[HERE](https://www.reddit.com/r/FCInterMilan/wiki/bot-commands). ^(If you think there was a mistake, please contact us using Mod Mail. Thank you!)"
    REMOVED_DUPLICATE: Final[
        str] = "🤖 Your post has been removed because it contains duplicate news or content.\n\n---\n\n^(I am a bot. If you would like to know more about me, you can visit our wiki article Inter Bot Commands) ^[HERE](https://www.reddit.com/r/FCInterMilan/wiki/bot-commands). ^(If you think there was a mistake, please contact us using Mod Mail. Thank you!)"
    REMOVED_WEEKLY_FREE_TALK_THREAD: Final[
        str] = "🤖 Your post has been removed because the content belongs to the weekly free talk thread. Feel free to submit your question or content there.\n\n---\n\n^(I am a bot. If you would like to know more about me, you can visit our wiki article Inter Bot Commands) ^[HERE](https://www.reddit.com/r/FCInterMilan/wiki/bot-commands). ^(If you think there was a mistake, please contact us using Mod Mail. Thank you!)"
    REMOVED_SOURCE: Final[
        str] = "🤖 Your post has been removed due to source-related issues. Some suggestions, as per our rules: try to use reliable sources, mentioned the source in post title, etc. You can refer to our wiki article Transfer News Reliability Tier List [HERE](https://www.reddit.com/r/FCInterMilan/wiki/transfer-news-reliability-guide).\n\n---\n\n^(I am a bot. If you would like to know more about me, you can visit our wiki article Inter Bot Commands) ^[HERE](https://www.reddit.com/r/FCInterMilan/wiki/bot-commands). ^(If you think there was a mistake, please contact us using Mod Mail. Thank you!)"
    REMOVED_MATCH_THREAD: Final[
        str] = "🤖 Your post has been removed. Please use our Match Thread posts instead.\n\n---\n\n^(I am a bot. If you would like to know more about me, you can visit our wiki article Inter Bot Commands) ^[HERE](https://www.reddit.com/r/FCInterMilan/wiki/bot-commands). ^(If you think there was a mistake, please contact us using Mod Mail. Thank you!)"
    REMOVED_LOW_EFFORT: Final[
        str] = "🤖 Your post has been detected as Low Effort and has been removed. Some suggestions, as per our rules: use descriptive titles, post quality content, avoid duplications, etc.\n\n---\n\n^(I am a bot. If you would like to know more about me, you can visit our wiki article Inter Bot Commands) ^[HERE](https://www.reddit.com/r/FCInterMilan/wiki/bot-commands). ^(If you think there was a mistake, please contact us using Mod Mail. Thank you!)"
    IDENTIFIED_TRANSFER_MARKET: Final[
        str] = "🤖 *This post has been identified as transfer market news. Make sure to check out our wiki article Transfer News Reliability Tier List [HERE](https://www.reddit.com/r/FCInterMilan/wiki/transfer-news-reliability-guide)*.\n\n---\n\n^(I am a bot. If you would like to know more about me, you can visit our wiki article Inter Bot Commands) ^[HERE](https://www.reddit.com/r/FCInterMilan/wiki/bot-commands). ^(If you think there was a mistake, please contact us using Mod Mail. Thank you!)"
    TWITTER: Final[
        str] = "🤖 Your post contains a direct link to X (formerly Twitter), which is not allowed. Please re-submit the content via an alternative source, or submit a screenshot/text post instead. Read more about the rule [HERE](https://www.reddit.com/r/FCInterMilan/comments/1ig0dkc/our_statement_on_future_moderation_of_x_twitter/).\n\n---\n\n^(I am a bot. If you would like to know more about me, you can visit our wiki article Inter Bot Commands) ^[HERE](https://www.reddit.com/r/FCInterMilan/wiki/bot-commands). ^(If you think there was a mistake, please contact us using Mod Mail. Thank you!)"
    DISCORD: Final[
        str] = "🤖 Your post has automatically been removed by the bot because it contains Discord keywords. If you are seeking an Inter Discord chanel, the link is available in the sidebar.\n\n---\n\n^(I am a bot. If you would like to know more about me, you can visit our wiki article Inter Bot Commands) ^[HERE](https://www.reddit.com/r/FCInterMilan/wiki/bot-commands). ^(If you think there was a mistake, please contact us using Mod Mail. Thank you!)"
    MOD_FLAIR_TRANSFER_MARKET: Final[
        str] = "🤖 *This post contains transfer market news. Make sure to check out our wiki article Transfer News Reliability Tier List [HERE](https://www.reddit.com/r/FCInterMilan/wiki/transfer-news-reliability-guide).*\n\n---\n\n^(I am a bot. If you would like to know more about me, you can visit our wiki article Inter Bot Commands) ^[HERE](https://www.reddit.com/r/FCInterMilan/wiki/bot-commands). ^(If you think there was a mistake, please contact us using Mod Mail. Thank you!)"
    TICKETS: Final[
        str] = "🤖 Your post has been automatically removed by the bot because it contains tickets keywords. If you need information about tickets, please use the Weekly Free Talk Thread or visit our wiki article Tickets and Matchday guide [HERE](https://www.reddit.com/r/FCInterMilan/wiki/tickets-and-matchday-guides).\n\n---\n\n^(I am a bot. If you would like to know more about me, you can visit our wiki article Inter Bot Commands) ^[HERE](https://www.reddit.com/r/FCInterMilan/wiki/bot-commands). ^(If you think there was a mistake, please contact us using Mod Mail. Thank you!)"
    SPAM: Final[
        str] = "🤖 Your post has been automatically removed by the bot because it contains spam keywords. If you need information about tickets, please use the Weekly Free Talk Thread or visit our wiki article Tickets and Matchday guide [HERE](https://www.reddit.com/r/FCInterMilan/wiki/tickets-and-matchday-guides).\n\n---\n\n^(I am a bot. If you would like to know more about me, you can visit our wiki article Inter Bot Commands) ^[HERE](https://www.reddit.com/r/FCInterMilan/wiki/bot-commands). ^(If you think there was a mistake, please contact us using Mod Mail. Thank you!)"


class Sidebar:
    ABOUT: Final[
        str] = "###F.C. Internazionale Milano ⭐⭐ \n\nF.C. Internazionale Milano (or Inter for short) is a football club based in Milano (Italy) and it is the only club that has played continuously in Serie A since its debut in 1909. Inter have won 46 total domestic and international trophies and with foundations set on racial and international tolerance and diversity, we truly are brothers and sisters of the world.\n\nWelcome to our community dedicated to news, discussion and support of our club. When discussing, please remember to be civil and avoid unwanted behaviour such as using racial slurs, offensive slang, homophobic taunts and other offensive behaviour. Respect your nerazzurri brothers and sisters! AMALA!"
    FILTER: Final[
        str] = "###Filter content by type\n\n[Transfer Market](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Transfer+Market%27&sort=new&restrict_sr=on)\n[Club News](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Club+news%27&sort=new&restrict_sr=on)\n[Team News](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Team+News%27&sort=new&restrict_sr=on)\n[Quote](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Interview+Quote%27&sort=new&restrict_sr=on)\n[Primavera](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Primavera%27&sort=new&restrict_sr=on)\n[Inter Women](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Women%27&sort=new&restrict_sr=on)\n[Loan/NT Watch](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Loan%2FNT+Watch%27&sort=new&restrict_sr=on)\n[Discussion](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Discussion%27&sort=new&restrict_sr=on)\n[Match Threads](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Match+Thread%27&sort=new&restrict_sr=on)\n[Highlights](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Highlights%27&sort=new&restrict_sr=on)\n[Analysis / Stats](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Analysis%2FStats%27&sort=new&restrict_sr=on)\n[Article](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Article%27&sort=new&restrict_sr=on)\n[Nostalgia](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Nostalgia%27&sort=new&restrict_sr=on)\n[Questions](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Question%27&sort=new&restrict_sr=on)\n[Other](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Other%27&sort=new&restrict_sr=on)\n[Amala](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Amala%27&sort=new&restrict_sr=on)\n[Banter](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Banter%27&sort=new&restrict_sr=on)\n[Poll](https://www.reddit.com/r/FCInterMilan/search?q=flair%3A%27Poll%27&sort=new&restrict_sr=on)\n\n"
    LINKS: Final[
        str] = "###Inter network\n\n######[Website](http://www.inter.it/en/hp)\n\n######[Twitter](https://twitter.com/Inter_en)\n\n######[Facebook](https://www.facebook.com/Inter/?ref=br_rs)\n\n######[Instagram](https://www.instagram.com/inter/)\n\n######[YouTube](https://www.youtube.com/user/INTER)\n\n######[Podcast](https://open.spotify.com/show/7l9XbUdnHuzXuTTAj1a4Q7?si=BiIVLaCAQ5-SO3k-OFz0yA)\n\n"
    COMMUNITIES: Final[
        str] = "###Inter communities\n\n######[Forza Inter Forums] (http://forzainterforums.com/forum.php)\n\n######[SempreInter](http://www.sempreinter.com/)\n\n######[Serpents of Madonnina] (http://www.serpentsofmadonnina.com/)\n\n######[FedeNerazzurra] (https://www.fedenerazzurra.net/)\n\n######[Discord](https://discordapp.com/invite/SfCJvqQ)\n\n"
    WIKI: Final[
        str] = "###Useful Wiki links\n\n######[News Reliability Guide](https://reddit.com/r/FCInterMilan/wiki/transfer-news-reliability-guide/)\n\n######[Rules / Moderation](https://reddit.com/r/FCInterMilan/wiki/rules-and-moderation/)\n\n######[Tickets / Matchday Guide](https://reddit.com/r/FCInterMilan/wiki/tickets-and-matchday-guides/)\n\n######[Inter Bot Commands](https://reddit.com/r/FCInterMilan/wiki/bot-commands/)\n\n"
    PODCASTS: Final[
        str] = "###Fan podcasts\n\n######[Inter Worldwide](https://soundcloud.com/inter-worldwide)\n\n######[SempreInter](https://www.youtube.com/user/SempreIntercom/videos)\n\n######[Solo Inter](https://www.youtube.com/channel/UCgKtRERg6OwhtWFMQevgG_g/videos)\n\n######[Brothers of the World](https://open.spotify.com/show/0kUhoGCFnU8nXW6yWCCZV4?si=pWuHvztsTVKtPat08VZUpw)\n\n######[Uncle Sharma](https://www.youtube.com/channel/UCOe5T5uFI-Kp9CNHGfqmnDQ)\n\n######[Passione Inter](https://youtube.com/@passioneinter)\n\n######[Inter Jections](https://open.spotify.com/show/5GfcrniMJ6OeNzfb0DFzdV)\n\n"
    SUBREDDITS: Final[str] = "###Other subreddits\n\n######[r/soccer](https://www.reddit.com/r/soccer/)\n\n######[r/football](https://reddit.com/r/football/)\n\n######[r/italy](https://www.reddit.com/r/italy/)\n\n######[r/milano](https://www.reddit.com/r/milano/)"


if __name__ == "__main__":
    pass
