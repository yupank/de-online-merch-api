import pytest
from src.api.routes import get_products, get_categories,  get_product,\
    get_user_average_spend, process_query, get_db_connection, \
    get_users, get_user_by_id, get_user_sales, get_user_sales_latest, \
    get_products_for_category,\
    DBConnectionException
from unittest.mock import patch
from flask import Flask, jsonify
from src.data.sql import query_strings
from data import sample_data, sample_data_unsorted, categories_result,\
    users_result, products_result, multiple_sales,\
    sample_headers, sample_result, products_expected, single_sale


def db_data(query):
    if query == 'test query':
        return sample_data
    elif query == 'test query unsorted':
        return sample_data_unsorted
    elif query == query_strings['categories']:
        return categories_result
    elif query == query_strings['products']:
        return products_expected
    return []


def dummy_process(query):
    if query == query_strings['categories']:
        return jsonify(categories_result)
    elif query == query_strings['products']:
        return jsonify(products_expected)
    elif query == query_strings['all_users']:
        return jsonify(users_result)


def db_data_params(query, **params):
    if query == 'test params' :
        return sample_data
    return []


@pytest.fixture
def app_context():
    app = Flask(__name__)
    with app.app_context():
        yield


@pytest.fixture
def mock_env():
    env_vars = {
        'DB_HOST': 'abc',
        'DB_PORT': '5432',
        'DB_USER': 'def',
        'DB_PASSWORD': 'password',
        'DB_DB': 'db'
    }
    with patch.dict('os.environ', env_vars) as mock_env:
        yield mock_env


@patch('src.api.routes.Connection', autospec=True)
def test_get_db_creates_connection(mock_conn, mock_env, app_context):
    get_db_connection()
    mock_conn.assert_called_with(
        host='abc',
        user='def',
        port='5432',
        password='password',
        database='db'
    )


def test_get_db_raises_error_on_incorrect_connection(mock_env, app_context):
    with pytest.raises(DBConnectionException):
        get_db_connection()


def test_process_query_returns_correct_dict_array(app_context):
    with patch('src.api.routes.get_db_connection') as mock_conn:
        mock_conn().run.side_effect = db_data
        mock_conn().columns = sample_headers
        result = process_query('test query')
        assert result.json == sample_result

def test_process_query_returns_sorted_dict_array(app_context):
    with patch('src.api.routes.get_db_connection') as mock_conn:
        mock_conn().run.side_effect = db_data
        mock_conn().columns = sample_headers
        result = process_query('test query unsorted')
        assert result.json == sample_result

def test_process_query_works_with_parameters(mock_env, app_context):
    with patch('src.api.routes.Connection', autospec=True) as mock_conn:
        mock_conn().columns = sample_headers
        mock_conn().run.side_effect = db_data_params
        result = process_query('test params', param1='x')
        assert result.json == sample_result
        mock_conn().run.assert_called_once_with('test params', param1='x')

def test_process_query_returns_empy_if_id_does_not_exists(app_context):
    with patch('src.api.routes.get_db_connection') as mock_conn:
        mock_conn().run.side_effect = db_data_params
        mock_conn().columns = sample_headers
        result = process_query('test users', user_id=3)
        assert result.json == []

def test_get_categories_returns_categories(app_context):
    with patch('src.api.routes.process_query',
               side_effect=dummy_process):
        result = get_categories()
        assert result.json == categories_result

def test_get_products_returns_products(app_context):
    with patch('src.api.routes.process_query',
               side_effect=dummy_process):
        result = get_products()
        assert result.json == products_expected


def test_get_user_average_calculates_average_one_purchase(app_context):
    patch_return = jsonify(single_sale)
    with patch('src.api.routes.process_query',
               return_value=patch_return) as mock_process:
        expected = {"user": 10, "average_spend": 101.00}
        expected_query = query_strings['sales_average']
        result = get_user_average_spend(10)
        mock_process.assert_called_with(expected_query, user_id=10)
        assert result.json == expected


def test_get_user_average_correctly_calculates_average(app_context):
    patch_return = jsonify(multiple_sales)
    with patch('src.api.routes.process_query',
               return_value=patch_return):
        expected = {"user": 10, "average_spend": 95.67}
        result = get_user_average_spend(10)
        assert result.json == expected

def test_get_user_average_returs_error_message_for_wrong_id(app_context):
    patch_return = jsonify([])
    with patch('src.api.routes.process_query',
               return_value=patch_return):
        expected = {"user": 100, "query_error": "User does not exist"}
        result = get_user_average_spend(100)
        assert result.json == expected

