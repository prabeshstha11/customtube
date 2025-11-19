import os
import json
from flask import Flask, render_template, request, jsonify
from database import db, SearchCache, SavedKeyword, BannedChannel
from scraper import fetch_videos

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customtube.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/keywords', methods=['GET', 'POST'])
def manage_keywords():
    if request.method == 'GET':
        keywords = SavedKeyword.query.order_by(SavedKeyword.created_at.desc()).all()
        return jsonify([k.keyword for k in keywords])
    
    if request.method == 'POST':
        data = request.get_json()
        keyword = data.get('keyword')
        if not keyword:
            return jsonify({'error': 'No keyword provided'}), 400
        
        if SavedKeyword.query.filter_by(keyword=keyword).first():
            return jsonify({'error': 'Keyword already exists'}), 400
            
        new_keyword = SavedKeyword(keyword=keyword)
        db.session.add(new_keyword)
        db.session.commit()
        return jsonify({'message': 'Keyword added', 'keyword': keyword}), 201

@app.route('/api/keywords/<string:keyword>', methods=['DELETE'])
def delete_keyword(keyword):
    saved_keyword = SavedKeyword.query.filter_by(keyword=keyword).first()
    if not saved_keyword:
        return jsonify({'error': 'Keyword not found'}), 404
        
    db.session.delete(saved_keyword)
    db.session.commit()
    return jsonify({'message': 'Keyword deleted'})

@app.route('/api/ban_channel', methods=['POST'])
def ban_channel():
    data = request.get_json()
    channel_name = data.get('channel_name')
    if not channel_name:
        return jsonify({'error': 'No channel name provided'}), 400
    
    if BannedChannel.query.filter_by(channel_name=channel_name).first():
        return jsonify({'message': 'Channel already banned'}), 200
        
    new_ban = BannedChannel(channel_name=channel_name)
    db.session.add(new_ban)
    db.session.commit()
    return jsonify({'message': f'Banned channel: {channel_name}'}), 201

@app.route('/api/feed', methods=['GET'])
def get_feed():
    keywords = SavedKeyword.query.all()
    if not keywords:
        return jsonify({'videos': [], 'message': 'No keywords saved'})

    # Get banned channels
    banned_channels = {b.channel_name for b in BannedChannel.query.all()}

    all_videos = []
    seen_ids = set()
    
    # Fetch videos for each keyword
    for k in keywords:
        # Check cache first
        cached_result = SearchCache.query.filter_by(keywords=k.keyword).order_by(SearchCache.created_at.desc()).first()
        
        videos = []
        if cached_result:
             # TODO: Check expiry? For now, just use it.
             videos = json.loads(cached_result.results_json)
        else:
            # Fetch fresh
            print(f"Fetching fresh videos for '{k.keyword}'")
            videos = fetch_videos(k.keyword, limit=10)
            if videos:
                new_cache = SearchCache(keywords=k.keyword, results_json=json.dumps(videos))
                db.session.add(new_cache)
                db.session.commit()
        
        # Deduplicate and add
        for video in videos:
            # Filter banned channels
            if video.get('uploader') in banned_channels:
                continue

            if video['id'] not in seen_ids:
                seen_ids.add(video['id'])
                all_videos.append(video)
    
    # Optional: Shuffle or sort by date?
    # For now, let's sort by upload date if available, or just mix them?
    # Simple mix: they are currently grouped by keyword.
    # Let's shuffle them to make it feel like a feed.
    import random
    random.shuffle(all_videos)

    return jsonify({'videos': all_videos})

if __name__ == '__main__':
    # For development
    app.run(debug=True, port=5000)

# ASGI entry point for Uvicorn
from asgiref.wsgi import WsgiToAsgi
asgi_app = WsgiToAsgi(app)
