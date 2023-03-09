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



# 1) Home page
@app.route('/')
def home():
    return render_template('home.html', session=session.get('user'), userDetails=json.dumps(session.get('user'), indent=4))



# 2) Products page
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
  return render_template('products.html', products_list=products_list, query_dict=checked_query_dict ,session=session.get('user'))



# 3) Routine page
@app.route('/routine', methods=["GET"])
def routine():
  return render_template('routine.html', session=session.get('user'))



# 4) Account page
@app.route('/yourAccount', methods=["GET"])
def yourAccount():
  # Get the users details from session object
  user_details = session
  # Get the users name
  # Reference to check if a key exists within a python dict: https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
  if ('nickname' in user_details):
      user = user_details['nickname']

      # Get user_ids from users table to add to the review table 
      usersID_and_names = db.get_all_user_ids_and_names()

      # Iterate list and find user_id corresponding to user's name
      for item in usersID_and_names:
          if item[1] == user:
              user_id = item[0]

  # Get the users quiz selections 
  quiz_selections_list = db.get_user_quiz_selections(user_id)
  skin_type = quiz_selections_list[0][0]
  skin_target = quiz_selections_list[0][1]
  num_of_steps = quiz_selections_list[0][2]
  return render_template('yourAccount.html', session=session.get('user'), userDetails=json.dumps(session.get('user'), indent=4),user_target=skin_target, user_skin_type=skin_type, routine_steps=num_of_steps)
  


# 5) Review Page
@app.route('/reviews', methods=["GET"])
def reviews():
  return render_template('reviews.html',session=session.get('user'))




#########################################################
# Editing Quiz Selection Routes
#########################################################
# Edit skin type route (comes here when edit skin type btn is clicked on "your account" page)
@app.route('/edit_skin_type', methods=['GET', 'POST'])
def editSkinType():
  # Get the modified skin type from the form 
  if request.method == 'POST':
    modified_skin_type = request.form["skin-type"]

    # Get the users details so we know which user to edit the skin type of in users table
    user_details = session

    # Edit users skin type in the users table
    db.edit_skin_type(user_details, modified_skin_type)

    # Get users details from session object
    user_details = session

    if ('nickname' in user_details):
            user = user_details['nickname']

            # Get user_ids from users table to add to the review table 
            usersID_and_names = db.get_all_user_ids_and_names()

            # Iterate list and find user_id corresponding to user's name
            for item in usersID_and_names:
                if item[1] == user:
                   user_id = item[0]

    # Get the users selections from the users table and store them into variables           
    user_selections_list = db.get_user_quiz_selections(user_id)
    skin_type = user_selections_list[0][0]
    skin_target = user_selections_list[0][1]
    num_of_steps = user_selections_list[0][2]
    return render_template('yourAccount.html', session=session.get('user'), userDetails=json.dumps(session.get('user'), indent=4),user_target=skin_target, user_skin_type=skin_type, routine_steps=num_of_steps)


# Edit skin target route (comes here when edit skin target btn is clicked on "your account" page)
@app.route('/edit_skin_target', methods=['GET', 'POST'])
def editSkinTarget():
  # Get the modified skin target from the form 
  if request.method == 'POST':
    modified_skin_target = request.form["target-type"]
    # Get the users details so we know which user to edit the skin target of in users table
    user_details = session
    # Edit users skin target in the users table
    db.edit_skin_target(user_details, modified_skin_target)
    # Get users details from session object
    user_details = session
    if ('nickname' in user_details):
            user = user_details['nickname']

            # Get user_ids from users table to add to the review table 
            usersID_and_names = db.get_all_user_ids_and_names()

            # Iterate list and find user_id corresponding to user's name
            for item in usersID_and_names:
                if item[1] == user:
                   user_id = item[0]
    # Get the users selections from the users table and store them into variables               
    user_selections_list = db.get_user_quiz_selections(user_id)
    skin_type = user_selections_list[0][0]
    skin_target = user_selections_list[0][1]
    num_of_steps = user_selections_list[0][2]
    return render_template('yourAccount.html', session=session.get('user'), userDetails=json.dumps(session.get('user'), indent=4),user_target=skin_target, user_skin_type=skin_type, routine_steps=num_of_steps)


# Edit number of steps in routine route (comes here when edit skin target btn is clicked on "your account" page)
@app.route('/edit_num_of_steps', methods=['GET', 'POST'])
def editNumOfSteps():
# If steps are from the form, edit user steps
  if request.method == 'PO  # Get the modified num oST':
    modified_num_of_steps = request.form["number-steps"]
    # Get the users details so we know which user to edit the skin target of in users table
    user_details = session
    # Edit users skin target in the users table
    db.edit_num_of_steps(user_details, modified_num_of_steps)
    # Get users details from session object
    user_details = session
    if ('nickname' in user_details):
            user = user_details['nickname']

            # Get user_ids from users table to add to the review table 
            usersID_and_names = db.get_all_user_ids_and_names()

            # Iterate list and find user_id corresponding to user's name
            for item in usersID_and_names:
                if item[1] == user:
                   user_id = item[0]
    # Get the users selections from the users table and store them into variables             
    user_selections_list = db.get_user_quiz_selections(user_id)
    skin_type = user_selections_list[0][0]
    skin_target = user_selections_list[0][1]
    num_of_steps = user_selections_list[0][2]
    return render_template('yourAccount.html', session=session.get('user'), userDetails=json.dumps(session.get('user'), indent=4),user_target=skin_target, user_skin_type=skin_type, routine_steps=num_of_steps)
  


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

  # Get user ID
  # Get product ID

  # Call database function to add routine to user
  db_products = db.get_skincare_products_json()
  
  # Render products page with skincare products
  return render_template('products.html')




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

# Auth0Json page to see what auth0's json returns
@app.route('/auth0json', methods=["GET"])
def auth0Json():
  return render_template('Auth0Json.html', session=session.get('user'), userDetails=json.dumps(session.get('user'), indent=4))



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



# Gets skineasy users from database
@app.route('/api/get-users-json', methods=["GET"])
def get_users_json():

  # Call database function to get skincare products
  db_users = db.get_users_json()
  
  # Return JSON format of skincare products
  return (db_users)



# Gets users review from database 
@app.route('/api/get-reviews-json', methods=["GET"])
def get_reviews_json():

  # Call database function to get user reviews
  db_users = db.get_reviews_json()
  
  # Return JSON format of user reviews
  return (db_users)




#########################################################
# Authorization
#########################################################
# @app.route("/signin")
# def login():
#     return render_template('signin.html')

#   return oauth.autho.authorize_redirect (
#     redirect_url=url_for("callback", external=True)
#   )

# User login
@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


# User login authorization callback
@app.route("/api/auth/callback", methods=["GET", "POST"])
def callback():

    # Check if user denied authorization errors
    if (request.args.get('error')):
      print("Error, user denied authorization")
      return redirect("/")

    # Store auth0 access token in a variable 'token'
    token = oauth.auth0.authorize_access_token()
    print(token)

    # * Fill sessions dictionary
    # * Ensure keys exist before putting in session dict
    # * Reference to check if a key exists within a python dict: https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
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


# User logout
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

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=env.get("PORT", 5000))