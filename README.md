# CustomTube

A distraction free youtube homepage for productivity.

![](https://i.imgur.com/WtDuY4R.png)

## Features

- **Keyword-Based Feed**: Your feed is generated solely from keywords you define (e.g., "lofi", "python").
- **Distraction-Free**: Automatically blocks YouTube Shorts and filters out videos shorter than 60 seconds.
- **Channel Banning**: Ban specific channels to hide them from your feed.
- **Privacy-First**: No Google account required. No tracking history.
- **Fast**: Built with Flask and Uvicorn, utilizing SQLite caching.

## Tech Stack

- **Backend**: Python (Flask + Uvicorn via ASGI)
- **Database**: SQLite (Flask-SQLAlchemy)
- **Scraping**: yt-dlp
- **Frontend**: HTML5, Bootstrap 5, Vanilla JS

## Getting Started

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) (Recommended) or pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/customtube.git
   cd customtube
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Run the application**
   ```bash
   uv run uvicorn app:asgi_app --port 8000
   ```

4. **Open your browser**
   Visit `http://localhost:8000`

## Usage

1. **Add Keywords**: Type a topic you're interested in and hit Add.
2. **View Feed**: Your feed will populate with videos matching your keywords.
3. **Ban Channels**: Click the **Ban** button on any video card to hide that channel.
