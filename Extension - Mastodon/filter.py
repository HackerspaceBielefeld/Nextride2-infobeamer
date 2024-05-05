from profanity_check import predict
from bs4 import BeautifulSoup
import emoji
import re

def html_to_text(content):
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text(separator=' ')
    
    return text.strip(" ")

def adjust_content(content: str):
    pattern_anchor = r'<a\s.*?</a>'
    content = re.sub(pattern_anchor, "", content)

    content = html_to_text(content)

    content.strip(" ")
    if len(content) >= 250:
        content = content[:247] + "..."

    content = emoji.emojize(content, language='alias')
    
    content = content.encode('unicode-escape').decode('unicode-escape')
    return content


def filter_main(toots_df, not_older_then):  
    # Filter toots that are not older than one hour
    toots_df = toots_df[toots_df['created_at'] >= not_older_then]

    for index, row in toots_df.iterrows():
        # Filter sensitive
        if row['sensitive']:
            print("Removed toot because it contains sensitive content")
            toots_df.drop(index, inplace=True)

        # Filter for in_reply_to_id
        if row['in_reply_to_id'] or row['in_reply_to_account_id']:
            print("Removed toot because it's a reply")
            toots_df.drop(index, inplace=True)
        
        # Filter for polls
        if row['poll']:
            print("Removed toot because it contains a poll")
            toots_df.drop(index, inplace=True)

        # Filter supported languages
        if row['language'] not in ['de', 'en', "null", None]:
            print(f"Removed toot because it's content is in language: {row['language']}")
            toots_df.drop(index, inplace=True)

        if predict([row['content']]) or predict([row['account']['username']]):
            print(f"Removed toot because it contains bad content")
            toots_df.drop(index, inplace=True)

        toots_df.at[index, 'content'] = adjust_content(row['content'])

    return toots_df