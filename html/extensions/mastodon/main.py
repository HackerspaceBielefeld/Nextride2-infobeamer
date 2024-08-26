import os
import json
import requests
import pandas as pd

from post_filter import post_filter
from slide_creator import slide_creator
from db_extension_mastodon_helper import get_all_mastodon_tags

def create_slides(hashtag:str, limit:int):

    URL = f'https://mastodon.social/api/v1/timelines/tag/{hashtag}'

    r = requests.get(URL, params={'limit': limit})
    toots = json.loads(r.text)

    # Create pandas data frames from toots
    toots_df = pd.DataFrame(toots)

    # Convert "created_at" timestamps to pandas Timestamp objects
    toots_df['created_at'] = pd.to_datetime(toots_df['created_at']).dt.tz_convert('Europe/Berlin')

    # Filter toots
    one_hour_ago = pd.Timestamp.now(tz='Europe/Berlin') - pd.Timedelta(hours=3)
    filtered_toots_df = post_filter(toots_df, one_hour_ago)

    for index, row in filtered_toots_df.iterrows():
        if type(row['account']) == float: continue
        slide_creator(row, "static/uploads/")

def remove_old_images():
    for image in os.listdir("static/uploads/"):
        if image.split("_", 1)[0] == "mastodon":
            os.remove(os.path.join("static/uploads/", image))


def main():
    remove_old_images()
    for tag in get_all_mastodon_tags():
        hashtag = tag.name
        limit = tag.limit
        create_slides(hashtag, limit)

if __name__ == '__main__':
    main()
