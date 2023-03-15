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

from werkzeug.utils import secure_filename

import db
import io

#########################################################
# App setup and authorization
#########################################################
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # Reference to limit file size of user uploads: https://blog.filestack.com/thoughts-and-knowledge/secure-file-upload-flask-python/
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png']
# app.config['UPLOAD_PATH']

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

######################
# 1) Home page 
######################
@app.route('/')
def home():
  try:
    return render_template('home.html', session=session.get('user'), userDetails=json.dumps(session.get('user'), indent=4))
  except TemplateNotFound:
    abort(404)



#######################################
# 2) Products page & related functions
#######################################
@app.route('/products', methods=["GET"])
def products():
  
  # Get any queries from url
  query_dict = request.args
 
  # Get product type filters
  cleanser_filter     = False
  exfoliant_filter    = False
  toner_filter        = False
  serum_filter        = False
  moisturizer_filter  = False
  sunscreen_filter    = False

  # Keep track of number of skin typefilters checked/selected (If 0 then by default user selected all skin types)
  num_of_skintype_filters_selected = 0
  # Keep track of number of target filters checked/selected
  num_of_targets = 0

  # Get skin type filters
  show_all_filter = True
  normal_skin_filter = False
  dry_skin_filter = False
  oily_skin_filter = False

  # Get target area filters
  sensitive_target = False
  mature_target = False

  # By default price is set to price-all 
  price_filter = "price-all"

  # Ensure query parameters have valid values
  for query, value in query_dict.items():
    if (query == 'normal'):
      normal_skin_filter = True
      show_all_filter = False
      num_of_skintype_filters_selected +=1
    elif (query == 'dry'):
      dry_skin_filter = True
      show_all_filter = False
      num_of_skintype_filters_selected +=1
    elif (query == 'oily'):
      oily_skin_filter = True
      show_all_filter = False
      num_of_skintype_filters_selected +=1
    elif (query == 'sensitive-target'):
      sensitive_target = True
      num_of_targets +=1
    elif (query == 'mature-target'):
      mature_target = True
      num_of_targets +=1       
    elif (query == 'price'):
      price_filter = value

  # If user did not filter skin type, show all 
  if show_all_filter:
    normal_skin_filter  = True
    dry_skin_filter     = True
    oily_skin_filter    = True
    num_of_skintype_filters_selected +=4

  # Declare lists so if it doesnt have an item, it will still render to the html
  cleanser_list     = []
  exfoliant_list    = []
  toner_list        = []
  serum_list        = []
  moisturizer_list  = []
  sunscreen_list    = []

  # No filters selected / filter form not submmited SO we need to get ALL PRODUCTS
  # Goes here each time the products page is visited becasue the filter form is not submmited so its an empty list initially
  if (not query_dict):
    num_of_skintype_filters_selected = 4
    cleanser_list     = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets, sensitive_target, mature_target, price_filter, "cleanser")
    exfoliant_list    = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets, sensitive_target, mature_target, price_filter, "exfoliant")
    toner_list        = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets, sensitive_target, mature_target, price_filter, "toner")
    serum_list        = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets, sensitive_target, mature_target, price_filter, "serum")
    moisturizer_list  = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets, sensitive_target, mature_target, price_filter,"moisturizer")
    sunscreen_list    = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets, sensitive_target, mature_target, price_filter, "sunscreen")


  # Ensure query parameters have valid values
  for query, value in query_dict.items():
    if (query == 'cleanser'):
      cleanser_filter = True
      # Call database function to get skincare products with specified skin type and price filters
      cleanser_list = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets,sensitive_target, mature_target, price_filter, "cleanser")
    elif (query == 'exfoliant'):
      exfoliant_filter = True
      # Call database function to get skincare products with specified skin type and price filters
      exfoliant_list = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets,sensitive_target, mature_target, price_filter, "exfoliant")
    elif (query == 'toner'):
      toner_filter = True
      # Call database function to get skincare products with specified skin type and price filters
      toner_list = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets,sensitive_target, mature_target, price_filter, "toner")
    elif (query == 'serum'):
      serum_filter = True
      # Call database function to get skincare products with specified skin type and price filters
      serum_list = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets,sensitive_target, mature_target, price_filter, "serum")
    elif (query == 'moisturizer'):
      moisturizer_filter = True
      # Call database function to get skincare products with specified skin type and price filters
      moisturizer_list = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets,sensitive_target, mature_target, price_filter, "moisturizer")
    elif (query == 'sunscreen'):
      sunscreen_filter = True
      # Call database function to get skincare products with specified skin type and price filters
      sunscreen_list = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets,sensitive_target, mature_target, price_filter, "sunscreen")

  # No category or skintype selected, but filter form got submmited SO get ALL PRODUCTS with specified price
  # By default the price will be 'all' so dictionary will have "price : price all" which will be the only item in the dictinoary
  if (cleanser_filter == False and exfoliant_filter == False and toner_filter == False and serum_filter == False and moisturizer_filter == False and sunscreen_filter == False):
    cleanser_list     = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets,sensitive_target, mature_target, price_filter, "cleanser")
    exfoliant_list    = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets,sensitive_target, mature_target, price_filter, "exfoliant")
    toner_list        = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets,sensitive_target, mature_target, price_filter, "toner")
    serum_list        = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets,sensitive_target, mature_target, price_filter, "serum")
    moisturizer_list  = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets,sensitive_target, mature_target, price_filter,"moisturizer")
    sunscreen_list    = db.get_products(num_of_skintype_filters_selected, normal_skin_filter, dry_skin_filter, oily_skin_filter, show_all_filter,num_of_targets,sensitive_target, mature_target, price_filter, "sunscreen")


  # Render products page with skincare products
  try:
    return render_template('products.html', cleanser_list=cleanser_list, exfoliant_list=exfoliant_list, toner_list=toner_list, serum_list=serum_list, moisturizer_list=moisturizer_list, sunscreen_list=sunscreen_list, query_dict=query_dict ,session=session.get('user'), took_quiz=True)
  except:
    abort(404)



