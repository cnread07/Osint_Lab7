#!/usr/bin/env python3
"""
dashboard_server.py
Flask backend for OSINT Dashboard — unified collectors + DB storage
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import traceback
import os
from dotenv import load_dotenv

# load env
load_dotenv()

# config
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/osint.db')
DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', 5000))
DASHBOARD_HOST = os.getenv('DASHBOARD_HOST', '0.0.0.0')

# initialize DB helper on import
from database import init_db, save_to_db

init_db()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)


def normalize_record(rec):
    """Ensure record has required keys and normalized platform lowercased."""
    return {
        'platform': str(rec.get('platform', '')).lower(),
        'user': str(rec.get('user', '') or ''),
        'text': str(rec.get('text', '') or ''),
        'sentiment': float(rec.get('sentiment') or 0),
        'timestamp': rec.get('timestamp') or '',
        'url': rec.get('url') or ''
    }


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'database': os.path.exists(DATABASE_PATH)
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    # simple lightweight stats (safe if DB empty)
    try:
        from database import get_connection
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as total FROM osint_data")
        total = cur.fetchone()[0] if cur else 0
        cur.execute("SELECT COUNT(DISTINCT platform) FROM osint_data")
        platforms = cur.fetchone()[0] if cur else 0
        cur.execute("SELECT AVG(sentiment) FROM osint_data WHERE sentiment IS NOT NULL")
        avg = cur.fetchone()[0] or 0
        conn.close()
        return jsonify({
            'totalRecords': int(total),
            'platforms': int(platforms),
            'avgSentiment': round(float(avg), 3)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['GET'])
def api_search():
    q = request.args.get('q', '').strip()
    platform = request.args.get('platform', 'all').lower()
    if not q:
        return jsonify([])

    # search DB first
    try:
        from database import get_connection
        conn = get_connection()
        conn.row_factory = None
        cur = conn.cursor()

        sql = "SELECT platform, user, text, sentiment, timestamp, url FROM osint_data WHERE text LIKE ?"
        params = [f'%{q}%']
        if platform and platform != 'all':
            sql += " AND platform = ?"
            params.append(platform)
        sql += " ORDER BY timestamp DESC LIMIT 200"
        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()

        results = []
        for r in rows:
            # rows return tuples in order (platform, user, text, sentiment, timestamp, url)
            rec = {
                'platform': r[0],
                'user': r[1],
                'text': r[2],
                'sentiment': r[3] if r[3] is not None else 0,
                'timestamp': r[4] or '',
                'url': r[5] or ''
            }
            results.append(rec)

        if results:
            return jsonify(results)
    except Exception as e:
        print("DB search error:", e)
        traceback.print_exc()

    # if none in DB -> scrape live
    print(f"No DB results for '{q}' on '{platform}' -> scraping live")
    scraped = scrape_new_data(q, platform)
    # save to DB (normalized)
    if scraped:
        normalized = [normalize_record(r) for r in scraped]
        try:
            save_to_db(normalized)
        except Exception as e:
            print("Failed saving to DB:", e)
    return jsonify(scraped)


def safe_call(func, keyword, limit=10):
    try:
        return func(keyword, limit=limit) or []
    except Exception as e:
        print(f"Collector {getattr(func, '__name__', func)} failed:", e)
        traceback.print_exc()
        return []


def scrape_new_data(keyword, platform='all'):
    """Call collectors based on platform arg. Collectors should return list of dicts."""
    results = []

    # local imports (collectors placed next to this file or in collectors/ folder)
    # attempt to import each collector; if missing, skip gracefully
    collectors = []

    # map platform -> (module_name, function_name)
    collector_map = {
        'twitter': ('twitter_collector', 'fetch_twitter'),
        'reddit': ('reddit_collector', 'fetch_reddit'),
        'github': ('github_collector', 'fetch_github'),
        'linkedin': ('linkedin_collector', 'fetch_linkedin'),
        'hackernews': ('hackernews_collector', 'fetch_hackernews'),
        'mastodon': ('mastodon_collector', 'fetch_mastodon'),
        'snscrape': ('snscrape_collector', 'fetch_snscrape'),
        'stackoverflow': ('stackoverflow_collector', 'fetch_stackoverflow'),
        'harvester': ('harvester_collector', 'fetch_theharvester')
    }

    def try_add(name):
        mod_name, func_name = collector_map[name]
        try:
            mod = __import__(mod_name)
            func = getattr(mod, func_name)
            collectors.append((name, func))
        except Exception as e:
            print(f"[scrape] Could not load collector {mod_name}.{func_name}: {e}")

    if platform in ['all', 'twitter']:
        try_add('twitter')
    if platform in ['all', 'reddit']:
        try_add('reddit')
    if platform in ['all', 'github']:
        try_add('github')
    if platform in ['all', 'linkedin']:
        try_add('linkedin')
    if platform in ['all', 'hackernews']:
        try_add('hackernews')
    if platform in ['all', 'mastodon']:
        try_add('mastodon')
    if platform in ['all', 'snscrape']:
        try_add('snscrape')
    if platform in ['all', 'stackoverflow']:
        try_add('stackoverflow')
    if platform in ['all', 'harvester']:
        try_add('harvester')

    # call each collector safely
    for name, func in collectors:
        print(f"[scrape] Calling collector {name}")
        data = safe_call(func, keyword, limit=15)
        # normalize platform to lowercase string for frontend
        for d in data:
            d.setdefault('platform', name)
            results.append({
                'platform': str(d.get('platform')).lower(),
                'user': d.get('user', ''),
                'text': d.get('text', ''),
                'sentiment': d.get('sentiment', 0),
                'timestamp': d.get('timestamp', ''),
                'url': d.get('url', '')
            })
    print(f"[scrape] Collected {len(results)} total records")
    return results


# serve UI
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_ui(path):
    root = os.path.dirname(os.path.abspath(__file__))
    if path and os.path.exists(os.path.join(root, path)):
        return send_from_directory(root, path)
    index = os.path.join(root, 'index.html')
    if os.path.exists(index):
        return send_from_directory(root, 'index.html')
    return jsonify({'message': 'index.html not found'}), 404


if __name__ == '__main__':
    print("Starting OSINT Dashboard Server...")
    print(f"Host: {DASHBOARD_HOST} Port: {DASHBOARD_PORT}")
    app.run(host=DASHBOARD_HOST, port=DASHBOARD_PORT, debug=os.getenv('DASHBOARD_DEBUG', 'false').lower() == 'true')
