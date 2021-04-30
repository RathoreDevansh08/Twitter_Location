# imports
import os
import logging
import pandas as pd
from flask import Flask, request, send_file, jsonify, render_template
from metadata import MetadataDict, Metadata
import mysql.connector


# database
"""
    host = "sql129.main-hosting.eu",
    user = "u291509283_cargill"
    password = "Cargill123",
    database = "u291509283_cargill"
"""

mydb = mysql.connector.connect(
    host = "localhost",
    user = "carg",
    password = "pwd",
    database = "sample_db"
)

mycursor = mydb.cursor()

DATABASE = "sample_db"
TABLE = "Tweet_data"

logging.info("Database Connection Established.")


# server
HOST = '127.0.0.1'
PORT = '5000'

app = Flask(__name__)


# services - to return required food data dictionary
@app.route('/')
def data_request():

    logging.info("Received Request.")

    food = {}
    food["data"] = {}

    # fetching distinct locations from table in database
    mycursor.execute("SELECT DISTINCT location FROM {}".format(TABLE))
    locations = mycursor.fetchall()

    # fetching field names from table in database
    mycursor.execute("select COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS where TABLE_SCHEMA = \"{}\" and TABLE_NAME = \"{}\"".format(DATABASE, TABLE))
    fields = mycursor.fetchall()

    # storing data location wise in disctionary format, iteratively
    for x in locations:

        # filtering data according to a particular location
        mycursor.execute("SELECT * FROM {} WHERE location like \"{}\"".format(TABLE, str(x[0])))
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

    logging.info("Response Generated.")
    return resp


# main
if __name__ == '__main__':
    app.run(host = HOST, port = PORT)
