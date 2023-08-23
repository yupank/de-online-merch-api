"""Defines the functionality for the API routes.

Each route is invoked by the Connexion library from the
OperationId parameter included in the OpenAPI specification.

Classes:
    DBConnectionException: custom exception for database issues.
    Query strings are stored in data/sql.py.

Functions:
    get_db_connection: returns pg8000 Native Connection.
    process_query: helper function to execute supplied SQL.
    get_categories: handles the /categories route.
    get_products: handles the /products route.
    get_product: handles the /products/{product_id} route.
    get_users: handles the /users route.
    get_user_sales: handles the /users/{user_id}/sales route.
    get_user_sales_latest: handles the /users/{user_id}/sales/latest route.
    get_user_average_spend: handles the /users/{user_id}/average_spend route

"""
from pg8000.native import Connection, Error, DatabaseError
from flask import jsonify, abort
from src.data.sql import query_strings
import os


class DBConnectionException(Exception):
    """Wraps pg8000.native Error or DatabaseError."""

    def __init__(self, e):
        """Initialise with provided error message."""
        self.message = str(e)
        super().__init__(self.message)


def get_db_connection():
    """Gets a pg8000.native Connection to the database.

    Credentials are retrieved from environment variables.

    Returns:
        (pg8000.native.Connection): a database connection

    Raises:
        DBConnectionException
    """
    try:
        DB_HOST = os.environ['DB_HOST']
        DB_PORT = os.environ['DB_PORT']
        DB_USER = os.environ['DB_USER']
        DB_PASSWORD = os.environ['DB_PASSWORD']
        DB_DB = os.environ['DB_DB']
        return Connection(
            host=DB_HOST,
            user=DB_USER,
            port=DB_PORT,
            password=DB_PASSWORD,
            database=DB_DB
        )
    except (Error, DatabaseError) as e:
        raise DBConnectionException(e)


def process_query(query, **kwargs):
    """Gets a connection, executes a query, closes connection.

    Pass in a valid query string and any query parameters.

    Args:
        query (string): a valid SQL query.

    Keyword Arguments:
        kwargs: a tuple of SQL parameters e.g. user_id=3

    Returns:
        (Response) a response containing jsonified query results, 
        if sql database response is empty, returns  empty jsonified list

        Example:
        [
            {"category_id": 3, "category_name": "Books"},
            {"category_id": 7, "category_name": "Movies"}
        ]

    Raises:
        RuntimeError
    """

    try:
        conn = get_db_connection()
        result = conn.run(query, **kwargs)
        columns = [c['name'] for c in conn.columns]
    except DBConnectionException as e:
        raise RuntimeError(e)
    finally:
        conn.close()
    result_dict = [dict(zip(columns, r)) for r in result]
    if len(result_dict) > 0:
        result_sorted = sorted(result_dict, key=lambda r: r['id']) if 'id' in result_dict[0] else result_dict
    else:
        result_sorted = result_dict
    return jsonify(result_sorted)

def get_categories():
    """Gets list of all product categories.

    If no categories, returns empty list.

    Returns:
       (Response) Result of query.

        Example:
        [
            {
                "id": 1,
                "name": "Baby"
            },
            {
                "id": 2,
                "name": "Movies"
            }
        ]
    """
    query = query_strings['categories']
    return process_query(query)

def create_category(category):
    """ Creates new category - NOT IMPLEMENTED """
    # print(f"check: {category}")
    return {"response":200, "message":"successfully created category"}

def get_products():
    """Gets list of all products with named category.

    If no products, returns empty list.

    Returns:
        (Response) Result of query.

        Example:
        [
            {
                "id": 5,
                "title": "Car",
                "description": "Nice",
                "cost": 101.00,
                "category": "Movies"
            }
        ]
    """
    query = query_strings['products']
    return process_query(query)

def get_products_for_category(category_name, sort='title'):
    """ Gets list of products for specified category name 
        This is a utility function for diplaying product catalog
        Args:
            category_name (String)
            sort - whether to sort by title (default) or by id
        Returns
            list of products
    """
    product_list = [product for product in get_products().json if product['category'] == category_name ]
    if len(product_list) > 1:
        if sort == 'title' and 'title' in product_list[0]:
            return sorted(product_list, key=lambda r: r['title'])
        if sort == 'id' and 'id' in product_list[0]:
            return sorted(product_list, key=lambda r: r['id'])
    return product_list