# *********************************
# Search bar feature
# *********************************
@app.route('/products/search', methods=["GET"])
def search_bar_filtering():
  # Store the users search into query var
  query = request.args['search']

  cleanser_list     = []
  exfoliant_list    = []
  toner_list        = []
  serum_list        = []
  moisturizer_list  = []
  sunscreen_list    = []

  # If the query was a category name or similar to category name then call get_product_with_no_filters function
  if query in ('cleanser','cleansers'):
    cleanser_list = db.get_product_with_no_filters('cleanser')
  elif query in ('exfoliant','exfoliator','exfoliators','exfoliants'):
    exfoliant_list = db.get_product_with_no_filters('exfoliant')
  elif query in ('toner','toners'):
    toner_list = db.get_product_with_no_filters('toner')
  elif query in ('serum', 'serums'):
    serum_list = db.get_product_with_no_filters('serum')
  elif query in ('moisturizer', 'moisturizers', 'moisturizing', 'lotion'):
    moisturizer_list = db.get_product_with_no_filters('moisturizer') 
  elif query in ('sunscreen', 'sunscreens', 'spf', 'lotion'):
    sunscreen_list = db.get_product_with_no_filters('sunscreen')
  else:
    # Call db function on each product to get all products that match users search 
    cleanser_list = db.search_bar_filtering(query, "cleanser")
    exfoliant_list = db.search_bar_filtering(query, "exfoliant")
    toner_list = db.search_bar_filtering(query, "toner")
    serum_list = db.search_bar_filtering(query, "serum")
    moisturizer_list = db.search_bar_filtering(query, "moisturizer")
    sunscreen_list = db.search_bar_filtering(query, "sunscreen")

  return render_template('/products.html',session=session.get('user'), cleanser_list=cleanser_list, exfoliant_list=exfoliant_list, toner_list=toner_list, serum_list=serum_list, moisturizer_list=moisturizer_list, sunscreen_list=sunscreen_list, query_dict=query )

