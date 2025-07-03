import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_file, after_this_request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from dotenv import load_dotenv
import io

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))

# Spotify credentials from environment variables
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID', "")
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET', "")
REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI', 'http://127.0.0.1:5000/callback')

def get_spotify_client():
    """
    Initialize and return a Spotify client with user authentication.
    Raises ValueError if credentials or token are missing.
    """
    if not CLIENT_ID or not CLIENT_SECRET:
        logger.error("Spotify credentials are not set in environment variables.")
        raise ValueError("Please set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables.")

    if 'token_info' in session:
        token_info = session['token_info']
        return spotipy.Spotify(auth=token_info['access_token'])
    else:
        logger.error("No authentication token found in session.")
        raise ValueError("No authentication token found. Please login first.")

def get_user_playlists(sp):
    """
    Get all playlists for the authenticated user.
    """
    playlists = []
    results = sp.current_user_playlists()
    while results:
        playlists.extend(results['items'])
        results = sp.next(results) if results['next'] else None
    return playlists

def get_playlist_tracks(sp, playlist_id):
    """
    Get all tracks from a specific playlist.
    """
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    while results:
        tracks.extend(results['items'])
        results = sp.next(results) if results['next'] else None
    return tracks

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@app.route('/login')
def login():
    """Start Spotify OAuth login flow."""
    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope='playlist-read-private playlist-read-collaborative'
    )
    auth_url = sp_oauth.get_authorize_url()
    logger.info(f"Redirecting user to Spotify auth URL: {auth_url}")
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Handle Spotify OAuth callback and store token in session."""
    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope='playlist-read-private playlist-read-collaborative'
    )
    session.clear()
    code = request.args.get('code')
    if not code:
        logger.error("No code received in callback.")
        return "Authorization failed: No code received.", 400
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    logger.info("Spotify token stored in session.")
    return redirect(url_for('export'))

@app.route('/export')
def export():
    """
    Export all user playlists and tracks to a CSV file and send as download.
    """
    try:
        if 'token_info' not in session:
            logger.warning("No token in session, redirecting to login.")
            return redirect(url_for('login'))

        sp = get_spotify_client()
        playlists = get_user_playlists(sp)

        all_tracks = []
        for playlist in playlists:
            playlist_name = playlist['name']
            tracks = get_playlist_tracks(sp, playlist['id'])
            for track in tracks:
                if track['track'] is None:
                    continue
                track_info = {
                    'Playlist Name': playlist_name,
                    'Track Name': track['track']['name'],
                    'Artist': ', '.join([artist['name'] for artist in track['track']['artists']]),
                    'Album': track['track']['album']['name'],
                    'Release Date': track['track']['album']['release_date'],
                    'Duration (ms)': track['track']['duration_ms'],
                    'Popularity': track['track']['popularity']
                }
                all_tracks.append(track_info)

        if not all_tracks:
            logger.info("No tracks found in any playlist.")
            return "No tracks found in your playlists.", 200

        df = pd.DataFrame(all_tracks)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'spotify_playlists_{timestamp}.csv'

        output = io.BytesIO()
        df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)

        logger.info(f"Exported playlists to in-memory file {filename}")

        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.exception("An error occurred during export.")
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True) 