def get_user_average_spend(user_id):
    """Gets average purchase value for a given user.

    Aggregates all sales to a given user and averages cost. If
    no sales for user, return zero. If user does not exist, return
    error message

    Args:
        user_id (int): the id of the user.

    Returns:
        (Response): Result of query.
        Examples:
        {"user": 10, "average_spend": 101.00}
        {"user": 975, "query_error": "User does not exist"}
    """
    user_check = get_user_by_id(user_id)
    if 'query_error' in user_check.json:
        return jsonify({"user": user_id, "query_error": "User does not exist"})
    query = query_strings['sales_average']
    sales = process_query(query, user_id=user_id)
    spends = [s['cost'] for s in sales.json]
    total = 0
    count = 0
    for spend in spends:
        total += spend
        count += 1
    return jsonify({
        "user": user_id,
        "average_spend": round(total / count, 2)
    })


def get_product(product_id):
    """Gets details of specific product 

    Returns details of specific product. If no such product,
    returns error response.

    Args:
        product_id (int): the identifier for the product.
    Returns:
        (Response) Result of query (if id exists) or error message

        Example:
        {
            "id": 5,
            "title": "Car",
            "description": "Nice",
            "cost": 101.00,
            "category": "Movies"
        }
        {"id": 111, "query_error": "Product does not exist"}
    """
    query = query_strings['product_by_id']
    product_data = process_query(query, product_id=product_id)
    if len(product_data.json) > 0:
        return product_data
    else:
        return jsonify({"id": product_id, 
                        "query_error": "Product does not exist"})
        # abort(404, {"id": product_id, 
        #            "query_error": "Product does not exist"})


def get_users():
    """Gets list of all users.

    Returns list of users excluding important contact details,
    for example email and phone number. If no users, returns
    empty list.

    Returns:
        (Response) Result of query.

        Example:
        [
            {
                "id": 1,
                "first_name": "John",
                "last_name": "Smith"
            },
            {
                "id": 2,
                "first_name": "Jane",
                "last_name": "Jones"
            }
        ]
    """
    query = query_strings['all_users']
    return process_query(query)

def get_user_by_id(user_id):
    """ Gets details of specific user, excluding important contact details 
        
        Args : user_id(int) - user identifier

        Returns:
        (Response) Result of query. 
        If no such user, returns error response
        Examples:
        user_id=1 : {"id": 1, "first_name": "John", "last_name": "Smith"}
        user_id=111: {"id": 111, "query_error": "User does not exist"}
    """
    query = query_strings['user_by_id']
    user_data = process_query(query, user_id=user_id)
    if len(user_data.json) > 0:
        return user_data
    else:
        return jsonify({"id": user_id, 
                        "query_error": "User does not exist"})
    

def get_user_sales(user_id, date_from, date_to):
    """Gets sales for specific user between two dates .

    Returns error response if user does not exist. Returns
    empty list if no sales in date range. (Data is available between
    1/9/2022 - 23/1/2023).

    Args:
        user_id (int): valid user identifier
        date_from (str): date in format yyyy-mm-dd
        date_to (str): date in format yyyy-mm-dd

    Returns:
        (Response) Result of query, or
        (Response) Error response.
        Examples:
        [
            {'user_id': 5, 'sales_id': 14, 'product_id': 14,
            'Category': 'Movies', 'product_title': 'Awesome',
            'transaction_ts': '2023-01-23 12:17:01.181', 'Cost': 19:52},
            {'user_id': 5, 'sales_id': 272, 'product_id': 3,
            'Category': 'Books', 'product_title': 'Wow',
            'transaction_ts': '2023-01-02 01:17:01.181', 'Cost': 7.47}
        ]
        {'user_id': 789, 'query_error': 'User does not exist'}
    """

    user_check = get_user_by_id(user_id)
    if 'query_error' in user_check.json:
        return jsonify({"user_id": user_id, "query_error": "User does not exist"})
    query = query_strings['user_sales']
    sales_data = process_query(query, user_id=user_id, date_from=date_from, date_to=date_to)   
    return sales_data


def get_user_sales_latest(user_id):
    """Gets latest sales for user up to maximum of five.

    Returns error response if user does not exist. Returns
    empty list if no sales in date range. (Data is available between
    1/9/2022 - 23/1/2023).

    Args:
        user_id (int): valid user identifier

    Returns:
        (Response) Result of query, or
        (Response) Error response.
        Examples:
        [
            {'user_id': 5, 'sales_id': 14, 'product_id': 14,
            'Category': 'Movies', 'product_title': 'Awesome',
            'transaction_ts': '2023-01-23 12:17:01.181', 'Cost': 19:52},
            {'user_id': 5, 'sales_id': 272, 'product_id': 3,
            'Category': 'Books', 'product_title': 'Wow',
            'transaction_ts': '2023-01-02 01:17:01.181', 'Cost': 7.47}
        ]
        {'user_id': 789, 'query_error': 'User does not exist'}
    """
    user_check = get_user_by_id(user_id)
    if 'query_error' in user_check.json:
        return jsonify({"user_id": user_id, "query_error": "User does not exist"})
    query = query_strings['user_sales_latest']
    sales_data = process_query(query, user_id=user_id)   
    return sales_data