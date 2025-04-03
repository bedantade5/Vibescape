# Vibescape – A Mood-Based Music Recommender
### Vibescape is an intelligent music recommendation system that curates playlists based on user moods. By analyzing song attributes such as valence, energy, and danceability, the system provides tailored recommendations that align with emotional states. The platform also includes a search functionality for discovering songs based on specific artists or genres.

## Features
1. Mood-Based Recommendations – Users can select a mood (Happy, Sad, Energetic, or Relaxed) to receive a curated set of songs that match the selected emotion.
2. Intelligent Search – Supports keyword-based queries, allowing users to search for music using artist: or genre: filters.
3. Modern UI Design – The interface is designed with a sleek and futuristic aesthetic, ensuring an engaging user experience.
4. Mood Scoring System – The recommendation engine calculates mood scores based on key audio features to generate relevant song suggestions.
5. Efficient and Scalable – Developed using Flask for backend processing and HTML, CSS, and JavaScript for the frontend.

## Technology Stack
* Backend: Flask (Python)
* Frontend: HTML, CSS, JavaScript
* Database: SQLite (optional for user preferences)
* Dataset: Spotify Songs Dataset (sourced from Kaggle)

## How It Works
1. Mood Selection – Users choose a mood, and the system generates a playlist based on predefined mood parameters.
2. Song Recommendation – The backend applies a filtering algorithm to select and return ten songs that match the selected mood.
3. Search Functionality – Users can search for specific songs by providing queries such as artist: The Weeknd or genre: pop.
4. Playlist Exploration – The recommended songs are displayed in an intuitive interface, allowing users to explore and discover new music.

## Installation & Setup
Clone the Repository
```bash
git clone https://github.com/your-username/vibescape.git
cd vibescape
```
Install Dependencies
```bash
pip install -r requirements.txt
```
Run the Flask Server
```bash
python app.py
```
Once started, the application will be accessible at http://localhost:5000.

## Future Enhancements
1. Integration with Spotify API to fetch real-time song data
2. User Account System to enable personalized playlists and history tracking
3. Enhanced Genre Filtering for more refined recommendations

This project aims to provide a seamless and engaging music discovery experience through intelligent recommendations and an intuitive interface.
