from flask import Flask, request, render_template_string
import requests
from datetime import datetime, timezone, timedelta
from collections import Counter

app = Flask(__name__)

# Reddit API configuration
CLIENT_ID = 'MYD6BKoBjJ6FSXL9b8VscQ'
CLIENT_SECRET = 'TUslDdCpAZEZCeNcBxU3Uu-9Zx6QdQ'
USER_AGENT = "subreddit_report/1.0 by u/Expert_Tune_4913"

def get_reddit_token():
    """Get an authentication token from the Reddit API.

    Returns:
        str: The authentication token.
    """
    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    data = {'grant_type': 'client_credentials'}
    headers = {'User-Agent': USER_AGENT}
    response = requests.post('https://www.reddit.com/api/v1/access_token',
                             auth=auth, data=data, headers=headers)
    response.raise_for_status()
    return response.json().get('access_token')

def get_subreddit_data(subreddit, token):
    """Retrieve data about a subreddit.

    Args:
        subreddit (str): The subreddit name.
        token (str): The authentication token.

    Returns:
        dict: Subreddit data.
    """
    headers = {'Authorization': f'bearer {token}', 'User-Agent': USER_AGENT}
    response = requests.get(f'https://oauth.reddit.com/r/{subreddit}/about.json',
                            headers=headers)
    response.raise_for_status()
    return response.json().get('data', {})

def get_hot_threads(subreddit, token, limit=10):
    """Retrieve the hot threads from a subreddit.

    Args:
        subreddit (str): The subreddit name.
        token (str): The authentication token.
        limit (int, optional): The number of threads to retrieve. Defaults to 10.

    Returns:
        list: A list of hot threads.
    """
    headers = {'Authorization': f'bearer {token}', 'User-Agent': USER_AGENT}
    response = requests.get(f'https://oauth.reddit.com/r/{subreddit}/hot.json?limit={limit}',
                            headers=headers)
    response.raise_for_status()
    return response.json().get('data', {}).get('children', [])

def analyze_threads(threads):
    """Analyze threads for flair usage and metadata.

    Args:
        threads (list): A list of threads to analyze.

    Returns:
        tuple: A tuple containing flair statistics (Counter), recent post count (int), and metadata (list).
    """
    now = datetime.now(timezone.utc)
    flairs = Counter()
    recent_posts = 0
    metadata = []

    for thread in threads:
        data = thread['data']
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
            'flair': flair,
            'link': f"https://www.reddit.com{data['permalink']}",
            'created': created_utc.strftime('%Y-%m-%d %H:%M:%S')
        })

    return flairs, recent_posts, metadata

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>{{ subreddit_data['display_name_prefixed'] }} Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>{{ subreddit_data['display_name_prefixed'] }}</h1>
    <p>{{ subreddit_data['public_description'] }}</p>
    <p><strong>Subscribers:</strong> {{ subreddit_data['subscribers'] }}</p>
    <p><strong>Posts in Last 24h:</strong> {{ recent_posts }}</p>

    <form method="GET">
        <label for="num_threads">Number of Threads:</label>
        <input type="number" name="num_threads" value="{{ num_threads }}" min="1" max="50">
        <button type="submit">Filter</button>
        <br><br>
        {% for flair in flairs %}
            <input type="checkbox" name="selected_flairs" value="{{ flair }}" 
                {% if flair in selected_flairs %}checked{% endif %}> {{ flair }}<br>
        {% endfor %}
        <button type="submit">Apply Flair Filter</button>
    </form>

    <h2>Highlighted Threads</h2>
<ul>
    {% for thread in threads %}
        <li>
            <a href="{{ thread['link'] }}" target="_blank">{{ thread['title'] }}</a><br>
            <strong>Author:</strong> {{ thread['author'] }} | 
            <strong>Score:</strong> {{ thread['score'] }} | 
            <strong>Comments:</strong> {{ thread['comments'] }} | 
            <strong>Created:</strong> {{ thread['created'] }} | 
            <strong>Flair:</strong> {{ thread['flair'] }}
        </li>
        <hr>
    {% endfor %}
</ul>
    <h2>Most Used Flairs</h2>
    <ul>
        {% for flair, count in flair_stats.items() %}
            <li>{{ flair }}: {{ count }}</li>
        {% endfor %}
    </ul>

    <h2>Flair Statistics Chart</h2>
    <canvas id="flairChart" width="400" height="200"></canvas>

    <script>
        const ctx = document.getElementById('flairChart').getContext('2d');
        const data = {
            labels: {{ flair_stats.keys()|list|tojson }},
            datasets: [{
                label: 'Flair Usage',
                data: {{ flair_stats.values()|list|tojson }},
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        };

        const config = {
            type: 'bar',
            data: data,
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        };

        new Chart(ctx, config);
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    """Render the main page with subreddit statistics.

    Returns:
        str: The rendered HTML page.
    """
    subreddit = "opium"  # Default subreddit
    token = get_reddit_token()

    # Input filtering
    num_threads = int(request.args.get("num_threads", 10))
    selected_flairs = request.args.getlist("selected_flairs")

    # Fetch data
    subreddit_data = get_subreddit_data(subreddit, token)
    threads_data = get_hot_threads(subreddit, token, limit=50)

    # Analyze threads
    flairs, recent_posts, metadata = analyze_threads(threads_data)

    # Filter by selected flairs
    if selected_flairs:
        metadata = [t for t in metadata if t['flair'] in selected_flairs]

    # Limit number of threads
    metadata = metadata[:num_threads]

    return render_template_string(HTML_TEMPLATE,
                                  subreddit_data=subreddit_data,
                                  threads=metadata,
                                  flairs=flairs.keys(),
                                  flair_stats=flairs,
                                  recent_posts=recent_posts,
                                  num_threads=num_threads,
                                  selected_flairs=selected_flairs)

if __name__ == "__main__":
    app.run(debug=True)
