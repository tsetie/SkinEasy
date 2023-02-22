# app.py
# CSCI5117 Project 1
# yang7182 

#########################################################
# Imports
#########################################################
from flask import *

import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for

# from db import db functions...

#########################################################
# App setup and authorization
#########################################################
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get('FLASK_SECRET')

oauth = OAuth(app)
oauth.register (
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)


#########################################################
# Regular routes
#########################################################
# Home page
@app.route('/')
def home():
    return render_template('home.html')

# Products page
@app.route('/products', methods=["GET"])
def products():
  return render_template('products.html')

# Routine page
@app.route('/routine', methods=["GET"])
def routine():
  return render_template('routine.html')

# Review Page
@app.route('/reviews', methods=["GET"])
def reviews():
  return render_template('reviews.html')

# Quiz results
@app.route('/api/quiz', methods=["GET"])
def quizresults():
  return redirect('/products')

#########################################################
# APIs
#########################################################


#########################################################
# Authorization
#########################################################
@app.route("/signin")
def login():
    return render_template('signin.html')

#   return oauth.autho.authorize_redirect (
#     redirect_url=url_for("callback", external=True)
#   )