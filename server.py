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
from jinja2 import TemplateNotFound

import db

#########################################################
# App setup and authorization
#########################################################
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)

oauth.register(
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

# *********************************
# 1) Home page
# *********************************
@app.route('/')
def home():
  try:
    return render_template('home.html', session=session.get('user'), userDetails=json.dumps(session.get('user'), indent=4))
  except TemplateNotFound:
    abort(404)



# *********************************
# 2) Products page
# *********************************
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
      
  # Call database function to get skincare products
  products_list = db.filter_products(cleanser_filter, exfoliant_filter, toner_filter, serum_filter, moisturizer_filter, sunscreen_filter)

  # Render products page with skincare products
  # Template not found try/catch block reference: https://flask-diamond.readthedocs.io/en/stable/developer/writing_views_with_jinja_and_blueprints/
  try:
    return render_template('products.html', products_list=products_list, query_dict=checked_query_dict, session=session.get('user'))
  except TemplateNotFound:
    abort(404)


# *********************************
# 3) Routine page
# *********************************
@app.route('/routine', methods=["GET"])
def routine():

  # Check if user is logged in, if not tell user to sign up or login to view
  # ************************************************
  # * Only have routine features for logged in users
  # * Get the users details from session object
  # ************************************************
  user_details = session

  # Initialize user's routine products (for non-logged in users)
  is_user_logged_in = False
  if ('nickname' not in user_details):
    return render_template('routine.html', session=session.get('user'), is_user_logged_in=is_user_logged_in)

  else:
    is_user_logged_in = True
    username = user_details['nickname']

    # Call database function to get all of user's routine products for each category
    # NOTE: This method results in LONG LOAD TIMES.. Likely due to many SQL database queries :(
    # user_cleansers      = db.get_user_routine_by_type('cleanser', username)
    # user_exfoliants     = db.get_user_routine_by_type('exfoliant', username)
    # user_toners         = db.get_user_routine_by_type('toner', username)
    # user_serums         = db.get_user_routine_by_type('serum', username)
    # user_moisturizers   = db.get_user_routine_by_type('moisturizer', username)
    # user_suncreens      = db.get_user_routine_by_type('sunscreen', username)

    # Instead, try this, maybe it's faster?
    user_routine = db.get_user_routine(username)

    # Start with empty lists for product lists we want to return
    user_cleansers    = []
    user_exfoliants   = []
    user_toners       = []
    user_serums       = []
    user_moisturizers = []
    user_suncreens    = []
    # Loop through one SQL select's results and add to python lists
    for product in user_routine:

      # Product details stored as a dict in a length one list so remove the list part
      product_details = product[0]
      
      # If cleanser, add to cleanser list
      if (product_details['cleanser'] == True):
        user_cleansers.append(product)
      # If exfoliant, add to exfoliant list
      if (product_details['exfoliant'] == True):
        user_exfoliants.append(product)
      # If toner, add to toner list
      if (product_details['toner'] == True):
        user_toners.append(product)
      # If serum, add to serum list
      if (product_details['serum'] == True):
        user_serums.append(product)
      # If moisturizer, add to moisturizer list
      if (product_details['moisturizer'] == True):
        user_moisturizers.append(product)
      # If sunscreen, add to sunscreen list
      if (product_details['sunscreen'] == True):
        user_suncreens.append(product)


  # Render routine page with the skincare products on the current user's wishlist
  try:
    return render_template('routine.html', session=session.get('user'), is_user_logged_in=is_user_logged_in, user_cleansers=user_cleansers, user_exfoliants=user_exfoliants, user_toners=user_toners, user_serums=user_serums, user_moisturizers=user_moisturizers, user_suncreens=user_suncreens)
  except TemplateNotFound:
    abort(404)

# **********************************************************************************
# Add a product to routine after its respective 'add to routine' button is selected
# **********************************************************************************
@app.route('/add_to_routine', methods=["POST"])
def add_to_routine():

  # Add to users' routine/wishlist (NOTE: Arguments stored in request.json)
  if (('username' in request.json) and ('productName' in request.json)):
    db.add_to_routine(request.json)

  return request.json


# ******************************************************************************************
# Remove a product to routine after its respective 'remove from routine' button is selected
# ******************************************************************************************
@app.route('/remove_from_routine', methods=["POST"])
def remove_from_routine():
  
  # Add to users' routine/wishlist (NOTE: Arguments stored in request.json)
  if (('username' in request.json) and ('productName' in request.json)):
    db.remove_from_routine(request.json)

  return request.json


# *********************************
# 4) Account page
# *********************************
@app.route('/account', methods=["GET"])
def account():
  
  # Get users details from session object
  user_details = session
  
  # Ensure username exists
  # * Reference to check if a key exists within a python dict: https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
  if ('nickname' not in user_details):
    print('Error at "/account" route. No suitable username provided.')
    return
  
  username = user_details['nickname']  # Get username

  # Get user_ids from users table to add to the review table 
  user_id = db.get_user_id_from_username(username)

  # Get the users quiz selections 
  quiz_selections_list = db.get_user_quiz_selections(user_id)
  skin_type     = quiz_selections_list[0][0]
  skin_target   = quiz_selections_list[0][1]
  num_of_steps  = quiz_selections_list[0][2]
  
  # Render account page
  try:
    return render_template('account.html', session=session.get('user'), userDetails=json.dumps(session.get('user'), indent=4),user_target=skin_target, user_skin_type=skin_type, routine_steps=num_of_steps)
  except TemplateNotFound:
    abort(404)


# *********************************
# 5) Review Page
# *********************************
@app.route('/reviews', methods=["GET"])
def reviews():
  try:
    return render_template('reviews.html',session=session.get('user'))
  except TemplateNotFound:
    abort(404)
  

@app.route('/write-a-review', methods=["GET"])
def write_review():
  try:
    return render_template('add_review.html',session=session.get('user'))
  except TemplateNotFound:
    abort(404)



#########################################################
# Editing Quiz Selection Routes
#########################################################


# ***************************************************************************************************
# Edit user preferences route
# ***************************************************************************************************
@app.route('/edit_user_preferences', methods=['POST'])
def edit_user_preferences():

  # Ensure user is logged in (just in case)
  user_details = session
  if ('nickname' not in user_details):
    print('Error at "/edit_user_preferences": User not logged in.')
    return
  
  # Initialize values to pass into db function responsible for modifying user preferences
  preference_type     = None
  preference_value    = None

  # Identify which preference user wants to change
  # Valid Preferences: ['skin-type', 'target-type', 'number-steps']
  # 1) Preference to change is skin type
  if ('skin-type' in request.form):
    preference_type   = 'user_skin_type'
    preference_value  = request.form['skin-type']
  # 2) Preference to change is target type
  elif ('target-type' in request.form):
    preference_type   = 'user_target'
    preference_value  = request.form['target-type']
  # 3) Preference to change is number of routine steps
  elif ('number-steps' in request.form):
    preference_type   = 'routine_steps'
    preference_value  = request.form['number-steps']


  print("Preference type:", preference_type)
  print("Value:", preference_value)

  try:  # Attempt to run DB command
    db.edit_user_preferences(user_details, preference_type, preference_value)
  except:
    print('Error at: "/edit_user_preferences" route. DB function failed.')

  try:  # Redirect back to account page with new preferences
    return redirect('/account')
  except TemplateNotFound:
    abort(404)


#########################################################
# TEST routes
#########################################################

# *********************************
# Base page
# *********************************
@app.route('/base', methods=["GET"])
def base():
  return render_template('base.html')


# *********************************
# Child page (For testing)
# *********************************
@app.route('/child', methods=["GET"])
def child():
  return render_template('child.html')


# *********************************
# Test page (For testing)
# *********************************
@app.route('/api/get-user-routine-json', methods=["GET"])
def get_user_routine():

  # ************************************************
  # * Only have routine features for logged in users
  # * Get the users details from session object
  # ************************************************
  user_details = session
  if ('nickname' in user_details):
    # Get username
    username = user_details['nickname']

    # Call database function to get all of user's routine products that are
    # categorized as 'product_category'
    product_category = None
    user_products = db.get_user_routine_by_type(product_category, username)
    
  # Render routine page with the skincare products on their wishlist
  return user_products




#########################################################
# TEMPORARY ADMIN routes
#########################################################

# *********************************
# Admin form to add to database
# *********************************
@app.route('/admin/add-product-form', methods=["GET"])
def add_product_form():
  try:
    return render_template('add_product_form.html')
  except TemplateNotFound:
      abort(404)
  


# *********************************
# Add item to database
# *********************************
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

# Auth0Json page to see what auth0's json returns
@app.route('/auth0json', methods=["GET"])
def auth0Json():
  return render_template('Auth0Json.html', session=session.get('user'), userDetails=json.dumps(session.get('user'), indent=4))



#########################################################
# APIs
#########################################################

# *********************************
# Gets skincare products from database formatted as json
# *********************************
@app.route('/api/get-products-json', methods=["GET"])
def get_products_json():

  # Call database function to get skincare products
  db_products = db.get_skincare_products_json()
  
  # Return JSON format of skincare products
  return (db_products)


# *********************************
# Gets skineasy users from database
# *********************************
@app.route('/api/get-users-json', methods=["GET"])
def get_users_json():

  # Call database function to get skincare products
  db_users = db.get_users_json()
  
  # Return JSON format of skincare products
  return (db_users)


# *********************************
# Gets skineasy reviews from database
# *********************************
@app.route('/api/get-routines-json', methods=["GET"])
def get_routines_json():

  # Call database function to get skincare products
  db_users = db.get_routines_json()
  
  # Return JSON format of skincare products
  return (db_users)


# *********************************
# Gets users review from database 
# *********************************
@app.route('/api/get-reviews-json', methods=["GET"])
def get_reviews_json():

  # Call database function to get user reviews
  db_users = db.get_reviews_json()
  
  # Return JSON format of user reviews
  return (db_users)




#########################################################
# Authorization
#########################################################

# *********************************
# User login
# *********************************
@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


# *********************************
# User login authorization callback
# *********************************
@app.route("/api/auth/callback", methods=["GET", "POST"])
def callback():

    # Check if user denied authorization errors
    if (request.args.get('error')):
      print("Error, user denied authorization")
      return redirect("/")

    # Store auth0 access token in a variable 'token'
    token = oauth.auth0.authorize_access_token()
    print(token)

    # *******************************************************************************************************************************************************
    # * Fill sessions dictionary
    # * Ensure keys exist before putting in session dict
    # *
    # * Reference to check if a key exists within a python dict: https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
    # *******************************************************************************************************************************************************
    # User login details stored in auth0 token
    if (token):
      session["user"] = token

    # Ensure we have dictionary w/ user information
    if ('userinfo' in token):

      # Username (use nickname from token)
      if ('nickname' in token['userinfo']):
        session['nickname'] = token['userinfo']['nickname']
      # Session ID
      if ('sid' in token['userinfo']):
        session['sid'] = token['userinfo']['sid']
      # Email
      if ('email' in token['userinfo']):
        session['email'] = token['userinfo']['email']
      # Picture
      if ('picture' in token['userinfo']):
        session['picture'] = token['userinfo']['picture']
        
      # Fill users table by calling db function
      db.add_user(session)

    # Redirect back to whatever page we were on before
    return redirect("/")


# *********************************
# User logout
# *********************************
@app.route("/logout")
def logout():
    # Clear out session when user logging out
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


# *********************************
# Run on port 5000 if run locally
# *********************************
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=env.get("PORT", 5000))