-- 1) Create table for skin care products
CREATE TABLE skineasy_skincare_products (
    product_id       serial primary key NOT NULL,
    product_name     varchar(255) NOT NULL,
    product_url      varchar(255) NOT NULL,
    product_brand    varchar(255) NOT NULL,

    image_path       varchar(255) NOT NULL,

    cleanser         boolean,
    exfoliant        boolean,
    toner            boolean,
    serum            boolean,
    moisturizer      boolean,
    sunscreen        boolean,

    sensitive_target boolean,
    mature_target    boolean,
    none_target      boolean,

    normal_skin      boolean,
    oily_skin        boolean,
    dry_skin         boolean,
    is_all           boolean
);


-- Insert product into skincare products table
INSERT INTO skineasy_skincare_products (product_name, product_url, product_brand, cleanser, exfoliant, toner, serum, moisturizer, sunscreen, sensitive_target, mature_target, none_target, normal_skin, oily_skin, dry_skin, is_all)
VALUES                                 (product_name, product_url, product_brand, is_cleanser, is_exfoliant, is_toner, is_serum, is_moisturizer, is_sunscreen, for_sensitive_skin, for_mature_skin, no_target, for_normal, for_oily, for_dry, for_all);

-- Insert new data into table (with NO specified columns)
INSERT INTO skincare_products
VALUES (product_name, product_url, product_brand, is_cleanser, is_exfoliant, is_toner, is_serum, is_moisturizer, is_sunscreen, for_sensitive_skin, for_mature_skin, no_target, for_normal, for_oily, for_dry, for_all);

-- Update existing table data
UPDATE skineasy_skincare_products
SET image_path = '/static/images/first-aid-beauty/first-aid-beauty-ultra-repair-cream-intense-hydration.png'
WHERE image_path = '/static/first-aid-beauty/first-aid-beauty-ultra-repair-cream-intense-hydration.png';


-- Remove products entry from skincare products table
DELETE FROM skineasy_skincare_products WHERE condition;

-- Deleting skincare products table
DROP TABLE IF EXISTS skineasy_skincare_products;




-- 2) Create table for users
CREATE TABLE IF NOT EXISTS skineasy_users (
    user_id          serial primary key NOT NULL,
    username         varchar(255),

    first_name       varchar(255),
    last_name        varchar(255),
    email            varchar(255),

    user_skin_type   varchar(255),
    user_target      varchar(255),

    routine_steps    int
);

-- 3) Routine/wishlist table
CREATE TABLE IF NOT EXISTS skineasy_routine_wishlist_id (
    ...
    ...
    ...
);


-- 4) Review table
CREATE TABLE IF NOT EXISTS skineasy_product_reviews_id (
    ...
    ...
    rating           int,
    review_msg       varchar(255)
  
);




-- psycopg2 connections
-- Connect to database from RENDER via PYTHON terminal: 
python

import os
os.environ["DATABASE_URL"]

import psycopg2
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()

-- # Example of making a table 'facts':
    * Would be helpful to have a schema.sql file for remembering SQL commands:

    create_script =  ''' CREATE TABLE IF NOT EXISTS facts ( id serial primary key, source text, content text); '''
    cur.execute(create_script)
    conn.commit()

-- # Example of selecting from a table 'facts'
    * Assumes there is a table that exists in the database
    
    cur.execute('select * from facts')
    cur.fetchall()
        * Should show some contents of the facts table


-- # If you run into some weird error where your terminal gets stuck w/ same error message:
    cur.execute('ROLLBACK')
    conn.commit()

-- Close connection
    conn.close()




-- Printing out database table names
-- Show all tables via python connection cursor:
cur.execute("""SELECT table_name FROM information_schema.tables
       WHERE table_schema = 'public'""")
for table in cur.fetchall():
    print(table)

-- Show all contents of table
cur.execute('select * from skineasy_skincare_products')
cur.fetchall()