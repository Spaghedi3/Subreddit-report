import requests
from datetime import datetime, timezone, timedelta
from collections import Counter
from jinja2 import Template

CLIENT_ID = ''
CLIENT_SECRET = ''
USER_AGENT = "subreddit_report/1.0"


def get_token():
    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    data = {'grant_type': 'client_credentials'}
    headers = {'User-Agent': USER_AGENT}
    response = requests.post(
        'https://www.reddit.com/api/v1/access_token',
        auth=auth, data=data, headers=headers)
    print(response.json())
    return response.json().get('access_token')


def get_data(subreddit, token):
    headers = {'Authorization': f'bearer {token}', 'User-Agent': USER_AGENT}
    response = requests.get(
        f'https://oauth.reddit.com/r/{subreddit}/about.json', headers=headers)

    return response.json().get('data', {})

def get_hot_posts(subreddit, token, limit=10):
    headers = {'Authorization': f'bearer {token}', 'User-Agent': USER_AGENT}
    response = requests.get(
        f'https://oauth.reddit.com/r/{subreddit}/hot.json?limit={limit}', headers=headers)
    return response.json().get('data', {}).get('children', [])

def analyze_posts(posts):
    now = datetime.now(timezone.utc)
    flairs = Counter()
    recent_posts = 0
    metadata = []

    for post in posts:
        data = post['data']
        flair = data.get('link_flair_text', 'No Flair')
        created_utc = datetime.fromtimestamp(data['created_utc'], timezone.utc)

        flairs[flair] += 1

        if now - created_utc <= timedelta(days=1):
            recent_posts += 1

        metadata.append({
            'title': data['title'],
            'author': data['author'],
            'score': data['score'],
            'comments': data['num_comments'],
            'link': f"https://www.reddit.com{data['permalink']}",
            'created': created_utc.strftime('%Y-%m-%d %H:%M:%S')
        })

    return flairs, recent_posts, metadata

def generate_html(subreddit_data):
    template = Template("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ subreddit_data['display_name_prefixed'] }} Report</title>
    </head>
    <body>
        <h1>{{ subreddit_data['display_name_prefixed'] }}</h1>
        <p>{{ subreddit_data['public_description'] }}</p>
        <p><strong>Subscribers:</strong> {{ subreddit_data['subscribers'] }}</p>
        <p><strong>Active Users:</strong> {{ subreddit_data['accounts_active'] }}</p>
        <p><strong>Posts in Last 24h:</strong> {{ recent_posts }}</p>
    </body>
    </html>
    """)
    return template.render(
        subreddit_data=subreddit_data)

if __name__ == "__main__":
    token = get_token()
    subreddit = "python"
    subreddit_data = get_data(subreddit, token)
    hot_posts = get_hot_posts(subreddit, token, limit=10)
    print("posts:")
    for post in hot_posts:
        print(post)
    flairs, recent_posts, metadata = analyze_posts(hot_posts)
    for flair, count in flairs.items():
        print(f'flair:{flair}:{count}')
    print(f'recent posts:{recent_posts}')
    print(f'metadata:{metadata}')
    html_content = generate_html(subreddit_data)
    with open("subreddit_report.html", "w", encoding="utf-8") as f:
        f.write(html_content)