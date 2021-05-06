import logging
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from functions import *

# logger
logging.basicConfig(level=logging.DEBUG, format='%(process)d-%(levelname)s-%(message)s')


# database
"""
    host = "sql129.main-hosting.eu",
    user = "u291509283_cargill"
    password = "Cargill123",
    database = "u291509283_cargill"
"""
# server
HOST = '0.0.0.0'
PORT = '5000'

app = Flask(__name__)
CORS(app)


# services - to return required food data dictionary
@app.route('/')
@cross_origin()
def data_request():

    logging.info("Received Request.")

    food = {}
    food["data"] = {}

    mydb = db_connection()

    # fetching distinct locations from table in database
    mycursor = mydb.cursor()
    mycursor.execute("select * from {} order by Tweet_location ASC,tweet_type asc ,verified desc, time DESC".format(TABLE))

    columns = mycursor.description
    locationColumnIndex = -1
    print(columns)
    for (index, column) in enumerate(columns):
        if column[0].lower()=="tweet_location".lower():
            locationColumnIndex = index
            break

    rows = mycursor.fetchall()

    locations = {}
    print(locationColumnIndex)
    for row in rows:
        tweet = {}
        for (index,value) in enumerate(row):
            tweet[str(columns[index][0])] = str(value)
        if row[locationColumnIndex] not in locations:
            locations[str(row[locationColumnIndex])] = {"tweets":[]}
        locations[str(row[locationColumnIndex])]["tweets"].append(tweet)

    food["data"] = locations
    # creating json object to return
    resp = jsonify(food)
    resp.status_code = 200

    mycursor.close()

    logging.info("Response Generated.")

    return resp


# services - ping check
@app.route('/health')
@cross_origin()
def ping_check():

    logging.info("Ping Check Request Received.")

    null_dict = {}

    # creating empty response with status code 200 to return for health check
    resp_chk = jsonify(null_dict)
    resp_chk.status_code = 200

    return resp_chk;


# services - disctinct tweet locations
@app.route('/tweet_locations')
@cross_origin()
def tweet_locations():

    logging.info("Distinct Tweet Locations Requested.")

    mydb = db_connection()

    # fetching distinct locations from table in database
    mycursor = mydb.cursor()
    mycursor.execute("select distinct Tweet_location from {} order by Tweet_location".format(TABLE))
    rows = mycursor.fetchall()

    locations = {}
    locations_list = []

    for row in rows:
        for (index, value) in enumerate(row):
            locations_list.append(str(value))

    locations["data"] = locations_list

    # creating json object to return
    resp = jsonify(locations)
    resp.status_code = 200

    mycursor.close()

    logging.info("Response Generated.")

    return resp


# services - tweet by locations
@app.route('/location_tweets', methods = ['GET'])
@cross_origin()
def location_tweets():

    logging.info("Tweet Locations Requested.")

    mydb = db_connection()

    loc_name = request.args.get('location')
    #loc_name = "bangalore"

    # fetching distinct locations from table in database
    mycursor = mydb.cursor()
    mycursor.execute("select * from {} where Tweet_location like \"{}\" order by tweet_type asc,verified desc, time DESC".format(TABLE, loc_name))
    rows = mycursor.fetchall()
    columns = mycursor.description

    col_list = []
    for (index, column) in enumerate(columns):
        col_list.append(str(column[0]))

    food_loc = {}
    loc_tweets = []
    for row in rows:
        twt = {}
        for (index, value) in enumerate(row):
            twt[col_list[index]] = str(value)
        loc_tweets.append(twt)

    food_loc["data"] = loc_tweets

    # creating json object to return
    resp = jsonify(food_loc)
    resp.status_code = 200

    mycursor.close()

    logging.info("Response Generated.")

    return resp

# services - tweet by locations
@app.route('/search', methods=['GET'])
@cross_origin()
def search():
    text = request.args.get('text')
    df = search_tweet_as_df(text)
    df = process_tweets(df)
    tweets_response = tweet_df_to_location_response(df)
    response = {"data": tweets_response}
    resp = jsonify(response)
    resp.status_code = 200
    logging.info("Response Generated.")
    return resp


@app.route('/fetch_latest_tweets', methods=['GET'])
@cross_origin()
def fetch_latest_tweets():
    password = request.args.get('password')
    if password != "justdoit":
        resp = jsonify({"Error": "Wrong Password"})
        resp.status_code = 200
        return resp

    search_terms = ['home cooked food corona', 'home made food corona', 'home made food delivery',
                    'home made food covid', 'home cooked food covid', 'home cooked food corona']
    mydb = db_connection()
    mycursor = mydb.cursor()
    mycursor.execute("delete from "+TABLE+" where tweet_type='twitter'")
    for text in search_terms:
        df = search_tweet_as_df(text)
        df = process_tweets(df)
        for i, row in df.iterrows():
            sql = "INSERT IGNORE INTO " + DATABASE + "." + TABLE + "(time,tweet_id,name,tweet,retweets,location,created,followers,is_user_verified,Urls,Tweet_location,tweet_type)"
            sql += " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            mycursor.execute(sql, tuple(row))
    mydb.commit()
    logging.info("Fetched Latest Tweets for: ", search_terms)
    resp = jsonify(search_terms)
    resp.status_code = 200
    return resp


# main
if __name__ == '__main__':

    app.run(host = HOST, port = PORT)
