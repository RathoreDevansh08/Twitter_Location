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
CORS(app, support_credentials=True)

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
    mycursor.execute("SELECT DISTINCT tweet_location FROM {}".format(TABLE))
    locations = mycursor.fetchall()

    # fetching field names from table in database
    mycursor.execute("select COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS where TABLE_SCHEMA = \"{}\" and TABLE_NAME = \"{}\"".format(DATABASE, TABLE))
    fields = mycursor.fetchall()

    # storing data location wise in disctionary format, iteratively
    for x in locations:

        # filtering data according to a particular location
        mycursor.execute("SELECT * FROM {} WHERE tweet_location like \"{}\"".format(TABLE, str(x[0])))
        loc_data = mycursor.fetchall()

        loc_name = str(x[0])
        loc_details = {}
        tweet_list = []

        for rw in loc_data:

            tweet_info = {}
            for i in range(len(fields)):
                tweet_info[str(fields[i][0])] = str(rw[i])

            tweet_list.append(tweet_info)

        # setting fields in output dictionary
        loc_details["tweets"] = tweet_list
        food["data"][loc_name] = loc_details

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
