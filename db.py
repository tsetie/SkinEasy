''' 
Database access:
docs:
* http://initd.org/psycopg/docs/
* http://initd.org/psycopg/docs/pool.html
* http://initd.org/psycopg/docs/extras.html#dictionary-like-cursor
'''


#################################
# Imports
#################################
from contextlib import contextmanager
import logging
import os

from flask import current_app, g, redirect, render_template, request, send_file, session, url_for

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

import io

##################################################################
# Connection pool setup
##################################################################

# ******************************************************************
# Global connection variable
pool = None

# Connection pool to setup
def setup():
    global pool
    DATABASE_URL = os.environ['DATABASE_URL']
    current_app.logger.info(f'creating db connection pool')
    pool = ThreadedConnectionPool(1, 100, dsn=DATABASE_URL, sslmode='require')

@contextmanager
def get_db_connection():
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)

@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
      cursor = connection.cursor(cursor_factory=DictCursor)
      # cursor = connection.cursor()
      try:
          yield cursor
          if commit:
              connection.commit()
      finally:
          cursor.close()
          
# ******************************************************************


###################################################################################################
# 1) PRODUCTS TABLE functions
###################################################################################################
# ****************************************************
# A) Function to add a product to skincare products table
# Input(s):   product_name (string):  text name of product we want to find the 'product_id' of
# Returns:    product_id (integer):   ID from products table of product name parameter
# ****************************************************
def add_skincare_product(product_name, product_url, product_brand, image_path, cleanser=False, exfoliant=False, toner=False, serum=False, moisturizer=False, sunscreen=False, sensitive_target=False, mature_target=False, none_target=False, normal_skin=False, dry_skin=False, oily_skin=False, is_all=False, price=None):
    with get_db_cursor(True) as cur:

        # Build SQL insertion statement for each column in products table
        sql = '''
            INSERT INTO skineasy_skincare_products (
                product_name,
                product_url, 
                product_brand,
                image_path,
                cleanser,
                exfoliant,
                toner, 
                serum, 
                moisturizer, 
                sunscreen,
                sensitive_target, 
                mature_target, 
                none_target,
                normal_skin, 
                oily_skin, 
                dry_skin, 
                is_all,
                price
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
        # Execute sql insertion
        cur.execute(sql, (product_name, product_url, product_brand, image_path, cleanser, exfoliant, toner, serum, moisturizer, sunscreen, sensitive_target, mature_target, none_target, normal_skin, oily_skin, dry_skin, is_all, price))
        current_app.logger.info('Attempted to add entry to skincare products table')
        return


# *****************************************************************************************
# B) Function to get product id based on product name string
# Input(s):   product_name (string):  text name of product we want to find the 'product_id' of
# Returns:    product_id (integer):   ID from products table found using product name parameter
# *****************************************************************************************
def get_product_id_from_product_name(product_name):
    with get_db_cursor(True) as cur:
    
        # Make SQL statement to get product ID from the product name (string) parameter
        get_product_sql = "SELECT %s FROM %s WHERE %s = '%s'" % ('product_id', 'skineasy_skincare_products', 'product_name', product_name)
        cur.execute(get_product_sql)
        product_id = cur.fetchall()[0][0]
        return product_id


# *****************************************************************************************
# C) Function to get all products with product_id
# Input(s):  product_id (integer):   ID from products table found using product name parameter
# Returns:   product_name (string):  text name of product we get from ID
# *****************************************************************************************
def get_product_name(product_id):
    with get_db_cursor(True) as cur:    

        # Build SQL string to get product name from product ID
        sql = (
            "SELECT row_to_json(row) "
            "FROM (SELECT product_name FROM skineasy_skincare_products WHERE product_id = %s ) row"
            % product_id
        )
        
        # Execute sql statement with data
        cur.execute(sql)
        return cur.fetchall()


# *****************************************************************************************
# D) Function to get a product's details based on product ID
# Input(s):  product_id (integer):   ID from products table found using product name parameter
# Returns:   JSON (dictionary):      column key and pair values from product table
# *****************************************************************************************
def get_product_details_from_id(product_id):
    with get_db_cursor(True) as cur:    

        # Build SQL string to get product details from product ID 
        sql = '''
            SELECT row_to_json(skineasy_skincare_products)
            FROM skineasy_skincare_products
            WHERE product_id = %s
        '''

        # Execute sql statement with data
        cur.execute(sql, (product_id))
        return cur.fetchall()
    
    

# *****************************************************************************
# D) Function to get all skincare products from skincare products table as JSON
# *****************************************************************************
def get_skincare_products_json():
    with get_db_cursor() as cur:

        # Make SQL statement asking database for all entries in products table as JSON
        sql = 'SELECT row_to_json(skineasy_skincare_products) FROM skineasy_skincare_products ORDER BY product_id ASC'
        cur.execute(sql)   
        return cur.fetchall()


# ************************************************************************************************************************************************************
# E) Function to get skincare products based on product category tags as JSON
# Input(s): 
# References:
#   * Reference to convert lists to tuples: https://www.w3schools.com/python/python_tuples_update.asp
#   * Reference to use multi-line strings in python with parenthesis: https://stackoverflow.com/questions/5437619/python-style-line-continuation-with-strings
#   * Reference to use '%s' in python: https://www.geeksforgeeks.org/what-does-s-mean-in-a-python-format-string/
# ************************************************************************************************************************************************************
def filter_products(num_filters=0, cleanser_filter=False, exfoliant_filter=False, toner_filter=False, serum_filter=False, moisturizer_filter=False, sunscreen_filter=False):
    with get_db_cursor(True) as cur:    
        
        where_clause = ''  # Build a PSQL WHERE clause based on filters
        
        # If there is at least one filter to be applied, set up WHERE clause format
        if (num_filters >= 1):
            where_clause += 'WHERE %s'

        # For any additional filters, begin to use 'OR' statement in WHERE clause
        for i in range(1, num_filters-1):
            where_clause += ' OR %s' 
        data = []  # Add any filters to where clause in a python list --> python tuple

        # Check passed in filters
        if (cleanser_filter):
            data.append('cleanser IS TRUE')

        if (exfoliant_filter):
            data.append('exfoliant IS TRUE')

        if (toner_filter):
            data.append('toner IS TRUE')

        if (serum_filter):
            data.append('serum IS TRUE')

        if (moisturizer_filter):
            data.append('moisturizer IS TRUE')

        if (sunscreen_filter):
            data.append('sunscreen IS TRUE')

        # Convert SQL data to tuples to fill in '%s' for SQL strings
        data = tuple(data)
        
        # Fill where clause with data tuple
        where_clause = where_clause % data

        # Make SQL SELECT statement with filter data (tuple)
        sql = (
            'SELECT row_to_json(skineasy_skincare_products) '
            'FROM skineasy_skincare_products '
            + where_clause
        )

        # Execute sql statement with data
        cur.execute(sql)
        return cur.fetchall()


# **********************************************************************************************************************************************************
# F) Function to get all products with any user applied filters as JSON
# Input(s): 
# References:
#   * Reference to convert lists to tuples: https://www.w3schools.com/python/python_tuples_update.asp
#   * Reference to use multi-line strings in python with parenthesis: https://stackoverflow.com/questions/5437619/python-style-line-continuation-with-strings
#   * Reference to use "%s" in python: https://www.geeksforgeeks.org/what-does-s-mean-in-a-python-format-string/
#   * Reference to display 2 decimal points for price https://stackoverflow.com/questions/13113096/how-to-round-an-average-to-2-decimal-places-in-postgresql
# **********************************************************************************************************************************************************
def get_products(num_of_skintype_filters_selected, normal_skin_type, dry_skin_type, oily_skin_type, all_skin_type,num_of_targets, sensitive_target, mature_target, price, product_type):
    with get_db_cursor(True) as cur:

        where_clause = "%s"  # Build a PSQL WHERE clause based on filters for SKIN TYPE
    
        # For any additional filters, begin to use "OR" statement in WHERE clause
        for i in range(1, num_of_skintype_filters_selected):
            where_clause += " OR %s" 

        data = []  # Add any filters to where clause in a python list --> python tuple

        # Build a PSQL WHERE clause based on filters for TARGET AREAS
        target_clause = "AND (%s"

        # For any additional filters, begin to use "or" statement in TARGET clause
        for i in range(1, (num_of_targets)):
            target_clause += " OR %s"

        # Add closing parenthesis for target_clause
        target_clause += ")"
        target_data = []

        # In case price is not filtered, at least need an empty string to pass into SQL query
        price_range_clause = ""

        # Check passed in filters
        # --- Skin type ---
        if (normal_skin_type):
            data.append("normal_skin IS TRUE")

        if (oily_skin_type):
            data.append("oily_skin IS TRUE")

        if (dry_skin_type):
            data.append("dry_skin IS TRUE")

        if (all_skin_type):
            data.append("is_all IS TRUE")

        # --- Skin target ---
        if (sensitive_target):
            target_data.append("sensitive_target IS TRUE")

        if (mature_target):
            target_data.append("mature_target IS TRUE")
       
        if (num_of_targets < 1):
            target_data.append("none_target is TRUE OR sensitive_target IS TRUE OR mature_target IS TRUE")

        # --- Price ---
        if (price == "price-under-20"):
            price_range_clause = ("  AND price < 20.00")

        elif (price == "price-20-40"):
           price_range_clause = " AND price > 20.00 AND price < 40.00"

        elif (price == "price-40-60"):
           price_range_clause = (" AND price > 40.00 AND price < 60.00")

        elif (price == "price-60-80"):
           price_range_clause = (" AND price > 60.00 AND price < 80.00")

        elif (price == "price-above-80"):
            price_range_clause = (" AND price > 80.00")

        # Convert SQL data to tuples to fill in '%s' for SQL strings
        data = tuple(data)
        target_data = tuple(target_data)

        where_clause = where_clause % data              # Fill where clause with data tuple
        target_clause = target_clause % target_data     # Fill target clause with target data tuple

        # Make SQL SELECT statement with filter data (tuple)
        sql = (
            "SELECT row_to_json(row) "
            "FROM (SELECT * , to_char(price::numeric, 'FM9999D00') display_price FROM skineasy_skincare_products ) row "
            "WHERE %s IS TRUE "
            "AND (" % product_type
            + where_clause + ") "
            + target_clause
            + " %s" % price_range_clause
        )
        
        # Execute sql statement with data
        cur.execute(sql)
        return cur.fetchall()


# *****************************************************************
# G) Function to get all products with specified filters 
# Input(s):
#   * query (string):           user-entered search bar text
#   * product_type (string):    skincare product category
# Returns: search results as JSON
# Refernces:
#   * Reference to use multi-line strings in python with parenthesis: https://stackoverflow.com/questions/5437619/python-style-line-continuation-with-strings
#   * Reference to use "%s" in python: https://www.geeksforgeeks.org/what-does-s-mean-in-a-python-format-string/
#   * Reference to display 2 decimal points for price https://stackoverflow.com/questions/13113096/how-to-round-an-average-to-2-decimal-places-in-postgresql
# *****************************************************************
def search_bar_filtering(query, product_type):
    with get_db_cursor(True) as cur:    

        # Build the regex to to find all products that have the searched word 
        query_regex = "'%" + query + "%'"

        # Build SQL string using string querye
        sql = (
            "SELECT row_to_json(row) "
            "FROM (SELECT * , to_char(price::numeric, 'FM9999D00') display_price FROM skineasy_skincare_products ) row "
            "WHERE %s IS TRUE AND " % product_type +
            "product_name ILIKE %s" % query_regex
        )
        
        print(sql)

        # Execute sql statement with data
        cur.execute(sql)
        return cur.fetchall()

# *****************************************************************
# Select a category with no filters for the search functionality
# *****************************************************************
def get_product_with_no_filters(product_type):
    with get_db_cursor(True) as cur:    

        # Build SQL string with product_type
        sql = (
            "SELECT row_to_json(row) "
            "FROM (SELECT * , to_char(price::numeric, 'FM9999D00') display_price FROM skineasy_skincare_products ) row "
            "WHERE %s IS TRUE" % product_type
        )

        # Execute sql statement with data
        cur.execute(sql)
        return cur.fetchall()



# ************************************************************************************************
# H) Function to get product id based on product name string
# Input(s):     product_name (string):  text representing which product name we want the ID of
# Returns:      product_id (integer):   ID from products table found using product name parameter
# ************************************************************************************************
def get_product_id_from_product_name(product_name):
    with get_db_cursor(True) as cur:
        
        get_product_sql = "SELECT %s FROM %s WHERE %s = '%s'" % ('product_id', 'skineasy_skincare_products', 'product_name', product_name)
        cur.execute(get_product_sql)
        product_id = cur.fetchall()[0][0]
        return product_id



###################################################################################################
# 2) USER TABLE functions
###################################################################################################
# *****************************************************************
# A) Function to get all skineasy users in ascending order as JSON
# *****************************************************************
def get_users_json():
    with get_db_cursor() as cur:
        
        # Make SQL statement asking database for all entries in users table
        sql = 'SELECT row_to_json(skineasy_users) FROM skineasy_users ORDER BY user_id ASC'
        cur.execute(sql)   
        return cur.fetchall()


# *******************************************************************************************
# B) Function to get user id based on username string
# Input(s):   username (string): user unique text identifier
# Returns:    user_id (integer): ID from users table found using provided username parameter
# *******************************************************************************************
def get_user_id_from_username(username):
    with get_db_cursor(True) as cur:
        
        # Make SQL statement asking for user ID using provided username input
        get_user_sql = "SELECT %s FROM %s WHERE %s = '%s'" % ('user_id', 'skineasy_users', 'username', username)
        cur.execute(get_user_sql)
        user_id = cur.fetchall()[0][0]
        return user_id


# *******************************************************************************************
# B) Function to get username based on user ID
# Input(s):   user_id (integer): ID from users table
# Returns:    username (string): user unique text identifier found using user_id parameter
# *******************************************************************************************
def get_username_from_id(user_id):
    with get_db_cursor(True) as cur:
        
        # Make SQL statement asking for username using provided user ID
        get_user_sql = "SELECT %s FROM %s WHERE %s = '%s'" % ('username', 'skineasy_users', 'user_id', user_id)
        cur.execute(get_user_sql)
        username = cur.fetchall()[0][0]
        return username


# *************************************************************************************************************************************************************************************
# C) Function to add a user to the users table when logging in for the first time
# Input(s):   user_details (dictionary):  two-key dictionary with { username: (string), email: (string) } as keys
# Returns:    nothing
# References: 
#   * Reference to check if a key exists within a python dict:    https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
#   * Reference on PSQL insertion without duplicates:             https://stackoverflow.com/questions/1009584/how-to-emulate-insert-ignore-and-on-duplicate-key-update-sql-merge-with-po
# *************************************************************************************************************************************************************************************
def add_user(user_details):
    with get_db_cursor(True) as cur:
        
        # --- Check for invalid Input(s) ---
        # Only add user if provided a username and email
        if (('nickname' not in user_details) or ('email' not in user_details)):
            current_app.logger.info('Error at function "add_user": Invalid username OR email given.')
        
        # Otherwise, we can get username & email since they exist
        user = user_details['nickname']
        email = user_details['email']

        # Build SQL statement with user and email
        # NOTE: Don't add to users table if a user already exists (don't want duplicate entries for users)
        sql = '''
            INSERT INTO skineasy_users (username, email)
            VALUES (%s, %s)
            ON CONFLICT (username, email) DO NOTHING;
            '''

        # Execute sql statement with username and email data
        cur.execute(sql, (user, email))

        # Report that attempt to add user was made
        current_app.logger.info('Attempted to add user to users table.')
        return


# *****************************************************************************************************************************************************************
# D) Function to update users skincare preferences in users table
# Input(s): 
#   * user_details (dictionary):      two-key dictionary with { username: (string), email: (string) } keys
#   * preference_type (string):       text representing which user preference to change  
#   * modified_preference (string):   specified value of what preference type should change to
# Returns:  
#   * void
# References:
#   * Reference to check if a key exists within a python dict:    https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
# *****************************************************************************************************************************************************************
def edit_user_preferences(user_details, preference_type, preference_value):
    with get_db_cursor(True) as cur: 
        
        # --- Check for invalid Input(s) ---
        # 1) Ensure username valid
        if ('nickname' not in user_details):
            current_app.logger.info('Error at function "edit_user_preferences": Invalid username given.')
            return

        # 2) Ensure preference type is valid
        valid_preferences = ['user_skin_type', 'user_target', 'routine_steps']
        if (preference_type not in valid_preferences):
            current_app.logger.info('Error at function "edit_user_preferences": Invalid preference type given.')
            return

        # 3) Ensure modified preference is valid
        valid_skin_types    = ['normal-skin', 'dry-skin', 'oily-skin']
        valid_targets       = ['sensitive-target', 'mature-target', 'none-target']
        valid_routine_steps = ['2', '3', '6']

        if ((preference_type == 'user_skin_type') and (preference_value not in valid_skin_types)):
            current_app.logger.info('Error at function "edit_user_preferences": Invalid preference value for skin type given.')
            return
        
        if ((preference_type == 'user_target') and (preference_value not in valid_targets)):
            current_app.logger.info('Error at function "edit_user_preferences": Invalid preference value for target ype given.')
            return

        if ((preference_type == 'routine_steps') and (preference_value not in valid_routine_steps)):
            current_app.logger.info('Error at function "edit_user_preferences": Invalid preference value for number of steps given.')
            return

        # --- Get username in order to find user ID ---
        username = user_details['nickname']
        user_id = get_user_id_from_username(username)

        # Build SQL string to change a user's skincare preferences
        sql = '''
            UPDATE skineasy_users
            SET %s = '%s'
            WHERE user_id = %s
            '''  % (preference_type, preference_value, user_id)

        # Execute sql statement with default data
        cur.execute(sql)
        current_app.logger.info('Attempted to edit user preference.')
        return


# ****************************************************************************
# E) Function to get QUIZ SELECTIONS from the user table for a specific user
# Input(s):     user_id (int):   ID of user in users table
# Returns:
# ****************************************************************************
def get_user_quiz_selections(user_id):
    with get_db_cursor() as cur:
        
        # Make SQL statement asking database for quiz selections from users table
        sql = 'SELECT user_skin_type, user_target, routine_steps FROM skineasy_users WHERE user_id = %s'
        cur.execute(sql, (user_id,))   
        return cur.fetchall()


# **********************************************************************************
# F) Function to get ALL USER_IDS and REVIEWER_NAMES from the user table as a list
# Returns:
# **********************************************************************************
def get_all_user_ids_and_names():

    with get_db_cursor() as cur:
        
        # Make SQL statement asking database for all entries in users table
        sql = 'SELECT user_id, username FROM skineasy_users'
        cur.execute(sql)   
        return cur.fetchall()



    
###################################################################################################
# 3) ROUTINE TABLE functions
###################################################################################################
# ****************************************************
# A) Function to get all routine table entries as JSON
# ****************************************************
def get_routines_json():
    with get_db_cursor() as cur:
        
        # Make SQL statement asking database for all entries in users table
        sql = "SELECT row_to_json(skineasy_routines) FROM skineasy_routines ORDER BY user_id ASC"
        cur.execute(sql)   
        return cur.fetchall()



# **************************************************************************************************************************
# B) Function to add an entry to routines table given a dictionary with username and product name
# Input(s): user_product_info (dictionary):     two-key dictionary with { username: (string), product name: (string) } keys
# Returns:  void
# **************************************************************************************************************************
def add_to_routine(user_product_info):
    with get_db_cursor(True) as cur:
        current_app.logger.info('Adding entry to routine table')

        # Get username and product name 
        username = user_product_info['username']
        product_name = user_product_info['productName']

        # Build SQL where statements to get user ID and product ID based on provided arguments
        user_id = get_user_id_from_username(username)
        product_id = get_product_id_from_product_name(product_name)

        # Use user ID and product ID to store in user's routine wishlist

        # Build SQL insertion statement and ensure product ids are unique
        add_routine_entry_sql = '''
            INSERT INTO skineasy_routines (user_id, product_id)
            VALUES (%s, %s)
            ON CONFLICT (user_id, product_id) DO NOTHING;
            '''
        # Execute sql insertion
        cur.execute(add_routine_entry_sql, (user_id, product_id))
        return


# ****************************************************
# C) Function to add an entry to routines table given a dictionary with username and product name
# Input(s):     user_
# Returns:      void
# ****************************************************
def remove_from_routine(user_product_info):
    with get_db_cursor(True) as cur:
        current_app.logger.info('Adding entry to routine table')

        # Get username and product name 
        username = user_product_info['username']
        product_name = user_product_info['productName']

        # Build SQL where statements to get user ID and product ID based on provided arguments
        user_id = get_user_id_from_username(username)
        product_id = get_product_id_from_product_name(product_name)

        # Use user ID and product ID to store in user's routine wishlist

        # Build SQL insertion statement and ensure product ids are unique
        remove_routine_entry_sql = '''
            DELETE 
            FROM skineasy_routines 
            WHERE user_id = %s AND product_id = %s
            '''
        # Execute sql insertion
        cur.execute(remove_routine_entry_sql, (user_id, product_id))

        return


# ****************************************************
# D) Function to get a user's respective routine products
# Input(s):     username (string)
# Returns:      
# ****************************************************
def get_user_routine(username):
    with get_db_cursor(True) as cur:

        # Using the username string, get JSON of all products via routines table that have right user ID
        user_id = get_user_id_from_username(username)

        # Get all product IDs that are associated with user's ID
        # * Reference on SQL joining w/ sub queries: https://www.tutorialspoint.com/postgresql/postgresql_sub_queries.htm
        get_user_products_sql = '''
            SELECT row_to_json(row) 
            FROM (
                SELECT * , to_char(price::numeric, 'FM9999D00') display_price FROM skineasy_skincare_products 
                WHERE skineasy_skincare_products.product_id in (
                SELECT product_id FROM skineasy_routines WHERE skineasy_routines.user_id = %s)
                ) row;
            ''' % user_id

        cur.execute(get_user_products_sql)
        return cur.fetchall()
        

# ********************************************************************************************************
# E) Function to get a get a specific product type based on type (string) and username (string)
# Input(s):
# Returns:
# ********************************************************************************************************
def get_user_routine_by_type(product_type=None, username=None):
    with get_db_cursor(True) as cur:

        # Ensure Input(s) don't cause an internal server error
        if ((username is None)):
            current_app.logger.info("Error: get_user_routine_type - Function Input(s) invalid.")
            return

        # Using the username string, get JSON of all products via routines table that have right user ID
        user_id = get_user_id_from_username(username)

        # Get all product IDs that are associated with user's ID
        # * Reference on SQL joining w/ WHERE clause: https://mode.com/sql-tutorial/sql-joins-where-vs-on/
        # If NO product category specified
        if (product_type is None):
            get_user_products_sql = '''
            SELECT row_to_json(skineasy_skincare_products)
            FROM skineasy_skincare_products
            INNER JOIN skineasy_routines ON skineasy_routines.product_id = skineasy_skincare_products.product_id
            WHERE skineasy_routines.user_id = %s
            ''' % (user_id)
        
        # If product category specified
        else:
            get_user_products_sql = '''
            SELECT row_to_json(skineasy_skincare_products)
            FROM skineasy_skincare_products
            INNER JOIN skineasy_routines ON skineasy_routines.product_id = skineasy_skincare_products.product_id
            WHERE skineasy_routines.user_id = %s AND skineasy_skincare_products.%s = true;
            ''' % (user_id, product_type)
            
        cur.execute(get_user_products_sql)
        return cur.fetchall()
        


###################################################################################################
# 4) REVIEWS TABLE functions
###################################################################################################
# *********************************************************
# A) Function to get all reviews from the review table as JSON
# Returns: 
# *********************************************************
def get_reviews_json():
    with get_db_cursor() as cur:

        # Make SQL statement asking database for all entries in reviews table
        sql = "SELECT row_to_json(skineasy_reviews) FROM skineasy_reviews ORDER BY review_id ASC"
        cur.execute(sql)

        return cur.fetchall()
    

# ****************************************************************************************************************************************************************************
# B) Function to add a review to the review table
# Input(s):
#   * username (string):  name of user who made review
#   * user_id (int):      ID of user that made review
#   * product_id (int):   ID of product that review is about
#   * title (string):     review header text
#   * content (string):   written description of review
#   * rating (integer):   1-5 star score
# References:
#   * Reference to check if a key exists within a python dict: https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
#   * Reference on PSQL insertion without duplicates: https://stackoverflow.com/questions/1009584/how-to-emulate-insert-ignore-and-on-duplicate-key-update-sql-merge-with-po
# ****************************************************************************************************************************************************************************
def add_review(reviewer_name, user_id, product_id, title, content, rating, img_filename, img_stream):
    with get_db_cursor(True) as cur: 
   
        # Only add review if we have required parameters
        if (reviewer_name is None or user_id is None or product_id is None or rating is None):
            current_app.logger.info("Error: add_review - Function Input(s) invalid.")
            return

        # Build SQL statement for inserting new review
        insert_sql = '''
            INSERT INTO skineasy_reviews (
                reviewer_name,
                user_id,
                product_id,
                title,
                content,
                rating,
                img_filename,
                img_stream
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, product_id) DO 
            UPDATE
            SET title = %s,
                content = %s,
                rating = %s,
                img_filename = %s,
                img_stream = %s
            WHERE skineasy_reviews.user_id = %s AND skineasy_reviews.product_id = %s;
            '''

        # Execute sql statement with default data
        cur.execute(insert_sql, (reviewer_name, user_id, product_id, title, content, rating, img_filename, img_stream, title, content, rating, img_filename, img_stream, user_id, product_id))
        current_app.logger.info('Attempted to add entry to skincare reviews table')

        return


# *****************************************************************
# C) Function to get review details based on user_id and product_id
# Input(s):
#   * user_id (int):      ID of user that made review
#   * product_id (int):   ID of product that review is about
# Returns: JSON of review entry row
# *****************************************************************
def get_review_from_user_product_ids(user_id, product_id):
    with get_db_cursor(True) as cur: 

        # Ensure inputs exist
        if (user_id is None or product_id is None):
            current_app.logger.info("Error: get_review_id_from_user_product_ids - Function Input(s) invalid.")
            return 

        # Make SQL statement string to get review details
        sql = '''
            SELECT row_to_json(skineasy_reviews)
            FROM skineasy_reviews
            WHERE user_id = %s AND product_id = %s
        '''

        # # Execute sql statement with default data
        cur.execute(sql, (user_id, product_id))
        return cur.fetchall()


# ***************************************************************
# D) Function to show all reviews for a certain product
# Input(s):  product_id (int):   ID of product that review is about
# Returns:   all reviews for specified product
# ***************************************************************
def get_all_reviews_for_product(product_id):
    with get_db_cursor(True) as cur: 
   
        # Source that showed how to convert CURRENT_TIMESTAMP to a string
        # Build SQL statement to get all reviews for a product with the product_id
        sql = '''
            SELECT row_to_json(rows)
            FROM (SELECT * , TO_CHAR(published_date,'Month DD, YYYY') FROM skineasy_reviews ) rows
            WHERE product_id = %s
            '''
        # Execute sql statement with default data
        cur.execute(sql, product_id)
        return cur.fetchall()


# ********************************************************
# E) Function to show all reviews written by a specific user
# Input(s): 
# ********************************************************
def get_all_reviews_by_user(user_id):
    with get_db_cursor(True) as cur: 
        
        # # # Build SQL statement to get all reviews for a product with the product_id
        sql = '''
            SELECT * 
            FROM skineasy_reviews 
            WHERE user_id = %s
            '''
        # # Execute sql statement with default data
        cur.execute(sql, user_id)
        return cur.fetchall()

# ***********************************************************
# D) Function to read an image from bytea sequence
# # Input(s): review_id (int)
# Reference:
# ***********************************************************
def read_image_from_id(review_id):
    with get_db_cursor(True) as cur:

        cur.execute("SELECT * FROM skineasy_reviews where review_id=%s", (review_id,))
        image_row = cur.fetchone() # just another way to interact with cursors
        
        # in memory pyhton IO stream
        stream = io.BytesIO(image_row["img_stream"])
            
        # use special "send_file" function
        return send_file(stream, download_name=image_row["img_filename"])
    
    
# DELETE LATER 
def remove_from_products_table(product_id):
    with get_db_cursor(True) as cur:

        sql = '''
            DELETE 
            FROM skineasy_skincare_products 
            WHERE product_id = %s
            '''
        # Execute sql insertion
        cur.execute(sql, (product_id,))

