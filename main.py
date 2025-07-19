import os
from googleapiclient.discovery import build
from datetime import datetime
import re
from typing import List, Tuple

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def extract_channel_id(youtube, url_or_id: str) -> str:
    """Lấy channel ID từ link, @username hoặc channel ID."""
    if not isinstance(url_or_id, str):
        raise ValueError("url_or_id must be a string")
    url_or_id = url_or_id.strip()
    # Nếu là channel ID thì trả về luôn
    if url_or_id.startswith('UC') and len(url_or_id) == 24:
        return url_or_id
    # Nếu là link @username thì lấy username
    match = re.search(r"@([\w\-]+)", url_or_id)
    if match:
        username = match.group(1)
        # Luôn dùng search API để lấy channelId từ username
        search = youtube.search().list(q=username, type='channel', part='snippet', maxResults=1).execute()
        if search.get('items'):
            return search['items'][0]['snippet']['channelId']
    # Nếu là link channel/UC...
    match = re.search(r"channel/(UC[\w\-]{22})", url_or_id)
    if match:
        return match.group(1)
    raise ValueError(f'Không thể xác định channel ID từ link hoặc username: {url_or_id}')

def get_channel_title(youtube, channel_id: str) -> str:
    res = youtube.channels().list(id=channel_id, part='snippet').execute()
    if res.get('items'):
        return res['items'][0]['snippet']['title']
    raise ValueError(f'Không tìm thấy thông tin kênh với ID: {channel_id}')

def get_videos_from_channel(youtube, channel_id: str) -> List[Tuple[str, str, str]]:
    res = youtube.channels().list(id=channel_id, part='contentDetails').execute()
    if not res.get('items'):
        raise ValueError(f'Không tìm thấy playlist uploads cho kênh: {channel_id}')
    uploads_playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    videos = []
    next_page_token = None
    while True:
        pl_request = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part='snippet',
            maxResults=50,
            pageToken=next_page_token
        )
        pl_response = pl_request.execute()
        for item in pl_response.get('items', []):
            title = item['snippet']['title'].replace('|', '-')
            video_id = item['snippet']['resourceId']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            published_at = item['snippet']['publishedAt'][:10]
            videos.append((title, video_url, published_at))
        next_page_token = pl_response.get('nextPageToken')
        if not next_page_token:
            break
    # Sắp xếp tăng dần theo ngày tạo (video cũ nhất lên đầu)
    videos.sort(key=lambda x: x[2])
    return videos

def main():
    API_KEY = os.getenv("YOUTUBE_API_KEY")
    if not API_KEY:
        print("Không tìm thấy YOUTUBE_API_KEY trong file .env!")
        return
    input_file = "input.md"
    output_file = "output.md"
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            channel_links = [line.strip() for line in f if line.strip() and (line.strip().startswith('http://') or line.strip().startswith('https://'))]
    except Exception as e:
        print(f"Lỗi khi đọc file {input_file}: {e}")
        return
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    all_videos = []
    channel_sections = []
    for link in channel_links:
        try:
            channel_id = extract_channel_id(youtube, link)
            channel_title = get_channel_title(youtube, channel_id)
            videos = get_videos_from_channel(youtube, channel_id)
        except Exception as e:
            print(f"Lỗi với kênh {link}: {e}")
            continue
        all_videos.extend(videos)
        total = len(videos)
        section = f"## {channel_title}\n\n"
        section += f"- Channel link: {link}\n"
        section += f"- Channel ID: {channel_id}\n"
        section += f"- Total videos: {total}\n\n"
        section += "| No. | Title | Link | Created Date |\n"
        section += "|-----|-------|------|--------------|\n"
        for idx, (title, url, date) in enumerate(videos, 1):
            section += f"| {idx} | {title} | [Link]({url}) | {date} |\n"
        channel_sections.append(section)
    # Section 1: Thông tin chung
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    header = "# YouTube Video Collection\n\n"
    header += f"- File created at: {now}\n"
    header += f"- Total channels: {len(channel_sections)}\n"
    header += f"- Total videos collected: {len(all_videos)}\n"
    header += f"- Source file: {input_file}\n\n"
    # Ghi ra file output
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(header)
            for section in channel_sections:
                f.write(section + '\n')
        print(f"Đã lưu thông tin vào file {output_file}")
        print(f"Tổng số kênh: {len(channel_sections)} | Tổng số video: {len(all_videos)} | Thời gian tạo: {now}")
        print(f"Bạn có thể mở file '{output_file}' để xem kết quả chi tiết cho từng kênh.")
    except Exception as e:
        print(f"Lỗi khi ghi file {output_file}: {e}")

if __name__ == "__main__":
    main()