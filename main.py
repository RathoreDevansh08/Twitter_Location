# imports
import os
import pandas as pd
from flask import Flask, request, send_file, jsonify, render_template
from metadata import MetadataDict, Metadata
import mysql.connector


# database
mydb = mysql.connector.connect {
    host = "sql129.main-hosting.eu",
    user = "u291509283_cargill"
    password = "Cargill123",
    database = "u291509283_cargill"
}

mycursor = mydb.cursor()

TABLE = "Tweet_data"


# server
HOST = '127.0.0.1'
PORT = '5000'

app = Flask(__name__)


# services
@app.route('/', methods = [])
def data_request():

    mycursor.execute("SELECT * FROM {} WHERE location like {}".format(TABLE, city))
    myresult = mycursor.fetchall()

    # for x in myresult:
    #     print(x)

    return 


# main
if __name__ == '__main__':
    app.run(host = HOST, port = PORT)
