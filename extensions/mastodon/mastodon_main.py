import json
import requests
import pandas as pd

from filter import filter
from slide_creator import slide_creator

def create_slides(hashtag:str, limit:int, destination_path: str):
    URL = f'https://mastodon.social/api/v1/timelines/tag/{hashtag}'

    r = requests.get(URL, params={'limit': limit})
    toots = json.loads(r.text)

    # Create pandas data frames from toots
    toots_df = pd.DataFrame(toots)

    # Convert "created_at" timestamps to pandas Timestamp objects
    toots_df['created_at'] = pd.to_datetime(toots_df['created_at']).dt.tz_convert('Europe/Berlin')

    # Filter toots
    one_hour_ago = pd.Timestamp.now(tz='Europe/Berlin') - pd.Timedelta(hours=1)
    filtered_toots_df = filter(toots_df, one_hour_ago)

    for index, row in filtered_toots_df.iterrows():
        if type(row['account']) == float: continue
        slide_creator(row, destination_path)
