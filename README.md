# YouTube Channel Video Collector

This project collects and exports all videos (title, link, and creation date) from one or more YouTube channels into a Markdown file. It uses the official YouTube Data API v3 for reliable and up-to-date results.

## Features
- Input a list of YouTube channel links (supports @username, /channel/UC..., or direct channel ID)
- Automatically detects and skips non-link lines in the input file
- Collects all videos from each channel, including:
  - Video title
  - Video link
  - Video creation date
- Outputs a well-formatted Markdown file with:
  - General summary section (creation time, total channels, total videos, etc.)
  - One section per channel, with a table of all videos
- Handles errors gracefully and continues processing other channels

## Requirements
- Python 3.7+
- YouTube Data API v3 key
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## Setup
1. **Clone the repository and install dependencies:**
   ```bash
   git clone <your-repo-url>
   cd get-video-list
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Prepare your API key:**
   - Get your API key from [Google Cloud Console](https://console.developers.google.com/).
   - Copy `.env.sample` to `.env` and paste your API key:
     ```
     cp .env.sample .env
     # Then edit .env and set YOUTUBE_API_KEY=your_key_here
     ```

3. **Prepare your input file:**
   - Copy `input.md.sample` to `input.md` and add your YouTube channel links (one per line).
   - You can add comments or notes; only lines starting with `http://` or `https://` will be processed.
   - Example:
     ```
     # My favorite channels
     https://www.youtube.com/@GoogleCareerCertificates
     ```

## Usage
Run the script:
```bash
python main.py
```

- The script will generate `output.md` with all collected video data, organized by channel.
- Any errors (e.g. invalid channel, quota exceeded) will be printed but will not stop the script.

## Output Example
```
# YouTube Video Collection

- File created at: 2025-07-19 16:00:00
- Total channels: 2
- Total videos collected: 1234
- Source file: input.md

## Channel Name

- Channel link: https://www.youtube.com/@GoogleCareerCertificates
- Channel ID: <channel_id_here>
- Total videos: <total_videos_here>

| No. | Title | Link | Created Date |
|-----|-------|------|--------------|
| 1   | ...   | ...  | ...          |
```

## Notes
- The script skips any channel that cannot be found or accessed.
- API quota limits may apply depending on your Google Cloud project.
- For large channels, the script may take several minutes to complete.
- Only lines starting with `http://` or `https://` in `input.md` are processed as channel links.

## License
MIT
