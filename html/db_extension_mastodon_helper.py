from sqlalchemy.exc import SQLAlchemyError

from db_models import Mastodon, db, commit_db_changes
from helper import logging, sanitize_string


def get_mastodon_tag_by_name(tag_name: str):
    try:
        tag = db.session.query(Mastodon).filter(Mastodon.name == tag_name).first()
        if tag: return tag
    except SQLAlchemyError as e:
        logging(f"An error occurred while retrieving a tag from the mastodon table: {e}")
    return False

def get_all_mastodon_tags():
    tags = Mastodon.query.all()
    if not tags: return []
    return tags

def add_mastodon_tag(tag_name: str, tag_limit: int):
    if get_mastodon_tag_by_name(tag_name):
        logging(f"Tag with the same name already exist in the mastodon table")
        return False

    try:
        tag = Mastodon(tag_name, tag_limit)
        db.session.add(tag)
        db.session.commit()
    except SQLAlchemyError as e:
        logging(f"An error occurred while adding a tag to the maston table: {e}")
        return False
    return True

def remove_mastodon_tag(tag_name: str):
    try:
        tag = get_mastodon_tag_by_name(tag_name)
        if tag:
            db.session.delete(tag)
            db.session.commit()
            return tag
        logging("Tag to delete wasn't found in the mastodon table")
        return False
    except SQLAlchemyError as e:
        logging(f"An error occurred while removing a tag from the mastodon table: {e}")
        return False

def update_mastodon_tag(tag_name: str, tag_limit: int):
    tag = get_mastodon_tag_by_name(tag_name)
    if not tag:
        logging("The tag to update do not exist")
        return False
    
    if tag_limit == 0:
        if not remove_mastodon_tag(tag_name):
            return False
    elif not tag.set_limit(tag_limit):
        logging("An error occured while updating the tags limit")
        return False
    return True

