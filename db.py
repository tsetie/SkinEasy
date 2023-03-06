""" database access
docs:
* http://initd.org/psycopg/docs/
* http://initd.org/psycopg/docs/pool.html
* http://initd.org/psycopg/docs/extras.html#dictionary-like-cursor
"""


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


#################################
# Connection pool setup
#################################
# Global connection variable
pool = None

# Connection pool to setup
def setup():
    global pool
    DATABASE_URL = os.environ['DATABASE_URL']
    current_app.logger.info(f"creating db connection pool")
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


#################################
# PRODUCTS TABLE functions
#################################

# Function to add a product to skincare products table
def add_skincare_product(product_name, product_url, product_brand, image_path, cleanser=False, exfoliant=False, toner=False, serum=False, moisturizer=False, sunscreen=False, sensitive_target=False, mature_target=False, no_target=False, normal_skin=False, oily_skin=False, dry_skin=False, is_all=False):
    # Since we're using connection pooling, it's not as big of a deal to have
    # lots of short-lived cursors (I think -- worth testing if we ever go big)
    with get_db_cursor(True) as cur:
        current_app.logger.info("Adding entry to skincare products table")

        # Build SQL insertion statement
        sql = """
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
            """
        # Execute sql insertion
        cur.execute(sql, (product_name, product_url, product_brand, image_path, cleanser, exfoliant, toner, serum, moisturizer, sunscreen, sensitive_target, mature_target, no_target, normal_skin, oily_skin, dry_skin, is_all))


# Function to get all skincare products from skincare products table
def get_skincare_products_json():
    ''' note -- result can be used as list of dictionaries'''
    with get_db_cursor() as cur:

        # Make SQL statement asking database for all entries in products table
        sql = "SELECT row_to_json(skineasy_skincare_products) FROM skineasy_skincare_products ORDER BY product_id ASC"
       
        cur.execute(sql)   
        return cur.fetchall()


# Function to get skincare products based on filter tags
def filter_products(num_filters=0, cleanser_filter=False, exfoliant_filter=False, toner_filter=False, serum_filter=False, moisturizer_filter=False, sunscreen_filter=False):
    ''' note -- result can be used as list of dictionaries'''
    with get_db_cursor(True) as cur:    
        
        # *Build a PSQL WHERE clause based on filters
        # If any filters are to be applied, set up a WHERE clause
        where_clause = ""
        
        # If there is at least one filter to be applied, set up WHERE clause format
        if (num_filters >= 1):
            where_clause += "WHERE %s"

        # For any additional filters, begin to use "OR" statement in WHERE clause
        for i in range(1, num_filters-1):
            where_clause += " OR %s" 
 
        # Add any filters to where clause in a python list --> python tuple
        data = []

        # Check passed in filters
        if (cleanser_filter):
            data.append("cleanser IS TRUE")

        if (exfoliant_filter):
            data.append("exfoliant IS TRUE")

        if (toner_filter):
            data.append("toner IS TRUE")

        if (serum_filter):
            data.append("serum IS TRUE")

        if (moisturizer_filter):
            data.append("moisturizer IS TRUE")

        if (sunscreen_filter):
            data.append("sunscreen IS TRUE")

        # Reference to convert lists to tuples: https://www.w3schools.com/python/python_tuples_update.asp
        data = tuple(data)
        
        # Fill where clause with data tuple
        where_clause = where_clause % data

        # Reference to use multi-line strings in python with parenthesis: https://stackoverflow.com/questions/5437619/python-style-line-continuation-with-strings
        # Reference to use "%s" in python: https://www.geeksforgeeks.org/what-does-s-mean-in-a-python-format-string/
        sql = (
            "SELECT row_to_json(skineasy_skincare_products) "
            "FROM skineasy_skincare_products "
            + where_clause
        )

        # Execute sql statement with data
        cur.execute(sql)
        return cur.fetchall()



#################################
# USER TABLE functions
#################################

# Function to add a user to the users table after they make an account
def add_user(user_details):
    with get_db_cursor(True) as cur: 
        
        # Only add user if provided a username and email
        # Reference to check if a key exists within a python dict: https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
        if (('nickname' in user_details) and ('email' in user_details)):
            user = user_details['nickname']
            email = user_details['email'] or None

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


# Function to get ALL USERS from the user table as JSON
def get_users_json():
    ''' note -- result can be used as list of dictionaries'''
    with get_db_cursor() as cur:
        
        # Make SQL statement asking database for all entries in users table
        sql = "SELECT row_to_json(skineasy_users) FROM skineasy_users ORDER BY user_id ASC"
        cur.execute(sql)   
        return cur.fetchall()


# Function to get 


#################################
# REVIEWS TABLE functions
#################################

# Function to add a review to a product
# Things to consider:
# 1) A user can only have a single review per product
# 2) A user should be able to edit their existing review
# 3) A user should be able to delete their review


# Function to get all users from the user table as JSON
def get_reviews_json():
    ''' note -- result can be used as list of dictionaries'''
    with get_db_cursor() as cur:

        # Make SQL statement asking database for all entries in reviews table
        sql = "SELECT row_to_json(skineasy_reviews) FROM skineasy_reviews ORDER BY review_id ASC"
        cur.execute(sql)   

        return cur.fetchall()