# The Online-Merchandize API

This is RESTful API training project which uses the Flask framework.

IMPLEMENTED endpoints
- get/products/{product_id}
- get/users: 
- get/users/{user_id} 
- get/users/{user_id}/sales 
- get/users/{user_id}/sales/latest
TO BE IMPLEMENTED
- get/products/{product_id}/sales/total
- get/users/{user_id}/sales/total
- other CRUD endpoints, like update and put new products and users
- front-end

API concerns sales of highly desirable merch from the coffers of Northcoders.

To run the API locally :
1. Fork and clone the repo.
2. Ensure that your Python interpreter is Python 3.9.7 - you may use a tool like `pyenv`.
3. Create and activate a virtual environment:
 
  python -m venv venv
  source venv/bin/activate

4. Install the dependencies:

  pip install -r requirements.txt

5. Set the `PYTHONPATH`
  export PYTHONPATH=$(pwd)

6. Start the server by running:

  python src/api/app.py

7. Navigate to `localhost:8000/api/ui/` to view the API documentation page.
8. Then you can navigate to the endpoint of your choice, e.g. `localhost:8000/api/categories`.
