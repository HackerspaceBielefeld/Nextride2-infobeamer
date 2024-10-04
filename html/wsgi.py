"""
@file wsgi.py
@brief WSGI entry point for the Flask application.

@details This module sets up the WSGI application to be served by a WSGI server
            like Gunicorn or uWSGI. It allows running the app in production.

@author Inflac
@date 2024-10-04
"""

from app import app

if __name__ == "__main__":
    app.run()