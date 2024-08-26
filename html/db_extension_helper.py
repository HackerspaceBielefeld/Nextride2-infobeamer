from sqlalchemy.exc import SQLAlchemyError

from db_models import Extension, db
from helper import logging

def get_extension_from_config(extension_name: str):
    try:
        extension = db.session.query(Extension).filter(Extension.name == extension_name).first()
        if extension: return extension
    except SQLAlchemyError as e:
        logging(f"An error occurred while retrieving an extension from the extension table: {e}")
    return False

def get_extensions_from_extensions():
    extensions = Extension.query.all()
    if not extensions: return []
    return extensions
