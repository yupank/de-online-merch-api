"""The API entry point for the Flask API.

The API server is started by running this file directly
from Python. The API is specified in the OpenAPI file
swagger.yml in this directory. The routes are defined by
the Connexion library in routes.py.

Run:
    python src/api/app.py
from the root directory.

Then navigate to localhost:8000/api/ui to see the API documentation,
or navigate to localhost:8000/api/<route> to see an API request result.
"""
import connexion
import logging
from routes import get_categories, get_products_for_category
from dotenv import load_dotenv
from flask import render_template

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

PORT = 8000

app = connexion.App(__name__, specification_dir="./")
app.add_api('swagger.yml')

@app.route("/")
def home():
    categories = get_categories().json
    for category in categories:
        category['products'] = get_products_for_category(category['name'])
    return render_template("home.html",categories=categories)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT, debug=True)
