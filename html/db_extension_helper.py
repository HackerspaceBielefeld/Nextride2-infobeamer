"""
@file db_extension_helper.py
@brief This module provides helper functions to interact with the 'Extension' table in the database.

This module includes functions to retrieve specific extension entries or all entries from the 'Extension' table.
SQLAlchemy is used for database interaction, and all exceptions are handled with appropriate logging.

@dependencies
- SQLAlchemy for database ORM
- Custom logging function from the helper module
- Extension model from db_models

@author Inflac
@date 2024-10-04
"""

from typing import Union

from sqlalchemy.exc import SQLAlchemyError
from db_models import Extension, db
from helper import logging

def db_get_extension(extension_name: str) -> Union[bool, Extension]:
    """
    @brief Retrieves an extension entry by its name.

    This function queries the 'Extension' table for an entry that matches the given extension name.

    @param extension_name The name of the extension to retrieve.
    
    @return The matching Extension object if found, False otherwise.
    
    @exception SQLAlchemyError Logs an error message if an exception occurs while querying the database.
    """
    try:
        extension = db.session.query(Extension).filter(Extension.name == extension_name).first()
        if extension:
            logging(f"Extension '{extension_name}' successfully retrieved.")
            return extension
        else:
            logging(f"No extension found with the name '{extension_name}'.")
    except SQLAlchemyError as e:
        logging(f"An error occurred while retrieving extension '{extension_name}' from the database: {e}")
    
    return False

def db_get_extensions() -> list:
    """
    @brief Retrieves all entries from the 'Extension' table.

    This function queries the 'Extension' table and returns all entries as a list.
    
    @return A list of Extension objects. Returns an empty list if no entries are found.
    
    @exception SQLAlchemyError Logs an error message if an exception occurs while querying the database.
    """
    try:
        extensions = db.session.query(Extension).all()
        if extensions:
            logging(f"{len(extensions)} extensions successfully retrieved.")
            return extensions
        else:
            logging("No extensions found in the database.")
            return []
    except SQLAlchemyError as e:
        logging(f"An error occurred while retrieving all extensions: {e}")
        return []

