# imports
import os
import logging
from flask import Flask, request, send_file, jsonify, render_template
#from metadata import MetadataDict, Metadata
from flask_cors import CORS, cross_origin
import mysql.connector


# logger
logging.basicConfig(level=logging.DEBUG, format='%(process)d-%(levelname)s-%(message)s')


# database
"""
    host = "sql129.main-hosting.eu",
    user = "u291509283_cargill"
    password = "Cargill123",
    database = "u291509283_cargill"
"""
# host = "13.234.203.121",
# user = "covid_help",
# password = "covid_help",
# database = "covid_help"

HOSTNAME = "sql129.main-hosting.eu"
USERNAME = "u291509283_cargill"
PASSWORD = "Cargill123"
DATABASE = "u291509283_cargill"
TABLE = "Tweet_data"


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

    mydb = mysql.connector.connect(
        host = HOSTNAME,
        user = USERNAME,
        password = PASSWORD,
        database = DATABASE
    )

    # fetching distinct locations from table in database
    mycursor = mydb.cursor()
    mycursor.execute("select * from {} order by Tweet_location ASC,time DESC".format(TABLE))

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

    mydb = mysql.connector.connect(
        host = HOSTNAME,
        user = USERNAME,
        password = PASSWORD,
        database = DATABASE
    )

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

    mydb = mysql.connector.connect(
        host = HOSTNAME,
        user = USERNAME,
        password = PASSWORD,
        database = DATABASE
    )

    loc_name = request.args.get('location')
    #loc_name = "bangalore"

    # fetching distinct locations from table in database
    mycursor = mydb.cursor()
    mycursor.execute("select * from {} where Tweet_location like \"{}\" order by time DESC".format(TABLE, loc_name))
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


# main
if __name__ == '__main__':

    app.run(host = HOST, port = PORT)
