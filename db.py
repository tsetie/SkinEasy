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

from flask import current_app, g

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor


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
# Function to add a product to skincare products table
# ****************************************************
def add_skincare_product(product_name, product_url, product_brand, image_path, cleanser=False, exfoliant=False, toner=False, serum=False, moisturizer=False, sunscreen=False, sensitive_target=False, mature_target=False, no_target=False, normal_skin=False, oily_skin=False, dry_skin=False, is_all=False):
    
    # Since we're using connection pooling, it's not as big of a deal to have   
    # lots of short-lived cursors (I think -- worth testing if we ever go big)
    
    with get_db_cursor(True) as cur:
        current_app.logger.info('Adding entry to skincare products table')

        # Build SQL insertion statement
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
                is_all
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
        # Execute sql insertion
        cur.execute(sql, (product_name, product_url, product_brand, image_path, cleanser, exfoliant, toner, serum, moisturizer, sunscreen, sensitive_target, mature_target, no_target, normal_skin, oily_skin, dry_skin, is_all))


# ****************************************************
# Function to get all skincare products from skincare products table
# ****************************************************
def get_skincare_products_json():
    with get_db_cursor() as cur:

        # Make SQL statement asking database for all entries in products table
        sql = 'SELECT row_to_json(skineasy_skincare_products) FROM skineasy_skincare_products ORDER BY product_id ASC'
       
        cur.execute(sql)   
        return cur.fetchall()


# ****************************************************
# Function to get skincare products based on filter tags
# ****************************************************
def filter_products(num_filters=0, cleanser_filter=False, exfoliant_filter=False, toner_filter=False, serum_filter=False, moisturizer_filter=False, sunscreen_filter=False):
    with get_db_cursor(True) as cur:    
        
        # *Build a PSQL WHERE clause based on filters
        # If any filters are to be applied, set up a WHERE clause
        where_clause = ''
        
        # If there is at least one filter to be applied, set up WHERE clause format
        if (num_filters >= 1):
            where_clause += 'WHERE %s'

        # For any additional filters, begin to use 'OR' statement in WHERE clause
        for i in range(1, num_filters-1):
            where_clause += ' OR %s' 
 
        # Add any filters to where clause in a python list --> python tuple
        data = []

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

        # Reference to convert lists to tuples: https://www.w3schools.com/python/python_tuples_update.asp
        data = tuple(data)
        
        # Fill where clause with data tuple
        print("Where:", where_clause)
        print("Data:", data)
        where_clause = where_clause % data

        # References: 
        # * Reference to use multi-line strings in python with parenthesis: https://stackoverflow.com/questions/5437619/python-style-line-continuation-with-strings
        # * Reference to use '%s' in python: https://www.geeksforgeeks.org/what-does-s-mean-in-a-python-format-string/
        sql = (
            'SELECT row_to_json(skineasy_skincare_products) '
            'FROM skineasy_skincare_products '
            + where_clause
        )

        # Execute sql statement with data
        cur.execute(sql)
        return cur.fetchall()


# ****************************************************
# Function to get all products with filters
# ****************************************************
def get_products(num_of_skintype_filters_selected, normal_skin_type, dry_skin_type, oily_skin_type, all_skin_type, price, product_type):
    with get_db_cursor(True) as cur:    
        
        # *Build a PSQL WHERE clause based on filters
        # If any filters are to be applied, set up a WHERE clause
        where_clause = "%s"

        # For any additional filters, begin to use "OR" statement in WHERE clause
        for i in range(1, num_of_skintype_filters_selected):
            where_clause += " OR %s" 
 
        # Add any filters to where clause in a python list --> python tuple
        data = []

        # Check passed in filters
        if (normal_skin_type):
            data.append("normal_skin IS TRUE")

        if (oily_skin_type):
            data.append("oily_skin IS TRUE")

        if (dry_skin_type):
            data.append("dry_skin IS TRUE")

        if (all_skin_type):
            data.append("is_all IS TRUE")

        if(price == "price-under-20"):
            data.append("(price < 20)")

        if(price == "price-20-40"):
           data.append("(price > 20 AND price < 40)")

        if(price == "price-40-60"):
           data.append("(price > 40 AND price < 60)")

        if(price == "price-60-80"):
           data.append("(price > 60 AND price < 80)")

        if(price == "price-above-80"):
            data.append("price > 80")

        # Reference to convert lists to tuples: https://www.w3schools.com/python/python_tuples_update.asp
        data = tuple(data)

        print("\n")
        print(where_clause)
        # Fill where clause with data tuple
        where_clause = where_clause % data
        print(where_clause)
        
        # Reference to use multi-line strings in python with parenthesis: https://stackoverflow.com/questions/5437619/python-style-line-continuation-with-strings
        # Reference to use "%s" in python: https://www.geeksforgeeks.org/what-does-s-mean-in-a-python-format-string/
        sql = (
            "SELECT row_to_json(skineasy_skincare_products) "
            "FROM skineasy_skincare_products "
            "WHERE %s IS TRUE "
            "AND (" % product_type
            + where_clause
            + ")"
        )
        
        # Execute sql statement with data
        cur.execute(sql)
        return cur.fetchall()


