import yt_dlp
import json

def fetch_videos(keywords, limit=10):
    """
    Fetches videos from YouTube using yt-dlp based on keywords.
    Returns a list of dictionaries containing video details.
    """
    ydl_opts = {
        'default_search': f'ytsearch{limit * 2}:{keywords}', # Fetch more to filter out shorts
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True, # Do not download video, just get metadata
        'dump_single_json': True,
    }

    videos = []
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch{limit * 2}:{keywords}", download=False)
            
            if 'entries' in result:
                for entry in result['entries']:
                    # Filter out shorts (usually < 60s) if duration is available
                    # Note: extract_flat might not always give duration, but 'ytsearch' usually does.
                    # If duration is missing, we might assume it's a video or skip.
                    # Shorts often have 'shorts' in the URL or specific metadata, but duration is safest.
                    duration = entry.get('duration')
                    
                    # Skip if duration is less than 60 seconds (likely a short)
                    if duration and duration < 60:
                        continue

                    # Skip if URL contains '/shorts/'
                    url = entry.get('url')
                    if url and '/shorts/' in url:
                        continue
                        
                    # Get best thumbnail
                    thumbnail = entry.get('thumbnail')
                    if not thumbnail and entry.get('thumbnails'):
                        # Get the last thumbnail (usually highest res)
                        thumbnail = entry.get('thumbnails')[-1].get('url')

                    video_data = {
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'thumbnail': thumbnail, 
                        'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                        'duration': duration,
                        'view_count': entry.get('view_count'),
                        'uploader': entry.get('uploader'),
                        'upload_date': entry.get('upload_date'),
                    }
                    videos.append(video_data)
                    
                    if len(videos) >= limit:
                        break
                        
    except Exception as e:
        print(f"Error fetching videos: {e}")
        return []

    return videos
