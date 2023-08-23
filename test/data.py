"""Data for test cases."""
categories_result = [
    {
        "id": 1,
        "name": "Baby"
    },
    {
        "id": 2,
        "name": "Movies"
    }
]

users_result = [
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

products_result = [
    {
        "id": 5,
        "title": "Car",
        "description": "Nice",
        "cost": 101.00,
        "categoryId": 2
    },
    {
        "id": 7,
        "title": "Sausages",
        "description": "Tasty",
        "cost": 978.00,
        "categoryId": 1
    }
]

products_expected = [
    {
        "id": 5,
        "title": "Car",
        "description": "Nice",
        "cost": 101.00,
        "category": "Movies"
    },
    {
        "id": 7,
        "title": "Sausages",
        "description": "Tasty",
        "cost": 978.00,
        "category": "Baby"
    },
    {
        "id": 3,
        "title": "Sausage Party",
        "description": "vicked",
        "cost": 8.00,
        "category": "Movies"
    }
]


sample_data = [['a', 'b', 'c'], ['d', 'e', 'f']]
sample_data_unsorted = [['d', 'e', 'f'],['a', 'b', 'c']]

sample_headers = [{'name': 'id'}, {'name': 'col2'}, {'name': 'col3'}]


sample_result = [
    {
        "id": 'a',
        "col2": 'b',
        "col3": 'c'
    },
    {
        "id": 'd',
        "col2": 'e',
        "col3": 'f'
    }
]


single_sale = [
    {'id': 1, 'productId': 1, 'cost': 101.0, 'user': '10'}
]

multiple_sales = [
    {'id': 1, 'productId': 1, 'cost': 125.0, 'user': '10'},
    {'id': 1, 'productId': 1, 'cost': 65.0, 'user': '10'},
    {'id': 1, 'productId': 1, 'cost': 97.0, 'user': '10'}
]
