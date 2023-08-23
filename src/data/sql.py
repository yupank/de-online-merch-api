"""Contains SQL queries for routes."""
sales_average_sql = """select
    s.id,
    s."productId",
    p.cost,
    u.id as user
from sales s
inner join products p on s."productId" = p.id
inner join users u on s."buyerId" = u.id
where u.id = :user_id;"""

products_sql = """select
p.id,
p.title,
p.description,
p.cost,
c.name as category
from products p
inner join categories c on p."categoryId" = c.id;"""

product_by_id_sql = """select
p.id,
p.title,
p.description,
p.cost,
c.name as category
from products p
inner join categories c on p."categoryId" = c.id
WHERE p.id = :product_id;"""

user_sales_sql = """ WITH p_cat AS (SELECT 
p.id as product_id, p.title as product_title, p.cost as Cost, c.name as category 
FROM products p 
INNER JOIN categories c on p."categoryId" = c.id)
SELECT 
u.id as user_id, product_id, s.id as sales_id, transaction_ts,
product_title, Cost, p_cat.category
FROM sales s
INNER JOIN p_cat ON s."productId" = p_cat.product_id
INNER JOIN users u ON s."buyerId" = u.id
WHERE u.id = :user_id AND s.transaction_ts BETWEEN 
TO_DATE(:date_from,'YYYY-MM-DD') AND TO_DATE(:date_to,'YYYY-MM-DD');
"""

user_sales_latest_sql = """ WITH p_cat AS (SELECT 
p.id as product_id, p.title as product_title, p.cost as Cost, c.name as category 
FROM products p 
INNER JOIN categories c on p."categoryId" = c.id)
SELECT 
u.id as user_id, product_id, s.id as sales_id, transaction_ts,
product_title, Cost, p_cat.category
FROM sales s
INNER JOIN p_cat ON s."productId" = p_cat.product_id
INNER JOIN users u ON s."buyerId" = u.id
WHERE u.id = :user_id
ORDER BY transaction_ts DESC LIMIT 5;
"""


all_users_sql = "SELECT u.first_name, u.last_name, u.id from users u;"
user_by_id_sql = "SELECT u.first_name, u.last_name, u.id FROM users u WHERE u.id = :user_id;"

query_strings = {
    "categories": "SELECT * from categories;",
    "products": products_sql,
    "product_by_id": product_by_id_sql,
    "sales_average": sales_average_sql,
    "all_users": all_users_sql,
    "user_by_id": user_by_id_sql,
    "user_sales": user_sales_sql,
    "user_sales_latest": user_sales_latest_sql,
}