# *******************************************************
# Personal filter on filter bar
# When user is logged in, can filter 
# products with this button and 
# get products based on quiz
# *******************************************************
@app.route('/products/recommended', methods=["GET"])
def personal_filter():

  username = session['nickname']
  user_id = db.get_user_id_from_username(username)
  
  query = db.get_user_quiz_selections(user_id)
  
  took_quiz = True

  cleanser_list     = []
  exfoliant_list    = []
  toner_list        = []
  serum_list        = []
  moisturizer_list  = []
  sunscreen_list    = []
    
  # Always 1 for this route because user can only choose 1 skin type filter for quiz
  num_of_skintype_filters_selected = 1
  
  # Either 1 or 0, If 1 then sensitive or mature, if 0 then none-target
  num_of_targets = 1

  # They can pick only 1 skin type so it cant be all
  all_skin_type = False

  # In the quiz theres no option to choose price, so by default we should show all products of all prices
  price = 'price-all'

  # Create a dicionary to keep filters
  # the second key val is set to false so if user didnt take quiz and is logged in, it will not show personalized filters button 
  query_dict = {'price': 'price-all'}

  if (query[0][0] == 'dry-skin'):
    dry_skin_type = True
    normal_skin_type = False
    oily_skin_type = False
    query_dict['dry'] = True
  if (query[0][0] == 'oily-skin'):
    oily_skin_type = True
    normal_skin_type = False
    dry_skin_type = False
    query_dict['oily'] = True
  if (query[0][0] == 'normal-skin') :
    normal_skin_type = True
    dry_skin_type = False
    oily_skin_type = False
    query_dict['normal'] = True
  if (query[0][1] == 'mature-target'):
    mature_target = True
    sensitive_target = False
    none_target = False
    query_dict['mature-target'] = True
  if (query[0][1]  =='sensitive-target'):
    sensitive_target = True
    mature_target = False
    none_target = False
    query_dict['sensitive-target'] = True   
  if (query[0][1]  == 'none-target'):
    none_target = True
    sensitive_target = False
    mature_target = False
    num_of_targets -=1
  if (query[0][2] == 2):
    query_dict['cleanser'] = True
    query_dict['sunscreen'] = True
    routine_steps = 2
  elif (query[0][2] == 3):
    query_dict['cleanser'] = True
    query_dict['moisturizer'] = True
    query_dict['sunscreen'] = True
    routine_steps = 3
  elif (query[0][2] == 6):
    query_dict['cleanser'] = True
    query_dict['exfoliant'] = True
    query_dict['toner'] = True
    query_dict['serum'] = True
    query_dict['moisturizer'] = True
    query_dict['sunscreen'] = True
    routine_steps = 6

  if (query[0][0] == None and query[0][1] == None and query[0][2] == None):
    routine_steps = 6
    took_quiz = False
    num_of_targets = 0

    # Get skin type filters
    all_skin_type = True
    normal_skin_type = True
    dry_skin_type = True
    oily_skin_type = True
    num_of_skintype_filters_selected = 4

    # Get target area filters
    sensitive_target = False
    mature_target = False

  # Depending on num of steps in routine user chose, specific products/categories will be returned
  if (routine_steps == 2):
    cleanser_list     = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "cleanser")
    sunscreen_list    = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "sunscreen")
  elif (routine_steps == 3):
    cleanser_list     = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets,sensitive_target, mature_target, price, "cleanser")
    moisturizer_list  = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "moisturizer")
    sunscreen_list    = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "sunscreen")
  elif (routine_steps == 6):
    cleanser_list     = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "cleanser")
    exfoliant_list    = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "exfoliant")
    toner_list        = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "toner")
    serum_list        = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "serum")
    moisturizer_list  = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "moisturizer")
    sunscreen_list    = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "sunscreen")

  return render_template('/products.html',session=session.get('user'),cleanser_list=cleanser_list, exfoliant_list=exfoliant_list, toner_list=toner_list, serum_list=serum_list, moisturizer_list=moisturizer_list, sunscreen_list=sunscreen_list, query_dict=query_dict, took_quiz=took_quiz)


