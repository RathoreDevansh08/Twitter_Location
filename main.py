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
        host = "sql129.main-hosting.eu",
        user = "u291509283_cargill",
        password = "Cargill123",
        database = "u291509283_cargill"
    )
    # fetching distinct locations from table in database
    mycursor = mydb.cursor()
    mycursor.execute("select * from {} order by Tweet_location,time".format(TABLE))

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

#services - ping check
@app.route('/health')
@cross_origin()
def ping_check():

    null_dict = {}

    # creating empty response with status code 200 to return for health check
    resp_chk = jsonify(null_dict)
    resp_chk.status_code = 200

    return resp_chk;


# main
if __name__ == '__main__':

    app.run(host = HOST, port = PORT)
