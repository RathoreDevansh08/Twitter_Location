import mysql.connector
import tweepy, json
import re
import pandas as pd

HOSTNAME = "sql129.main-hosting.eu"
USERNAME = "u291509283_cargill"
PASSWORD = "Cargill123"
DATABASE = "u291509283_cargill"
TABLE = "Tweet_data"

access_token = "2427460241-yihCbhCrkA6QrS7mhtwkK9FCnoKMvZzPNRFEtYr"
access_token_secret = "p6dTQRMwy0SxVP49oHLUXeJ1L4T2cDqPM4RNlcEPErJ9X"
consumer_key = "3nHkUhoqNif1x64w2gN7UxfPD"
consumer_secret = "SD0qR7yWtUdGDqYxPcUpyNsRcMsX5MJB9z4MxjVKyq6VYwvDp0"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def db_connection():
    global HOSTNAME, USERNAME, PASSWORD, DATABASE
    return mysql.connector.connect(
        host=HOSTNAME,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE
    )

def get_location_map():
    location_map = {}
    mydb = db_connection()
    mycursor = mydb.cursor()
    mycursor.execute("select location_name,location_alias from location_mapping order by location_name ASC")
    rows = mycursor.fetchall()
    for row in rows:
        location_map[row[0]] = row[1]
    mycursor.close()
    return location_map


location_map = get_location_map()


def update_location_map():
    global location_map
    location_map = get_location_map()


def search_tweet(text, limit):
    global api
    result = []
    search_str = text + " -filter:retweets"
    with no_ssl_verification():
        for tweet in tweepy.Cursor(api.search, q=search_str, lang="en", count=limit+1, result_type="recent",
                                   tweet_mode='extended').items(limit):
            tweet_details = {'time': str(tweet.created_at), 'tweet_id': tweet.id, 'name': tweet.user.screen_name,
                             'tweet': tweet.full_text, 'retweets': tweet.retweet_count, 'location': '',
                             'created': tweet.created_at.strftime("%d-%b-%Y"), 'followers': tweet.user.followers_count,
                             'is_user_verified': tweet.user.verified}
            result.append(tweet_details)
    return result


def search_tweet_as_df(text, limit):
    tweets = search_tweet(text, limit)
    return pd.json_normalize(tweets)


def process_tweets(df):
    df = df.where(pd.notnull(df), '')
    df["tweet"] = df.tweet.apply(lambda tweet: deEmojify(tweet))
    df["tweet_location"] = df.tweet.apply(lambda tweet: extractLocation(tweet))
    df["Urls"] = df.tweet.apply(lambda tweet: extractURLs(tweet))
    df["is_user_verified"] = df.is_user_verified.apply(lambda v: str(v))
    df["tweet_type"] = "twitter"
    # df["tweet"] = df.tweet.apply(lambda tweet: removeURLs(tweet))
    df = df.explode("tweet_location")
    # df = df.explode("Urls")
    df = df.where(pd.notnull(df), '')
    df = df.drop_duplicates()
    df = df[['time', 'tweet_id', 'name', 'tweet', 'retweets', 'location', 'created', 'followers', 'is_user_verified',
             'Urls', 'tweet_location', 'tweet_type']]
    return df


def tweet_df_to_location_response(df):
    tweets_response = {}
    for row_index, row in df.iterrows():
        tweet = dict(row.items())
        if tweet["tweet_location"] not in tweets_response:
            tweets_response[tweet["tweet_location"]] = {"tweets": []}
        tweets_response[tweet["tweet_location"]]["tweets"].append(tweet)
    return tweets_response


def deEmojify(text):
    regrex_pattern = re.compile(pattern="["
                                        u"\U0001F600-\U0001F64F"  # emoticons
                                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                        u"\u2710-\u2900"
    # u"\u2757"
                                        '\n' "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r' ', text)


def extractLocation(tweet):
    global location_map
    locations = set({})
    for (name, alias) in location_map.items():
        if name.lower() in tweet.lower():
            locations.add(alias)
    if len(locations) == 0:
        locations.add("Other")
    return list(locations)


def extractURLs(tweet):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet)
    return ",".join(urls)


def removeURLs(tweet):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet)
    for url in urls:
        tweet = tweet.replace(url, " ")
    return tweet


import warnings
import contextlib
import requests
from urllib3.exceptions import InsecureRequestWarning

old_merge_environment_settings = requests.Session.merge_environment_settings


@contextlib.contextmanager
def no_ssl_verification():
    opened_adapters = set()

    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        # Verification happens only once per connection so we need to close
        # all the opened adapters once we're done. Otherwise, the effects of
        # verify=False persist beyond the end of this context manager.
        opened_adapters.add(self.get_adapter(url))

        settings = old_merge_environment_settings(self, url, proxies, stream, verify, cert)
        settings['verify'] = False

        return settings

    requests.Session.merge_environment_settings = merge_environment_settings

    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', InsecureRequestWarning)
            yield
    finally:
        requests.Session.merge_environment_settings = old_merge_environment_settings

        for adapter in opened_adapters:
            try:
                adapter.close()
            except:
                pass
