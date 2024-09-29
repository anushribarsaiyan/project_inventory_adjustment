 
# Inventory Management API

## Description
This project is an Inventory Management API built using Django REST framework. It provides user authentication and CRUD functionalities for inventory items.

## Features
- User signup and login (JWT authentication).
- Create, list, retrieve, update, and delete inventory items.
- Caching mechanism to optimize database queries.

## Prerequisites
- Python 3.11
- Django 5.1.1
- Django REST Framework
- Django Simple JWT

## Project Setup Instructions

1. **Clone the repository**:

git clone <repository-url>
cd <project-directory>
Create and activate a virtual environment:

python -m venv env

# For Windows: env\Scripts\activate
source env/bin/activate  
# For linux:
source .venv/bin/activate

Install the dependencies:
pip install -r requirements.txt

# Run the migrations:
python manage.py makemigrations
python manage.py migrate

# Start the development server:
python manage.py runserver

# Logging
Logging is enabled to track user activities and errors. Logs can be viewed in the console during development.

# Caching
The project uses caching to optimize inventory item retrieval. Cache expiration is set to 5 minutes.

