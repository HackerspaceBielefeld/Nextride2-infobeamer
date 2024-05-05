from sqlalchemy.exc import SQLAlchemyError

from db_models import Config, db
from helper import logging

def get_extension_from_config(extension_name: str):
    try:
        extension = db.session.query(Config).filter(Config.extension_name == extension_name).first()
        if extension: return extension
    except SQLAlchemyError as e:
        logging(f"An error occurred while retrieving an extension from the config table: {e}")
    return False

def get_extensions_from_config():
    extensions = Config.query.all()
    if not extensions: return []
    return extensions

def get_extensions_info_from_config():
    extensions = Config.query.all()
    if not extensions: return []
    return [(extension.extension_name, extension.active) for extension in extensions]