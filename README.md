# Guardians of the Playlist

A Flask web app to export all your Spotify playlists and tracks to a CSV file, ready for download. No files are stored on the server—your data is streamed directly to you!

## Features
- Login with your Spotify account (OAuth)
- Export all your playlists and tracks to a CSV file
- CSV is generated in-memory and sent directly to your browser (no server clutter)

## Requirements
- Python 3.7+
- Spotify Developer account ([create an app here](https://developer.spotify.com/dashboard/applications))

## Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/guardians-of-the-playlist.git
   cd guardians-of-the-playlist
   ```
2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment variables:**
   Create a `.env` file in the project root with the following:
   ```env
   SPOTIPY_CLIENT_ID=your_spotify_client_id
   SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
   FLASK_SECRET_KEY=your_flask_secret_key
   # Optional: override redirect URI
   # SPOTIPY_REDIRECT_URI=http://127.0.0.1:5000/callback
   ```

## Usage
1. **Run the app:**
   ```bash
   python app.py
   ```
2. **Open your browser and go to:**
   [http://127.0.0.1:5000](http://127.0.0.1:5000)
3. **Login with Spotify and export your playlists!**

## Deployment
- This app requires a Python server and cannot be hosted on GitHub Pages.
- For free hosting, consider [Render](https://render.com/), [Railway](https://railway.app/), or [Fly.io](https://fly.io/).
- Make sure to set your environment variables on your chosen platform.

## Security
- Never commit your `.env` file or credentials to version control.
- The `.gitignore` is set up to ignore `.env`, `venv/`, and other sensitive or unnecessary files.

## License
MIT