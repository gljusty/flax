import twint, re
from nltk.tokenize import sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer


# Uses NLTK's VADER to analyze tweet sentiment. Returns 4 scores: pos, neg, neutral, and compound.
# The compound score is used by TweetCard.vue to generate a small badge that is green if positive (between 0 and 1), red if negative (between 0 and -1) or grey if neutral (exactly 0).
# It is recommended to keep using the compound score, but all 4 scores are shipped in case the user wishes to use the other scores for some other purpose.

def AnalyzeTweetSentiment(tweets):
    sia = SentimentIntensityAnalyzer()
    for tweet in tweets:
        scores = sia.polarity_scores(str(sent_tokenize(RemoveURL(tweet.tweet))))
        tweet.__setattr__('scores', scores)     


# Instantiates a twint config object in prep for a search. Previous search results are manually cleared to avoid artifacts.
# Looks for 'username' and 'search_term' kwargs which are passed from the front end application via get request.
# Various config options are included below, required are tagged with required. See Twint documentation for more config options that can be added here.

def TwintConfig(**kwargs):
    c = twint.Config()
    twint.output.clean_lists()
    old = twint.output.tweets_list
    if (old):
        old.clear()
    if (kwargs['username']):
        c.Username = kwargs['username']
    if (kwargs['search_term']):
        c.Search = kwargs['search_term']
    c.Store_object = True                         #creates store data object; required.
    c.Hide_output = True                          #prevents spamming the terminal; required.
    c.Limit = 102                                 #recommended to stay at 102 for aesthetics or below 1000 for speed; required.
    #c.Profile_full = True                        #includes shadowbanned accounts & tweets. warning: slow; optional.
    return c


# Performs the search with a config object generated by TwintConfig that is passed in as the config_obj param.
# Including **kwargs for a reminder to myself for future dev purposes, currently useless -- input kwargs in the TwintConfig function instead.
# Utilizes several helper functions to clean tweet results before returning them to the front end application in json format.

def PerformSearch(config_obj, **kwargs):
    c = config_obj
    twint.run.Search(c)
    t = twint.output.tweets_list[:c.Limit]
    retry_counter = 0
    while (len(t) < c.Limit and retry_counter < 5):
        twint.run.Search(c)
        t = twint.output.tweets_list[:c.Limit]
        retry_counter += 1
        print(f"Application returning less than desired number of results; attempt {retry_counter} of 5") #for debug
        t = RemoveDuplicates(t)
    AnalyzeTweetSentiment(t)
    j = SerializeTweets(t)
    return j

# Helper function to remove duplicates from tweet results generated by PerformSearch. Takes in a list object as tweets param.
# Creates an empty set before looping through tweets and adding tweet ids that are not duplicates to the set. Returns a list object containing only non duplicates. 
# This solves the mysterious problem of occasional duplicate results and does so before they get to the front end app.

def RemoveDuplicates(tweets):
    seen = set()
    cleaned = []
    for tweet in tweets:
        if tweet.id not in seen:
            seen.add(tweet.id)
            cleaned.append(tweet)
    return cleaned

# Lazy work around for serialization issue with tweet data. Gets around Flask Jsonify bug.
# TODO: Revisit this as jsonify seems to be working now, not sure what changed.

def SerializeTweets(tweets):
    jt = []
    for tweet in tweets:
        jt.append(vars(tweet))
    return jt

# Honestly copied this off the internet somewhere. Tried fiddling with it, didn't go well. Just dont mess with it for now.
# TODO: Find alternative regex expressions and test. This one seems to cause AnaylzeTweetSentiment to return some false 0s. Still notably fewer false 0s than with no regex.

def RemoveURL(text):
    #dont change this nonsense
    return re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', " ", text)