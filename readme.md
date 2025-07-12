# Subreddit-report

Python (Flask) project.

## Overview

Subreddit-report is a Python-based project designed to generate reports and analytics for Reddit subreddits. It includes a web interface built with HTML to display the results in an intuitive and user-friendly format.

## Features

- **Subreddit Data Analysis**: Analyze posts, comments, and user activity within a subreddit.
- **Customizable Reports**: Generate detailed reports based on subreddit activity.
- **Web Interface**: View reports and analytics through a clean, responsive HTML interface.
- **Python Backend**: Leverages Python for data scraping, processing, and analysis.

## Technologies Used

- **Python (53.6%)**: Backbone of the project, used for data processing and analysis.
- **HTML (46.4%)**: Provides the structure and interface for presenting the results.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- A Reddit API key (you can get one by creating an application on [Reddit's developer page](https://www.reddit.com/prefs/apps))
- Required Python libraries (specified in the `requirements.txt` file)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Spaghedi3/Subreddit-report.git
   cd Subreddit-report
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Reddit API**
   - Create a `.env` file in the project root directory.
   - Add the following details to the `.env` file:
     ```
     CLIENT_ID=your_client_id
     CLIENT_SECRET=your_client_secret
     USER_AGENT=your_user_agent
     ```

4. **Run the Application**
   ```bash
   python main.py
   ```

5. Open your web browser and navigate to the specified local server (e.g., `http://127.0.0.1:5000`).

## Usage

1. Enter the desired subreddit name in the interface.
2. Click the button to generate a report.
3. View the results, which include activity trends, top posts, and user statistics.

## Contributing

Contributions are welcome! Please fork the repository, create a new branch, and submit a pull request with your changes. Make sure your code adheres to the project's coding standards.

## License

This project is currently unlicensed. For usage and contribution rights, contact the repository owner.

## Contact

For any questions or issues, feel free to open an issue on GitHub or contact the repository owner, [Spaghedi3](https://github.com/Spaghedi3).