######################################
# 3) Routine page & related functions
######################################
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
    print('Error at "/routine" route. No suitable username provided.')
    return render_template('routine.html', session=session.get('user'), is_user_logged_in=is_user_logged_in)

  # User is logged in
  is_user_logged_in = True
  username = user_details['nickname']

  # Call database function to get all of user's routine products for each category
  try:
    user_routine = db.get_user_routine(username)
  except:
    print('Error at route "routine". Failed to get user routine.')
    return render_template('routine.html', session=session.get('user'), is_user_logged_in=is_user_logged_in)

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



#####################################
# 4) Review Page & related functions
#####################################
@app.route('/reviews', methods=["GET"])
def reviews():

  # Store the product_id
  product_id = request.args.get('product_id')

  # If you go to reviews page without product_id then 404 
  if product_id == None:
    abort(404)  

  # Call db function to get all the reviews for the product
  review_list = db.get_all_reviews_for_product(product_id)
  print(review_list)
  # Get current product details
  product_details = db.get_product_details_from_id(product_id)
  product_details = product_details[0][0]  # Remove any unecessary list nesting

  try:  # Render reviews page with 
    return render_template('reviews.html', session=session.get('user'), review_list=review_list, product_details=product_details)
  except TemplateNotFound:
    abort(404)
  

# *************************************************
# Function to get review image from reviews table
# *************************************************
@app.route('/images/<int:review_id>',  methods=["GET"])
def get_image(review_id):
  img_file = db.read_image_from_id(review_id)
  return img_file


# ****************************************************************
# Add a review after selecting 'add a review' option to a product
# ****************************************************************
@app.route('/add_review', methods=["POST"])
def add_review():

  # TODO: ENSURE FILE MEDIA IS AN IMAGE

  # Ensure only logged in users can make reviews
  user_details = session
  if ('nickname' not in user_details):
    print('Error at route "/add_review". User not logged in.')
    return

  # Check for required user rating
  if ('rating' not in request.form):
    print('Error at route "/add_review". Rating not provided.')
    return

  # Initialize passable review data to send to HTML and replace with any form data after
  # --- Review variables ---
  user_id     = None
  product_id  = None
  content     = None
  rating      = None

  # --- Image variables ---
  img            = None
  img_filename   = None
  img_stream     = None


  # Initialize any existing values passed in from form
  username = user_details['nickname']
  user_id = db.get_user_id_from_username(username)
  rating = request.form['rating']

  # Check for optional review title
  if ('review-title' in request.form):
    title = request.form['review-title']

  # Check for optional written review content
  if ('review-content' in request.form):
    content = request.form['review-content']

  # Check for product ID
  if ('product-id' in request.form):
    product_id = request.form['product-id']

  # Check for optional user-submitted image
  if ('review-media' in request.files):
    img             = request.files['review-media']
    img_filename    = secure_filename(img.filename)
    img_stream      = img.read()
    

  try:  # Try to add review to database
    db.add_review(username, user_id, product_id, title, content, rating, img_filename, img_stream)
  except:
    print('Error at route "/add_review". DB function to add review failed.')

  try:  # Render back to product review page user was previously on
    return redirect('/reviews?product_id=' + product_id )
  except TemplateNotFound:
    abort(404)




