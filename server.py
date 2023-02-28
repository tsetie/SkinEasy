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

import db

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

# Setup connection to database
@app.before_first_request
def setup():
    db.setup()


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
  
  # Check query string and store any checkmarks to keep in a list
  print(request.args)
  
  unchecked_query_dict = request.args
  # checked_query_dict = {}
  checked_query_dict = request.args

  # Get product type filters
  cleanser_filter     = False
  exfoliant_filter    = False
  toner_filter        = False
  serum_filter        = False
  moisturizer_filter  = False
  sunscreen_filter    = False

  # Ensure query parameters have valid values
  for query, value in unchecked_query_dict.items():
    if (query == 'cleanser'):
      cleanser_filter = True
    elif (query == 'exfoliant'):
      exfoliant_filter = True
    elif (query == 'toner'):
      toner_filter = True
    elif (query == 'serum'):
      serum_filter = True
    elif (query == 'moisturizer'):
      moisturizer_filter = True
    elif (query == 'sunscreen'):
      sunscreen_filter = True
      

  print(exfoliant_filter)

  # Call database function to get skincare products
  # products_list = db.get_skincare_products_json()
  products_list = db.filter_products(cleanser_filter, exfoliant_filter, toner_filter, serum_filter, moisturizer_filter, sunscreen_filter)
  
  # print(products_list)

  # Render products page with skincare products
  return render_template('products.html', products_list=products_list, query_dict=checked_query_dict)

# Routine page
@app.route('/routine', methods=["GET"])
def routine():
  return render_template('routine.html')

# Review Page
@app.route('/reviews', methods=["GET"])
def reviews():
  return render_template('reviews.html')


#########################################################
# TEST routes
#########################################################
# Base page
@app.route('/base', methods=["GET"])
def base():
  return render_template('base.html')

# Child page (For testing)
@app.route('/child', methods=["GET"])
def child():
  return render_template('child.html')

# Test page (For testing)
@app.route('/test', methods=["GET"])
def test():

  # Call database function to get skincare products
  db_products = db.get_skincare_products_json()
  
  # Render products page with skincare products
  return render_template('test.html', products_list=db_products)


#########################################################
# TEMPORARY ADMIN routes
#########################################################
# Admin form to add to database
@app.route('/admin/add-product-form', methods=["GET"])
def add_product_form():
  return render_template('add_product_form.html') 

# Add item to database
@app.route('/admin/add-product-to-db', methods=["POST"])
def add_product():

  # Look at request form details
  print(request.form)

  # Get product name, url, brand
  name              = request.form.get('product-name') or None
  url               = request.form.get('product-url') or None 
  brand             = request.form.get('product-brand') or None 

  image_path        = request.form.get('product-img-path') or None

  cleanser          = request.form.get('cleanser') or False
  exfoliant         = request.form.get('exfoliant') or False
  toner             = request.form.get('toner') or False
  serum             = request.form.get('serum') or False
  moisturizer       = request.form.get('moisturizer') or False
  sunscreen         = request.form.get('sunscreen') or False 

  sensitive_target  = request.form.get('sensitive') or False 
  mature_target     = request.form.get('mature') or False 
  no_target         = request.form.get('none') or False 

  normal_skin       = request.form.get('normal') or False 
  oily_skin         = request.form.get('oily') or False 
  dry_skin          = request.form.get('dry') or False
  is_all            = request.form.get('all') or False

  # Call database function to add a product to skincare product table
  if ((name is not None) and (url is not None) and (brand is not None) and (image_path is not None)):
    db.add_skincare_product(name, url, brand, image_path, cleanser, exfoliant, toner, serum, moisturizer, sunscreen, sensitive_target, mature_target, no_target, normal_skin, dry_skin, is_all)
  # Otherwise, report error & bad inputs
  else:
    print("Error: Failed to add to database.")

  return redirect('/admin/add-product-form')

#########################################################
# APIs
#########################################################
# Gets skincare products from database formatted as json
@app.route('/api/get-products-json', methods=["GET"])
def get_products_json():

  # Call database function to get skincare products
  db_products = db.get_skincare_products_json()
  
  # Return JSON format of skincare products
  return (db_products)



#########################################################
# Authorization
#########################################################
@app.route("/signin")
def login():
    return render_template('signin.html')

#   return oauth.autho.authorize_redirect (
#     redirect_url=url_for("callback", external=True)
#   )