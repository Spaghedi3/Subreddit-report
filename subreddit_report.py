import requests
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

    html_content = generate_html(subreddit_data)
    with open("subreddit_report.html", "w", encoding="utf-8") as f:
        f.write(html_content)