######################################
# 5) Account page & related functions
######################################
@app.route('/account', methods=["GET"])
def account():
  
  user_details = session  # Get users details from session object
  
  # Ensure username exists
  # * Reference to check if a key exists within a python dict: https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
  if ('nickname' not in user_details):
    print('Error at "/account" route. No suitable username provided.')
    return

  # Get user_ids from users table to add to the review table 
  username = user_details['nickname']  # Get username
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


####################################
# Account related - Editing Quiz Selection Routes
####################################
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
  # * Valid prefernces from form: ['skin-type', 'target-type', 'number-steps']
  # * Translate to database keys: ['user_skin_type', 'user_target', 'routine_steps']
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

  try:  # Attempt to run DB command
    db.edit_user_preferences(user_details, preference_type, preference_value)
  except:
    print('Error at: "/edit_user_preferences" route. DB function failed.')

  try:  # Redirect back to account page with new preferences
    return redirect('/account')
  except TemplateNotFound:
    abort(404)

#########################################################
# 7) Quiz on home page & related functionality
#########################################################

@app.route('/api/quiz', methods=["GET"])
def quiz_results():

  # Declare lists so if it doesnt have an item, it will still render to the html
  cleanser_list     = []
  exfoliant_list    = []
  toner_list        = []
  serum_list        = []
  moisturizer_list  = []
  sunscreen_list    = []

  # Always 1 for this route because user can only choose 1 skin type filter for quiz
  num_of_skintype_filters_selected = 1
  # Either 1 or 0, If 1 then sensitive or mature, if 0 then none-target
  num_of_targets = 1

  # They can pick only 1 skin type so it cant be all
  all_skin_type = False

  # In the quiz theres no option to choose price, so by default we should show all products of all prices
  price = 'price-all'

  # Create a dicionary to keep filters 
  query_dict = {'price': 'price-all'}

  for query, value in request.args.items():
    if (query == 'skin-type'):
      if (value == 'dry-skin'):
        dry_skin_type = True
        normal_skin_type = False
        oily_skin_type = False
        query_dict['dry'] = True
        skin_value = value
      elif (value == 'oily-skin'):
        oily_skin_type = True
        normal_skin_type = False
        dry_skin_type = False
        query_dict['oily'] = True
        skin_value = value
      elif (value == 'normal-skin') :
        normal_skin_type = True
        dry_skin_type = False
        oily_skin_type = False
        query_dict['normal'] = True
        skin_value = value
    elif (query == 'target-type'):
      if (value == 'mature-target'):
        mature_target = True
        sensitive_target = False
        none_target = False
        query_dict['mature-target'] = True
        target_value = value
      elif (value =='sensitive-target'):
        sensitive_target = True
        mature_target = False
        none_target = False
        query_dict['sensitive-target'] = True  
        target_value = value 
      elif (value == 'none-target'):
        none_target = True
        sensitive_target = False
        mature_target = False
        num_of_targets -=1
        target_value = value
    elif (query == 'number-steps'):
      if (value == '2'):
        routine_steps = 2
        routine_value = value
        query_dict['cleanser'] = True
        query_dict['sunscreen'] = True
      elif (value == '3'):
        routine_steps = 3
        routine_value = value
        query_dict['cleanser'] = True
        query_dict['moisturizer'] = True
        query_dict['sunscreen'] = True
      elif (value == '6'):
        routine_steps = 6
        routine_value = value
        query_dict['cleanser'] = True
        query_dict['exfoliant'] = True
        query_dict['toner'] = True
        query_dict['serum'] = True
        query_dict['moisturizer'] = True
        query_dict['sunscreen'] = True
  
  # Depending on num of steps in routine user chose, specific products/categories will be returned
  if (routine_steps == 2):
    cleanser_list     = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "cleanser")
    sunscreen_list    = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "sunscreen")
  elif (routine_steps == 3):
    cleanser_list     = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets,sensitive_target, mature_target, price, "cleanser")
    moisturizer_list  = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "moisturizer")
    sunscreen_list    = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "sunscreen")
  elif (routine_steps == 6):
    cleanser_list     = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "cleanser")
    exfoliant_list    = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "exfoliant")
    toner_list        = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "toner")
    serum_list        = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "serum")
    moisturizer_list  = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "moisturizer")
    sunscreen_list    = db.get_products(num_of_skintype_filters_selected,normal_skin_type,dry_skin_type,oily_skin_type,all_skin_type, num_of_targets, sensitive_target, mature_target, price, "sunscreen")

  user_details = session  # Get users details from session object
  
  # Ensure username exists
  # * Reference to check if a key exists within a python dict: https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
  if ('nickname' in user_details):
    db.edit_user_preferences(user_details, 'user_skin_type', skin_value)
    db.edit_user_preferences(user_details, 'user_target', target_value)
    db.edit_user_preferences(user_details, 'routine_steps', routine_value)

  return render_template('products.html', cleanser_list=cleanser_list, exfoliant_list=exfoliant_list, toner_list=toner_list, serum_list=serum_list, moisturizer_list=moisturizer_list, sunscreen_list=sunscreen_list, query_dict=query_dict ,session=session.get('user'), took_quiz=True)

  
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

  price             = request.form.get('product-price')

  # Call database function to add a product to skincare product table
  if ((name is not None) and (url is not None) and (brand is not None) and (image_path is not None)):
    db.add_skincare_product(name, url, brand, image_path, cleanser, exfoliant, toner, serum, moisturizer, sunscreen, sensitive_target, mature_target, no_target, normal_skin, dry_skin, oily_skin, is_all, price)
  # Otherwise, report error & bad inputs
  else:
    print("Error: Failed to add to database.")

  return redirect('/admin/add-product-form')


