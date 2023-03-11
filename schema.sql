-------------------------------------------
-- 1) Create table for skin care products
-------------------------------------------
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
    is_all           boolean,

    price            money,
    num_reviews      integer,
    average_rating   numeric
);


-- Insert product into skincare products table
INSERT INTO skineasy_skincare_products (product_name, product_url, product_brand, cleanser, exfoliant, toner, serum, moisturizer, sunscreen, sensitive_target, mature_target, none_target, normal_skin, oily_skin, dry_skin, is_all)
VALUES                                 (product_name, product_url, product_brand, is_cleanser, is_exfoliant, is_toner, is_serum, is_moisturizer, is_sunscreen, for_sensitive_skin, for_mature_skin, no_target, for_normal, for_oily, for_dry, for_all);


-- Insert new data into table (with NO specified columns)
INSERT INTO skincare_products
VALUES (product_name, product_url, product_brand, is_cleanser, is_exfoliant, is_toner, is_serum, is_moisturizer, is_sunscreen, for_sensitive_skin, for_mature_skin, no_target, for_normal, for_oily, for_dry, for_all);


-- Update existing table data
UPDATE skineasy_skincare_products
SET product_name = 'Drunk Elephant Protini Polypeptide Cream'
WHERE product_name = 'Drunk Elephant Protini Polypeptide Cream ';


-- Add a new column to table
ALTER TABLE skineasy_skincare_products 
ADD COLUMN num_reviews integer,
ADD COLUMN average_rating numeric;

-- Remove products entry from skincare products table
DELETE FROM skineasy_skincare_products WHERE condition;


-- Deleting skincare products table
DROP TABLE IF EXISTS skineasy_skincare_products;



------------------------------------------------------------
-- 2) Create table for users
------------------------------------------------------------
CREATE TABLE skineasy_users (
    user_id          serial NOT NULL,
    username         varchar(255) UNIQUE NOT NULL,
    email            varchar(255) UNIQUE NOT NULL,

    user_skin_type   varchar(255),
    user_target      varchar(255),
    routine_steps    integer,

    PRIMARY KEY(user_id),
    UNIQUE(username, email)
);


-- Add a user to users table
INSERT INTO skineasy_users (username, email, user_skin_type, user_target, routine_steps)
VALUES (username, email, user_skin_type, user_target, routine_steps)


-- Example of adding to users table
INSERT INTO skineasy_users (username, email, user_skin_type, user_target, routine_steps)
VALUES ('example_username', 'example_email@gmail.com', '', '', 4)


-- Another format to add to users table
INSERT INTO skineasy_users (
    username,
    email, 
    user_skin_type,
    user_target,
    routine_steps
) VALUES (%s, %s, %s, %s, %s)



------------------------------------------------------------
-- 3) Routine/wishlist table
------------------------------------------------------------
CREATE TABLE skineasy_routines (
    routine_id      serial  NOT NULL,
    user_id         integer NOT NULL,
    product_id      integer NOT NULL,
    published_date  timestamp DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY(routine_id),

    CONSTRAINT user_id
        FOREIGN KEY (user_id)
        REFERENCES skineasy_users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT product_id
        FOREIGN KEY (product_id)
        REFERENCES skineasy_skincare_products(product_id)
        ON DELETE CASCADE,

    UNIQUE(user_id, product_id)
);



------------------------------------------------------------
-- 4) Review table
------------------------------------------------------------
CREATE TABLE skineasy_reviews (
    review_id       serial  NOT NULL,
    user_id         integer NOT NULL,
    product_id      integer NOT NULL,
    reviewer_name   varchar(255) NOT NULL,
    title           varchar (255),
    content         varchar(255),
    rating          integer NOT NULL,
    published_date  timestamp DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (review_id),

    CONSTRAINT user_id
        FOREIGN KEY (user_id)
        REFERENCES skineasy_users(user_id)
        ON DELETE CASCADE,
    
    CONSTRAINT product_id
        FOREIGN KEY (product_id)
        REFERENCES skineasy_skincare_products(product_id)
        ON DELETE CASCADE,

    UNIQUE(user_id, product_id)
);


-------------------------------------------------------------------
-- A) Viewing database table contents
-------------------------------------------------------------------
-- View ALL database table names
cur.execute("""SELECT table_name FROM information_schema.tables
       WHERE table_schema = 'public'""")
for table in cur.fetchall():
    print(table)


-- View ALL columns of a table
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'skineasy_reviews';


-- Show all contents of table
cur.execute('select * from skineasy_users')
cur.fetchall()


-- Show ALL primary keys of every table in database
SELECT conrelid::regclass AS table_name,
       conname AS primary_key, 
       pg_get_constraintdef(oid) 
FROM   pg_constraint 
WHERE  contype = 'p' 
AND    connamespace = 'public'::regnamespace   
ORDER  BY conrelid::regclass::text, contype DESC;



---------------------------------------------------------
-- B) psycopg2 connections
-- Connect to database from RENDER via PYTHON terminal:
---------------------------------------------------------
pipenv run python

-- Python connection to db paste
import os
os.environ["DATABASE_URL"]
import psycopg2
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()

-- Would be helpful to have a schema.sql file for remembering SQL commands:
create_script =  ''' CREATE TABLE IF NOT EXISTS facts ( id serial primary key, source text, content text); '''
cur.execute(create_script)
conn.commit()

-- Example of selecting from a table 'facts'
-- * Assumes there is a table that exists in the database
-- * Should show some contents of the facts table
cur.execute('select * from facts')
cur.fetchall()

-- End of black error paste:
cur.execute('ROLLBACK')
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()

-- Close connection
conn.close()


-- Try to get products via
'''
SELECT skincare_routines.product_id
FROM skincare_routines
INNER JOIN skincare_products ON skincare_routines.product_id = skincare_products.product_id;
'''


SELECT row_to_json(skineasy_skincare_products)
FROM skineasy_skincare_products
INNER JOIN skineasy_routines 
ON skineasy_routines.user_id = 4
-- ORDER BY payment_date;