###################################################################################################
# 2) USER TABLE functions
###################################################################################################

# ****************************************************
# Function to get ALL USERS from the user table as JSON
# ****************************************************
def get_users_json():
    with get_db_cursor() as cur:
        
        # Make SQL statement asking database for all entries in users table
        sql = 'SELECT row_to_json(skineasy_users) FROM skineasy_users ORDER BY user_id ASC'
        cur.execute(sql)   
        return cur.fetchall()


# ****************************************************
# Function to add a user to the users table after they make an account
# ****************************************************
def add_user(user_details):
    with get_db_cursor(True) as cur:
        
        # Only add user if provided a username and email
        # Reference to check if a key exists within a python dict: https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
        if (('nickname' in user_details) and ('email' in user_details)):
            user = user_details['nickname']
            email = user_details['email']

            # Build SQL statement with sessions object
            # Make sure no duplicate emails (emails are unique)
            # Reference on PSQL insertion without duplicates: https://stackoverflow.com/questions/1009584/how-to-emulate-insert-ignore-and-on-duplicate-key-update-sql-merge-with-po
            sql = '''
                INSERT INTO skineasy_users (username, email)
                VALUES (%s, %s)
                ON CONFLICT (username, email) DO NOTHING;
                '''

            # Execute sql statement with default data
            cur.execute(sql, (user, email))

            print('Adding user to users table.')

        return


# ****************************************************
# Function to update users skin type in users table
# ****************************************************
def edit_skin_type(user_details, modified_skin_type):
    with get_db_cursor(True) as cur: 
        
        # Get username
        # Reference to check if a key exists within a python dict: https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
        if ('nickname' in user_details):
            user = user_details['nickname']

            # Get user_ids from users table to add to the review table 
            usersID_and_names = get_all_user_ids_and_names()

            # Iterate list and find user_id corresponding to user's name
            for item in usersID_and_names:
                if item[1] == user:
                    user_id = item[0]
        
            sql = '''
                UPDATE skineasy_users
                SET user_skin_type = %s
                WHERE user_id = %s
                '''

            # Execute sql statement with default data
            cur.execute(sql, (modified_skin_type, user_id))


# ****************************************************
# Function to update users skin target in users table
# ****************************************************
def edit_skin_target(user_details, modified_skin_target):
    with get_db_cursor(True) as cur: 
        
        # Get username
        # Reference to check if a key exists within a python dict: https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
        if ('nickname' in user_details):
            user = user_details['nickname']

            # Get user_ids from users table to add to the review table 
            usersID_and_names = get_all_user_ids_and_names()

            # Iterate list and find user_id corresponding to user's name
            for item in usersID_and_names:
                if item[1] == user:
                    user_id = item[0]
        
            sql = '''
                UPDATE skineasy_users
                SET user_target = %s
                WHERE user_id = %s
                '''

            # Execute sql statement with default data
            cur.execute(sql, (modified_skin_target, user_id))


# ****************************************************
# Function to update users steps amount in users table
# ****************************************************
def edit_num_of_steps(user_details, modified_num_of_steps):
    with get_db_cursor(True) as cur: 
        
        # Get username
        # Reference to check if a key exists within a python dict: https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
        if ('nickname' in user_details):
            user = user_details['nickname']

            # Get user_ids from users table to add to the review table 
            usersID_and_names = get_all_user_ids_and_names()

            # Iterate list and find user_id corresponding to user's name
            for item in usersID_and_names:
                if item[1] == user:
                    user_id = item[0]
        
            sql = '''
                UPDATE skineasy_users
                SET routine_steps = %s
                WHERE user_id = %s
                '''

            # Execute sql statement with default data
            cur.execute(sql, (modified_num_of_steps, user_id))


# ****************************************************
# Function to get QUIZ SELECTIONS from the user table for a specific user
# ****************************************************
def get_user_quiz_selections(user_id):

    with get_db_cursor() as cur:
        
        # Make SQL statement asking database for quiz selections from users table
        sql = "SELECT user_skin_type, user_target, routine_steps FROM skineasy_users WHERE user_id = %s"
        cur.execute(sql, (user_id,))   
        return cur.fetchall()


# ****************************************************
# Function to get ALL USER_IDS and REVIEWER_NAMES from the user table as a list
# ****************************************************
def get_all_user_ids_and_names():

    with get_db_cursor() as cur:
        
        # Make SQL statement asking database for all entries in users table
        sql = "SELECT user_id, username FROM skineasy_users"
        cur.execute(sql)   
        return cur.fetchall()


    