def test_get_users_returns_users(app_context):
    with patch('src.api.routes.process_query',
               side_effect=dummy_process):
        result = get_users()
        assert result.json == users_result

def test_get_user_by_id_returns_correct_data(app_context):
    patch_return = jsonify(users_result[1])
    with patch('src.api.routes.process_query',
               return_value=patch_return) as mock_process:
        expected = {
            "id": 2,
            "first_name": "Jane",
            "last_name": "Jones"
        }
        expected_query = query_strings['user_by_id']
        result = get_user_by_id(2)
        mock_process.assert_called_with(expected_query, user_id=2)
        assert result.json == expected

def test_get_user_by_id_returns_error_message(app_context):
    patch_return = jsonify([])
    with patch('src.api.routes.process_query',
               return_value=patch_return) as mock_process:
        expected = {"id": 3,"query_error": "User does not exist"}
        expected_query = query_strings['user_by_id']
        result = get_user_by_id(3)
        mock_process.assert_called_with(expected_query, user_id=3)
        assert result.json == expected

def test_get_product_returns_correct_data(app_context):
    patch_return = jsonify(products_result[1])
    with patch('src.api.routes.process_query',
               return_value=patch_return) as mock_process:
        expected = { "id": 7,
                    "title": "Sausages",
                    "description": "Tasty",
                    "cost": 978.00,
                    "categoryId": 1
        }
        expected_query = query_strings['product_by_id']
        result = get_product(7)
        mock_process.assert_called_with(expected_query, product_id=7)
        assert result.json == expected

def test_get_product_returns_error_message_for_wrong_id(app_context):
    patch_return = jsonify([])
    with patch('src.api.routes.process_query',
               return_value=patch_return) as mock_process:
        expected = { "id": 77, "query_error": "Product does not exist"}
        expected_query = query_strings['product_by_id']
        result = get_product(77)
        mock_process.assert_called_with(expected_query, product_id=77)
        assert result.json == expected

def test_get_user_sales_returns_correct_data(app_context):
    patch_return = jsonify(multiple_sales)
    with patch('src.api.routes.process_query',
               return_value=patch_return) as mock_process:
        expected = multiple_sales
        expected_query = query_strings['user_sales']
        result = get_user_sales(2,'2022-11-11','2023-02-02')
        mock_process.assert_called_with(expected_query, user_id=2,date_from='2022-11-11', date_to='2023-02-02')
        assert result.json == expected

def test_get_user_sales_returs_error_message_for_wrong_user_id(app_context):
    patch_return = jsonify({"id": 100, "query_error": "User does not exist"})
    with patch('src.api.routes.get_user_by_id',
               return_value=patch_return):
        expected = {"user_id": 100, "query_error": "User does not exist"}
        result = get_user_sales(100,'2022-11-11','2023-02-02')
        assert result.json == expected


def test_get_user_sales_returns_empty_if_no_sales(app_context):
    with patch('src.api.routes.process_query',
               return_value=jsonify([])) as mock_process:
        with patch('src.api.routes.get_user_by_id', return_value = jsonify({"user_id":2,"user_data":[]})):
            expected = []
            expected_query = query_strings['user_sales']
            result = get_user_sales(2,'2023-11-11','2024-02-02')
            mock_process.assert_called_with(expected_query, user_id=2,date_from='2023-11-11', date_to='2024-02-02')
            assert result.json == expected

def test_get_user_sales_latest_returns_correct_data(app_context):
    patch_return = jsonify(multiple_sales)
    with patch('src.api.routes.process_query',
               return_value=patch_return) as mock_process:
        expected = multiple_sales
        expected_query = query_strings['user_sales_latest']
        result = get_user_sales_latest(2)
        mock_process.assert_called_with(expected_query, user_id=2)
        assert result.json == expected

def test_get_user_sales_returs_error_message_for_wrong_user_id(app_context):
    patch_return = jsonify({"id": 100, "query_error": "User does not exist"})
    with patch('src.api.routes.get_user_by_id',
               return_value=patch_return):
        expected = {"user_id": 100, "query_error": "User does not exist"}
        result = get_user_sales_latest(100)
        assert result.json == expected

def test_get_products_for_category_returns_correctly(app_context):
    with patch('src.api.routes.process_query',
               side_effect=dummy_process):
        assert get_products_for_category("Movies") == [products_expected[0],products_expected[2]]
        assert get_products_for_category("Baby") == [products_expected[1]]

def test_get_products_for_category_sorts_correctly(app_context):
    with patch('src.api.routes.process_query',
               side_effect=dummy_process):
        assert get_products_for_category("Movies",sort='id') == [products_expected[2],products_expected[0]]
