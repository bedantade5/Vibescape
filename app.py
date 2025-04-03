import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify, render_template, session
import joblib
import os
import json
from flask_cors import CORS
import random

app = Flask(__name__)
app.secret_key = 'music_recommendation_secret_key'
CORS(app) 

df = None
audio_features = ['danceability', 'energy', 'key', 'loudness', 'mode', 
                  'speechiness', 'acousticness', 'instrumentalness', 
                  'liveness', 'valence', 'tempo']

song_history = {}

def load_data():
    """Load the processed dataset and prepare it for recommendations"""
    global df

    try:
        df = pd.read_csv('processed_music_data.csv')
        print(f"Loaded processed dataset with {df.shape[0]} rows.")
    except FileNotFoundError:
        try:
            df = pd.read_csv('dataset.csv')
            print(f"Loaded original dataset with {df.shape[0]} rows.")
        except FileNotFoundError:
            print("Error: No dataset found. Please ensure 'processed_music_data.csv' or 'dataset.csv' exists.")
            df = None

    if df is not None:
        print(df.head())
        print("Available moods:", df['mood'].unique())

    df['track_id'] = df['track_id'].astype(str)
    precompute_feature_matrix()
    return df

# Precompute the feature matrix and similarity for faster recommendations
def precompute_feature_matrix():
    """Precompute the audio feature matrix and save scaler for reuse"""
    global df, audio_features
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df[audio_features])
    joblib.dump(scaler, 'audio_features_scaler.pkl')
    np.save('scaled_audio_features.npy', df_scaled)
    print("Precomputed feature matrix for recommendations.")
    return df_scaled

# Calculate a composite mood score based on audio features
def calculate_mood_score(songs_df, selected_mood):
    df_with_score = songs_df.copy()
    if selected_mood == 'happy':
        # Happy: High valence, moderate-high energy, high danceability
        df_with_score['mood_score'] = (
            df_with_score['valence'] * 0.5 + 
            df_with_score['energy'] * 0.3 + 
            df_with_score['danceability'] * 0.2
        )
    elif selected_mood == 'sad':
        # Sad: Low valence, low energy, high acousticness
        df_with_score['mood_score'] = (
            (1 - df_with_score['valence']) * 0.5 + 
            (1 - df_with_score['energy']) * 0.3 + 
            df_with_score['acousticness'] * 0.2
        )
    elif selected_mood == 'energetic':
        # Energetic: High energy, high tempo, high danceability
        df_with_score['mood_score'] = (
            df_with_score['energy'] * 0.5 + 
            df_with_score['tempo'] / 200 * 0.3 +
            df_with_score['danceability'] * 0.2
        )
    elif selected_mood == 'relaxed':
        # Relaxed: Low energy, high acousticness, moderate valence
        df_with_score['mood_score'] = (
            (1 - df_with_score['energy']) * 0.4 + 
            df_with_score['acousticness'] * 0.4 + 
            (1 - abs(df_with_score['valence'] - 0.5)) * 0.2
        )
    
    df_with_score['final_score'] = (
        df_with_score['mood_score'] * 0.65 + 
        df_with_score['popularity'] / 100 * 0.25 + 
        np.random.random(len(df_with_score)) * 0.1
    )
    return df_with_score

# Helper function to get session ID
def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(random.randint(10000, 99999))
    return session['session_id']

# Helper function to track history
def update_history(session_id, category, track_ids):
    global song_history    
    if session_id not in song_history:
        song_history[session_id] = {}    
    if category not in song_history[session_id]:
        song_history[session_id][category] = set()

    song_history[session_id][category].update(track_ids)

# Helper function to filter previously shown songs
def filter_history(songs_df, session_id, category):
    global song_history
    
    if session_id not in song_history or category not in song_history[session_id]:
        return songs_df
    return songs_df[~songs_df['track_id'].isin(song_history[session_id][category])]

# Modified Recommendation Functions
def get_mood_recommendations(mood, limit=10, session_id=None):
    global df
    print(f"Requested mood: {mood}")
    if not session_id:
        session_id = 'default'
    exact_mood_songs = df[df['mood'].str.lower() == mood.lower()]
    fresh_mood_songs = filter_history(exact_mood_songs, session_id, f"mood_{mood}")
    if len(fresh_mood_songs) < limit * 2:
        scored_songs = calculate_mood_score(exact_mood_songs, mood)
    else:
        scored_songs = calculate_mood_score(fresh_mood_songs, mood)
    
    # Sort by final score (which includes the random factor)
    sorted_songs = scored_songs.sort_values('final_score', ascending=False)
    if len(sorted_songs) < limit:
        all_songs_scored = calculate_mood_score(df, mood)
        fresh_songs = filter_history(all_songs_scored, session_id, f"mood_{mood}")
        sorted_songs = fresh_songs.sort_values('final_score', ascending=False)
    
    # Take the top recommendations
    recommendations = sorted_songs.head(limit)
    # Update history with these recommendations
    update_history(session_id, f"mood_{mood}", recommendations['track_id'].tolist())
    return recommendations[['track_id', 'track_name', 'artists', 'album_name', 
                            'popularity', 'track_genre', 'mood']].to_dict('records')


def search_songs(query, limit=10, session_id=None, search_type=None):
    global df
    if not session_id:
        session_id = 'default'
    query = query.lower()
    if search_type == 'artist':
        mask = df['artists'].str.lower().str.contains(query)
        category = f"artist_{query}"
    elif search_type == 'genre':
        mask = df['track_genre'].str.lower().str.contains(query)
        category = f"genre_{query}"
    else:
        mask = (df['track_name'].str.lower().str.contains(query) | 
                df['artists'].str.lower().str.contains(query) |
                df['track_genre'].str.lower().str.contains(query))
        category = f"search_{query}"
    matches = df[mask]
    
    # Filter out previously shown songs
    fresh_matches = filter_history(matches, session_id, category)
    if len(fresh_matches) < limit:
        results = matches.sort_values(['popularity', 'track_name'], ascending=[False, True]).head(limit)
    else:
        fresh_matches['random_factor'] = np.random.random(len(fresh_matches)) * 10
        fresh_matches['sort_score'] = fresh_matches['popularity'] + fresh_matches['random_factor']
        results = fresh_matches.sort_values('sort_score', ascending=False).head(limit)
    
    # Update history with these results
    update_history(session_id, category, results['track_id'].tolist())
    formatted_results = results[['track_id', 'track_name', 'artists', 'album_name', 
                                'popularity', 'track_genre', 'mood']].to_dict('records')
    return formatted_results

@app.route('/api/mood/<mood>')
def mood_endpoint(mood):
    """Endpoint for mood-based recommendations"""
    limit = request.args.get('limit', default=10, type=int)
    session_id = request.args.get('session_id', default=get_session_id())
    recommendations = get_mood_recommendations(mood, limit, session_id)
    return jsonify(recommendations)

@app.route('/api/search')
def search_endpoint():
    """Endpoint for searching songs"""
    query = request.args.get('q', default='', type=str)
    limit = request.args.get('limit', default=10, type=int)
    session_id = request.args.get('session_id', default=get_session_id())
    search_type = request.args.get('type', default=None, type=str)
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    results = search_songs(query, limit, session_id, search_type)
    return jsonify(results)

@app.route('/')
def home():
    """Serve the main application page"""
    return render_template('index.html')

# API run configuration
if __name__ == '__main__':
    # Load the dataset before starting the server
    load_data()
    # Run the Flask application
    app.run(debug=True, port=5000)