# *************************************************
# Auth0Json page to see what auth0's json returns
# *************************************************
@app.route('/auth0json', methods=["GET"])
def auth0Json():
  return render_template('Auth0Json.html', session=session.get('user'), userDetails=json.dumps(session.get('user'), indent=4))


# ***************************************************
# TODO: DELETE LATER 
# Function to chnage data type of column in database
# ***************************************************
@app.route('/changeType', methods=["GET"])
def changeType():
  db.changeType()
  return "Type Chnaged"



#########################################################
# APIs
#########################################################
# *******************************************************
# Gets skincare products from database formatted as JSON
# *******************************************************
@app.route('/api/get-products-json', methods=["GET"])
def get_products_json():

  # Call database function to get skincare products
  products = db.get_skincare_products_json()
  
  # Return JSON format of skincare products
  return (products)


# ******************************************
# Gets skineasy users from database as JSON
# ******************************************
@app.route('/api/get-users-json', methods=["GET"])
def get_users_json():

  # Call database function to get skincare products
  users = db.get_users_json()
  
  # Return JSON format of skincare products
  return (users)


# *********************************************
# Gets skineasy reviews from database as JSON
# *********************************************
@app.route('/api/get-routines-json', methods=["GET"])
def get_routines_json():

  # Call database function to get skincare products
  routines = db.get_routines_json()
  
  # Return JSON format of skincare products
  return (routines)


# ****************************************
# Gets users reviews from database as JSON
# ****************************************
@app.route('/api/get-reviews-json', methods=["GET"])
def get_reviews_json():

  # Call database function to get user reviews
  reviews = db.get_reviews_json()
  
  # Return JSON format of user reviews
  return (reviews)



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
    if (token):  # User login details stored in auth0 token
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
        
      try:  # Fill users table by calling db function
        db.add_user(session)
      except:
        print('Error at route "auth/callback". Failed to add user  to session.')

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
# deletes a product from the db
# *********************************
@app.route('/delete', methods=["GET"])
def delete_product():

  # Call database function to get skincare products
  db.remove_from_products_table('72')

  return "Deleted"


# *********************************
# Run on port 5000 if run locally
# *********************************
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=env.get("PORT", 5000))