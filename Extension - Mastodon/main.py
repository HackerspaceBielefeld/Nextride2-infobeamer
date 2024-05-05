import json
import requests
import pandas as pd

from filter import filter_main
from slide_creator import slide_creator

hashtag = 'apple'
URL = f'https://mastodon.social/api/v1/timelines/tag/{hashtag}'
params = {
    'limit': 1
}

r = requests.get(URL, params=params)
toots = json.loads(r.text)

# Create pandas data frames from toots
toots_df = pd.DataFrame(toots)

# Convert "created_at" timestamps to pandas Timestamp objects
toots_df['created_at'] = pd.to_datetime(toots_df['created_at']).dt.tz_convert('Europe/Berlin')

# Filter toots
one_hour_ago = pd.Timestamp.now(tz='Europe/Berlin') - pd.Timedelta(hours=1)
filtered_toots_df = filter_main(toots_df, one_hour_ago)

for index, row in filtered_toots_df.iterrows():
    slide_creator(row)
    print(row['account']['username'])
    print(row['account']['avatar'])
    print(row['created_at'])
    print(row['tags'])
    print(row['uri'])
    #print(row['media_attachments'])
    print("#################\n")


