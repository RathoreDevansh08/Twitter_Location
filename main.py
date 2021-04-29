# imports
import os
import pandas as pd
from flask import Flask, request, send_file, jsonify
from metadata import MetadataDict, Metadata


# server
HOST = '127.0.0.1'
PORT = '5000'

app = Flask(__name__)


# services
@app.route('/route', methods=[])
def request():


# main
if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
