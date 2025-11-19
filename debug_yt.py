import yt_dlp
import json

ydl_opts = {
    'default_search': 'ytsearch5:test video',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': True,
    'dump_single_json': True,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    result = ydl.extract_info("ytsearch5:test video", download=False)
    if 'entries' in result:
        print(json.dumps(result['entries'][0], indent=2))
