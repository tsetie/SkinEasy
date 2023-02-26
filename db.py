""" database access
docs:
* http://initd.org/psycopg/docs/
* http://initd.org/psycopg/docs/pool.html
* http://initd.org/psycopg/docs/extras.html#dictionary-like-cursor
"""

from contextlib import contextmanager
import logging
import os

from flask import current_app, g

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

# Connection pool
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


# Function to add a survey response into PSQL database
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

# Function to get skincare products from table
def get_skincare_products_json():
    ''' note -- result can be used as list of dictionaries'''
    with get_db_cursor() as cur:
        # cur.execute("select * from person order by person_id limit %s offset %s", (limit, offset))
        
        sql = "SELECT row_to_json(skineasy_skincare_products) FROM skineasy_skincare_products ORDER BY product_id ASC"
        cur.execute(sql)   

        return cur.fetchall()

# Function to get skincare based on product type
def filter_by_product_type(is_cleanser, is_toner, is_serum, is_moisturizer, is_sunscreen):
    ''' note -- result can be used as list of dictionaries'''
    with get_db_cursor() as cur:        
        sql = """
            SELECT row_to_json(skineasy_skincare_products) 
            FROM skineasy_skincare_products 
            WHERE is_cleanser IS TRUE OR is_toner IS TRUE OR is_serum IS TRUE OR is_moisturizer IS TRUE OR is_sunscreen IS TRUE;
            """

        cur.execute(sql)    
        return cur.fetchall()


# Function to get skincare products based on skin type
def filter_by_skin_type(sensitive_skin, mature_skin, normal_skin):
    ''' note -- result can be used as list of dictionaries'''
    with get_db_cursor() as cur:        
        sql = """
            SELECT row_to_json(skineasy_skincare_products) 
            FROM skineasy_skincare_products 
            WHERE sensitive_skin IS TRUE OR mature_skin IS TRUE OR normal_skin IS TRUE;
            """

        cur.execute(sql)    
        return cur.fetchall()

# Function to get skincare products based on skincare brand
def filter_by_brand(product_brand_input):
    ''' note -- result can be used as list of dictionaries'''
    with get_db_cursor() as cur:        
        sql = """
            SELECT row_to_json(skineasy_skincare_products) 
            FROM skineasy_skincare_products 
            WHERE product_brand = product_brand_input;
            """

        cur.execute(sql)    
        return cur.fetchall()