###################################################################################################
# 3) ROUTINE TABLE functions
###################################################################################################

# ****************************************************
# Function to get all routine table entries as JSON
# ****************************************************
def get_routines_json():

    with get_db_cursor() as cur:
        
        # Make SQL statement asking database for all entries in users table
        sql = "SELECT row_to_json(skineasy_routines) FROM skineasy_routines ORDER BY user_id ASC"
        cur.execute(sql)   
        return cur.fetchall()


# ****************************************************
# Function to get user id based on username string
# ****************************************************
def get_user_id_from_username(username):

    with get_db_cursor(True) as cur:
        get_user_sql = "SELECT %s FROM %s WHERE %s = '%s'" % ('user_id', 'skineasy_users', 'username', username)
        cur.execute(get_user_sql)
        user_id = cur.fetchall()[0][0]
        return user_id


# ****************************************************
# Function to get product id based on product name string
# ****************************************************
def get_product_id_from_product_name(product_name):

    with get_db_cursor(True) as cur:
        get_product_sql = "SELECT %s FROM %s WHERE %s = '%s'" % ('product_id', 'skineasy_skincare_products', 'product_name', product_name)
        cur.execute(get_product_sql)
        product_id = cur.fetchall()[0][0]
        return product_id


# ****************************************************
# Function to add an entry to routines table given a dictionary with username and product name
# ****************************************************
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
# Function to add an entry to routines table given a dictionary with username and product name
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
# Function to get a user's respective routine products
# ****************************************************
def get_user_routine(username):
    with get_db_cursor(True) as cur:

        # Using the username string, get JSON of all products via routines table that have right user ID
        user_id = get_user_id_from_username(username)

        # Get all product IDs that are associated with user's ID
        # * Reference on SQL joining w/ WHERE clause: https://mode.com/sql-tutorial/sql-joins-where-vs-on/
        get_user_products_sql = '''
            SELECT row_to_json(skineasy_skincare_products)
            FROM skineasy_skincare_products
            INNER JOIN skineasy_routines ON skineasy_routines.product_id = skineasy_skincare_products.product_id
            WHERE skineasy_routines.user_id = %s;
            ''' % user_id

        cur.execute(get_user_products_sql)
        return cur.fetchall()
        

# ********************************************************************************************************
# Function to get a get a specific product type based on type (string) and username (string)
# ********************************************************************************************************
def get_user_routine_by_type(product_type=None, username=None):
    with get_db_cursor(True) as cur:

        # Ensure inputs don't cause an internal server error
        if ((username is None)):
            current_app.logger.info("Error: get_user_routine_type - Function inputs invalid.")
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

# ****************************************************
# Function to get all reviews from the review table as JSON
# ****************************************************
def get_reviews_json():
    ''' note -- result can be used as list of dictionaries'''
    with get_db_cursor() as cur:

        # Make SQL statement asking database for all entries in reviews table
        sql = "SELECT row_to_json(skineasy_reviews) FROM skineasy_reviews ORDER BY review_id ASC"
        cur.execute(sql)

        return cur.fetchall()
    

# ****************************************************
# Function to add a review to the review table
# ****************************************************
def add_review(user_details, content, product_id, rating):
    with get_db_cursor(True) as cur: 
   
        # Only add review if user has a username
        # Reference to check if a key exists within a python dict: https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
        if ('nickname' in user_details):
            user = user_details['nickname']

            # Get user_ids from users table to add to the review table 
            usersID_and_names = get_all_user_ids_and_names()

            # Iterate list and find user_id corresponding to user's name
            for item in usersID_and_names:
                if item[1] == user:
                    user_id = item[0]

            # # # Build SQL statement with sessions object and user_id from users table 
            # # # Reference on PSQL insertion without duplicates: https://stackoverflow.com/questions/1009584/how-to-emulate-insert-ignore-and-on-duplicate-key-update-sql-merge-with-po
            sql = '''
                INSERT INTO skineasy_reviews (user_id, product_id, reviewer_name, content, rating)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_id, product_id, reviewer_name, content, rating) DO NOTHING;
                '''

            # # Execute sql statement with default data
            cur.execute(sql, (user_id, product_id, user, content, rating))


# ****************************************************
# Function to show all reviews for a certain product
# ****************************************************
def get_all_reviews_for_product(product_id):
    with get_db_cursor(True) as cur: 
   
        # # # Build SQL statement to get all reviews for a product with the product_id
        sql = '''
            SELECT * 
            FROM skineasy_reviews 
            WHERE product_id = %s
            '''
        # # Execute sql statement with default data
        cur.execute(sql, product_id)
        return cur.fetchall()


# ****************************************************
# Function to show all reviews written by a specific user
# ****************************************************
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