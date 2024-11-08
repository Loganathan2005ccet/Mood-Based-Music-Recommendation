import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from transformers import pipeline
import plotly.graph_objects as go
import sqlite3
import random
from textblob import TextBlob
import hashlib



SPOTIPY_CLIENT_ID = '91e7e71cd8884100a4aab594b72cd21f'
SPOTIPY_CLIENT_SECRET = '2809a68c966e4ac1a8d68f90a0e7a929'
SPOTIPY_REDIRECT_URI = 'http://localhost:8501/'



auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)


conn = sqlite3.connect('new_user_data.db')
c = conn.cursor()


c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    phone TEXT,
    email TEXT,
    password TEXT,
    mood TEXT
)
''')
conn.commit()


ADMIN_USERNAME = "ADMIN"
ADMIN_PASSWORD_HASH = hashlib.sha256("password".encode()).hexdigest() 


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, phone, email, password):
    try:
        c.execute("INSERT INTO users (username, phone, email, password) VALUES (?, ?, ?, ?)",
                  (username, phone, email, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    if result and result[0] == hash_password(password):
        return True
    return False


def login_admin(username, password):
    return username == ADMIN_USERNAME and hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD_HASH



st.sidebar.title("Authentication")
auth_option = st.sidebar.selectbox("Choose an option", ["Login", "Sign Up", "Admin Login"])

if auth_option == "Sign Up":
    st.sidebar.subheader("Create an Account")
    username = st.sidebar.text_input("Username")
    phone = st.sidebar.text_input("Phone Number")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type='password')
    
    if st.sidebar.button("Sign Up"):
        if register_user(username, phone, email, password):
            st.sidebar.success("User  registered successfully!")
        else:
            st.sidebar.error("Username already exists!")

elif auth_option == "Login":
    st.sidebar.subheader("User  Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type='password')
    
    if st.sidebar.button("Login"):
        if login_user(username, password):
            st.session_state.username = username
            st.success(f"Welcome {username}!")
        else:
            st.error("Invalid username or password!")

elif auth_option == "Admin Login":
    st.sidebar.subheader("Admin Login")
    username = st.sidebar.text_input("Admin Username")
    password = st.sidebar.text_input("Admin Password", type='password')
    
    if st.sidebar.button("Login"):
        if login_admin(username, password):
            st.session_state.admin_logged_in = True
            st.success("Admin logged in successfully!")
        else:
            st.error("Invalid admin credentials!")


if 'username' in st.session_state:
    st.write(f"### Welcome to your dashboard, {st.session_state.username}!")

    mood_genre_map = {
        'happy': ['pop', 'dance', 'party'],
        'sad': ['blues', 'classical', 'soft rock'],
        'excited': ['rock', 'edm', 'hip hop'],
        'relaxed': ['jazz', 'acoustic', 'chill'],
        'angry': ['metal', 'punk', 'rock'],
        'romantic': ['soul', 'R&B', 'soft rock'],
        'nostalgic': ['oldies', 'classical', 'country'],
    }

    
    sentiment_analysis_pipeline = pipeline("sentiment-analysis")

    
    mood_features_map = {
        'happy': {
            'valence': 0.95, 
            'energy': 0.85, 
            'danceability': 0.8, 
            'tempo': 130, 
            'loudness': -4, 
            'acousticness': 0.15, 
            'speechiness': 0.05, 
            'liveness': 0.35, 
            'instrumentalness': 0.0, 
            'key': 5, 
            'mode': 1,  
            'harmonic_complexity': 0.6,  
            'perceived_intensity': 0.8  
        },
        'sad': {
            'valence': 0.15, 
            'energy': 0.1, 
            'danceability': 0.4, 
            'tempo': 60, 
            'loudness': -12, 
            'acousticness': 0.8, 
            'speechiness': 0.03, 
            'liveness': 0.15, 
            'instrumentalness': 0.6, 
            'key': 2, 
            'mode': 0,  
            'harmonic_complexity': 0.8,
            'perceived_intensity': 0.3
        },'excited': {
        'valence': 0.85, 
        'energy': 0.98, 
        'danceability': 0.9, 
        'tempo': 150, 
        'loudness': -2, 
        'acousticness': 0.1, 
        'speechiness': 0.1, 
        'liveness': 0.5, 
        'instrumentalness': 0.0, 
        'key': 9, 
        'mode': 1, 
        'harmonic_complexity': 0.5,
        'perceived_intensity': 0.95
    },
    'relaxed': {
        'valence': 0.65, 
        'energy': 0.4, 
        'danceability': 0.6, 
        'tempo': 85, 
        'loudness': -6, 
        'acousticness': 0.9, 
        'speechiness': 0.02, 
        'liveness': 0.25, 
        'instrumentalness': 0.3, 
        'key': 4, 
        'mode': 1, 
        'harmonic_complexity': 0.4,
        'perceived_intensity': 0.4
    },
    'angry': {
        'valence': 0.35, 
        'energy': 0.9, 
        'danceability': 0.75, 
        'tempo': 140, 
        'loudness': -1, 
        'acousticness': 0.05, 
        'speechiness': 0.07, 
        'liveness': 0.4, 
        'instrumentalness': 0.0, 
        'key': 7, 
        'mode': 0, 
        'harmonic_complexity': 0.7,
        'perceived_intensity': 0.9
    },
    'romantic': {
        'valence': 0.85, 
        'energy': 0.55, 
        'danceability': 0.6, 
        'tempo': 95, 
        'loudness': -5, 
        'acousticness': 0.7, 
        'speechiness': 0.04, 
        'liveness': 0.25, 
        'instrumentalness': 0.05, 
        'key': 1, 
        'mode': 1, 
        'harmonic_complexity': 0.6,
        'perceived_intensity': 0.65
    },
    'nostalgic': {
        'valence': 0.7, 
        'energy': 0.45, 
        'danceability': 0.5, 
        'tempo': 90, 
        'loudness': -7, 
        'acousticness': 0.9, 
        'speechiness': 0.04, 
        'liveness': 0.3, 
        'instrumentalness': 0.25, 
        'key': 6, 
        'mode': 0, 
        'harmonic_complexity': 0.7,
        'perceived_intensity': 0.45
    },
    'focused': {
        'valence': 0.6, 
        'energy': 0.7, 
        'danceability': 0.65, 
        'tempo': 115, 
        'loudness': -3, 
        'acousticness': 0.3, 
        'speechiness': 0.03, 
        'liveness': 0.2, 
        'instrumentalness': 0.35, 
        'key': 8, 
        'mode': 1, 
        'harmonic_complexity': 0.55,
        'perceived_intensity': 0.6
    },
    'confident': {
        'valence': 0.75, 
        'energy': 0.85, 
        'danceability': 0.75, 
        'tempo': 125, 
        'loudness': -2, 
        'acousticness': 0.25, 
        'speechiness': 0.06, 
        'liveness': 0.4, 
        'instrumentalness': 0.05, 
        'key': 9, 
        'mode': 1, 
        'harmonic_complexity': 0.65,
        'perceived_intensity': 0.75
    },
    'calm': {
        'valence': 0.55, 
        'energy': 0.35, 
        'danceability': 0.5, 
        'tempo': 80, 
        'loudness': -9, 
        'acousticness': 0.85, 
        'speechiness': 0.02, 
        'liveness': 0.2, 
        'instrumentalness': 0.4, 
        'key': 3, 
        'mode': 1, 
        'harmonic_complexity': 0.5,
        'perceived_intensity': 0.35
    }
    
    }

    
    def enhanced_analyze_feelings(user_feelings):
        analysis_advanced = sentiment_analysis_pipeline(user_feelings)
        mood_detected = 'neutral'

        
        if analysis_advanced[0]['label'] == 'POSITIVE':
            mood_detected = 'happy'
        elif analysis_advanced[0]['label'] == 'NEGATIVE':
            mood_detected = 'sad'
    
    
        elif 'exciting' in user_feelings.lower() or 'thrilled' in user_feelings.lower():
           mood_detected = 'excited'
        elif 'relax' in user_feelings.lower() or 'calm' in user_feelings.lower():
             mood_detected = 'relaxed'
        elif 'angry' in user_feelings.lower() or 'furious' in user_feelings.lower():
             mood_detected = 'angry'
        elif 'love' in user_feelings.lower() or 'romantic' in user_feelings.lower():
             mood_detected = 'romantic'
        elif 'remember' in user_feelings.lower() or 'nostalgia' in user_feelings.lower():
            mood_detected = 'nostalgic'
        else:
            mood_detected='relaxed'







        

       
        print("Detected Mood:", mood_detected)
        return mood_detected

    # Function to create a speedometer gauge
    def create_speedometer(mood):
        mood_scores = {
            'happy': 80,
            'excited': 100,
            'relaxed': 70,
            'sad': 30,
            'angry': 20,
            'romantic': 60,
            'nostalgic': 50,
            'neutral': 40,
        }

    
        score = mood_scores.get(mood, 0)

        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': f'Mood Intensity: {mood.capitalize()}'},
            gauge={
                'axis': {'range': [0 , 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 25], 'color': 'red'},
                    {'range': [25, 50], 'color': 'yellow'},
                    {'range': [50, 75], 'color': 'lightgreen'},
                    {'range': [75, 100], 'color': 'green'},
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': score
                }
            }
        ))

        return fig  

    
    def get_age_group(age):
        if age < 13:
            return 'child'
        elif age < 18:
            return 'teen'
        elif age < 30:
            return 'young adult'
        elif age < 45:
            return 'adult'
        elif age < 60:
            return 'middle-aged'
        else:
            return 'senior'

    
    age_genre_map = {
        'child': ['children', 'animated'],
        'teen': ['pop', 'hip hop', 'k-pop'],
        'young adult': ['rock', 'edm', 'indie'],
        'adult': ['jazz', 'blues', 'soul'],
        'middle-aged': ['classic rock', 'soft rock', 'country'],
        'senior': ['oldies', 'classical', 'nostalgic']
    }

    
    language_artists_map = {
        'English': [
            'https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4',  
            'https://open.spotify.com/artist/1uNFoZAHBGtllmzznpCI3s',  
            'https://open.spotify.com/artist/6eUKZXaKkcviH0Ku9w2n3V', 
            'https://open.spotify.com/artist/66CXWjxzNUsdJxJ2JdwvnR',  
        ],'Hindi': [
        'https://open.spotify.com/artist/5f4QpKfy7ptCHwTqspnSJI',   
        'https://open.spotify.com/artist/1wRPtKGflJrBx9BmLsSwlU',  
        'https://open.spotify.com/artist/3TLpT1Jz5kKBLkxtnInC9z',
        'https://open.spotify.com/artist/4o8RzJ9Ksj5mj25byyUlKz',  
        'https://open.spotify.com/artist/4YXycRbyyAE0wozTk7QMEq', 
           ],
         'Tamil': [
        'https://open.spotify.com/artist/6AiX12wXdXFoGJ2vk8zBjy',  
        'https://open.spotify.com/artist/1VX5VW0BEaWYlJwA7k6J9n',
        'https://open.spotify.com/artist/4udfTWwtZsXa9peEt8qrN1',  
        'https://open.spotify.com/artist/3PeHfG9GK1eDFwlFnyIEYk', 
        'https://open.spotify.com/artist/7ceIhLzBzjuY42cBLQl3oa',  
       ],
        'Telugu': [
        'https://open.spotify.com/artist/7qjJw7ZM2ekDSahLXPjIlN?si=h8nzxQMiTCOqiZE-0Mupqw',  
        'https://open.spotify.com/artist/5sSzCxHtgL82pYDvx2QyEU?si=fZ_sRPa1SNeI212PY3UNOA',  
        'https://open.spotify.com/artist/4IKVDbCSBTxBeAsMKjAuTs?si=ccf6b114e9674880',  
        'https://open.spotify.com/artist/2ae6PxICSOZHvjqiCcgon8?si=36de93f9debd4811',  
        'https://open.spotify.com/artist/12l1SqSNsg2mI2IcXpPWjR?si=2412d7524f58415f',
        ],
        'Kannada': [
        'https://open.spotify.com/artist/4iA6bUhiZyvRKJf4FNVX39?si=AIoAvzBiSVaj6yU_GP9dwQ',  
        'https://open.spotify.com/artist/3IX32wm6CoEIYovZ0VcjBJ?si=746ed5f99ac94d3c',
        'https://open.spotify.com/artist/0ZnBmsYz6ImvXdfUglJEWA?si=5a2ef79e796a4e39',
        'https://open.spotify.com/artist/0oOet2f43PA68X5RxKobEy?si=a2153744982a4554', 
        'https://open.spotify.com/artist/002yVW3Yn595KWy74buQ1k?si=d57b0d3194a341a2',  
          ],
          'Malayalam': [
        'https://open.spotify.com/artist/4JXqxFqi9dxlsiXKZhKvzB?si=b4ae2289fa194bc3',  
        'https://open.spotify.com/artist/2wPsNCwhEGb0KvChZ5DD52?si=4926f51a7d4b4925',  
        'https://open.spotify.com/artist/2oJbFGuxu5d9xvez6yHvFh?si=54c4654f22b544fe',  
        'https://open.spotify.com/artist/2NoJ7NuNs9nyj8Thoh1kbu?si=e393d74bbc094b23',  
        'https://open.spotify.com/artist/4xlqU0G9EloUPHL1qlmWY6?si=025cd9ed52814fe2', 
           ],
         'Bengali': [
        'https://open.spotify.com/artist/4YRxDV8wJFPHPTeXepOstw?si=f1601366e7fa40d4',  
        'https://open.spotify.com/artist/2kkQthS9OLpK4UqNWYqoVl?si=1712ff4b567644dc',  
        'https://open.spotify.com/artist/5LZ894xYE9MG1sal0gjt5L?si=0a11bfb391e1425e',
        'https://open.spotify.com/artist/5LZ894xYE9MG1sal0gjt5L?si=3ea35e7227dd4ca9', 
        'https://open.spotify.com/artist/7gjiYwM6O5sNuYBaCdpCXA?si=d06a9d8d4c30476f', 
         ], 
         'Punjabi': [
        'https://open.spotify.com/artist/4PULA4EFzYTrxYvOVlwpiQ?si=d18f8b4496644c4a',  
        'https://open.spotify.com/artist/6LEG9Ld1aLImEFEVHdWNSB?si=9d27c28687e541d0', 
        'https://open.spotify.com/artist/2FKWNmZWDBZR4dE5KX4plR?si=fffc8f5cae1643c9',  
        'https://open.spotify.com/artist/2RlWC7XKizSOsZ8F3uGi59?si=fdc1693153b348e9',  
        'https://open.spotify.com/artist/56SjZARoEvag3RoKWIb16j?si=7e523694416d45b7', 
         ],
         'Marathi': [
        'https://open.spotify.com/artist/5fvTHKKzW44A9867nPDocM?si=dc0124f70ea74b63',  
        'https://open.spotify.com/artist/6mxY3ekITToaEK2XGtaock?si=ee11126ea0dd4fa3',  
        'https://open.spotify.com/artist/1SJOL9HJ08YOn92lFcYf8a?si=61f54fa0ba1342d5',  
        'https://open.spotify.com/artist/4B9efXsA6sv4w3vts8E0T7?si=21fd585a21fa4f67'
        'https://open.spotify.com/artist/2zGP2SUtwsDhdyYzf0kKp8?si=060d9e7308ec4bb3',
          ],
         'Gujarati': [
        'https://open.spotify.com/artist/1SJOL9HJ08YOn92lFcYf8a?si=61f54fa0ba1342d5',  
        'https://open.spotify.com/artist/7MAlFea251zaprQFjwvYaL?si=164ea31fb4c54944', 
        'https://open.spotify.com/artist/26qILArN7gTOjFRTbOTKbJ?si=c6f3ce5b41b74651',  
        'https://open.spotify.com/artist/2Hms1YhTKaXQ5yZPGKztXe',  
        'https://open.spotify.com/artist/6SLyfZLFgTmvDJh8XhzESU?si=2c5273a79d694ff6',  
          ],
        'French': [
        'https://open.spotify.com/artist/1CoZyIxLU3rDq3SnE8wVtw',  
        'https://open.spotify.com/artist/2SOB6LNBtdcFfwDkSMthF6',  
        'https://open.spotify.com/artist/7o46KLY6Fq8nT4Gx4G7M3B',  
        'https://open.spotify.com/artist/2k74oP4c4bP0o4PtEDU8bT',  
        'https://open.spotify.com/artist/4kT1TpDFl0zmEtAn2kVDAH',
           ],
         'Spanish': [
        'https://open.spotify.com/artist/1mcTU81TzQhprhouKaTkpq',  
        'https://open.spotify.com/artist/4tZ0Vf1azXrIhK1RlGznpB', 
        'https://open.spotify.com/artist/6G2I01zGXLUAMzWzOENkpK',  
        'https://open.spotify.com/artist/2ZZFj75Ip4Emi1cK0tM7KA',  
        'https://open.spotify.com/artist/6l8qDku5BbYYBWkMf1jQz1',  
         ],
        'German': [
        'https://open.spotify.com/artist/5K4W6rqBFWDnAN6FQUkS6x',  
        'https://open.spotify.com/artist/2IZgYxi5Vm8hvTHf7nJY3D',  
        'https://open.spotify.com/artist/5t4V0LFqojL5DRh0ST7tUk',  
        'https://open.spotify.com/artist/1UuM4u7Oq0RXiHwc6b0zZF',  
        'https://open.spotify.com/artist/0w9cmYbwMw7hNOFLK0g5mv',  
        ],
        'Brazilian Portuguese': [
        'https://open.spotify.com/artist/7tYKF4w9nC0nq9CsPZTHyP',  
        'https://open.spotify.com/artist/1Nq2GRoaB5AqGEjSBcYJW3', 
        'https://open.spotify.com/artist/3yUOLpRnsuW3RCbT3pTnbW', 
        'https://open.spotify.com/artist/6UjHAlHg3D5Gh2UBhbANHo', 
        'https://open.spotify.com/artist/5g8wE2IN7cYjZgB9IfA7U6',
         ],
      'Japanese': [
        'https://open.spotify.com/artist/1snhtMLeb2DYoMOcVbb8iB',  
        'https://open.spotify.com/artist/6T3F5Nf3Q3eYRV3KnqO6jC',  
        'https://open.spotify.com/artist/5b9k8uW4hN1KpQ28qqf7xH',  
        'https://open.spotify.com/artist/2auG9R2ZGO3I4WKh36P6Rp', 
        'https://open.spotify.com/artist/1lX0rxhKZBSWuEpZOWxwjh',  
        ],
    'tamilplaylists' : [
    "https://open.spotify.com/playlist/37i9dQZF1DX3bcfiyW6qms",
    "https://open.spotify.com/playlist/5UdcJ7mmkUt7Bue4I8zYLq",
    "https://open.spotify.com/playlist/51hmVNeZVcZQKaSecPoLs0",
    "https://open.spotify.com/playlist/37i9dQZF1DWZp7pYV7ceWl",
    "https://open.spotify.com/playlist/3jj4SEwNkDB2nAIKB5qkmq",
    "https://open.spotify.com/playlist/1b28eTgS0RGdVPFVCkcR2w",
    "https://open.spotify.com/playlist/4DBKi4I9pyydqhSOMD4qrt",
    "https://open.spotify.com/playlist/5H3oyhUA8mQ6dBZcdBwQOu",
    "https://open.spotify.com/playlist/2NPhFMYq9PukheULjcxXNr"
       ]
       
    }

    tamil_playlists = [
        "https://open.spotify.com/playlist/37i9dQZF1DX3bcfiyW6qms",
        "https://open.spotify.com/playlist/5UdcJ7mmkUt7Bue4I8zYLq",
        "https://open.spotify.com/playlist/51hmVNeZVcZQKaSecPoLs0",
        "https://open.spotify.com/playlist/37i9dQZF1DWZp7pYV7ceWl",
        "https://open.spotify.com/playlist/3jj4SEwNkDB2nAIKB5qkmq",
        "https://open.spotify.com/playlist/1b28eTgS0RGdVPFVCkcR2w",
        "https://open.spotify.com/playlist/4DBKi4I9pyydqhSOMD4qrt",
        "https://open.spotify.com/playlist/5H3oyhUA8mQ6dBZcdBwQOu",
        "https://open.spotify.com/playlist/2NPhFMYq9PukheULjcxXNr"
    ]

    
    def fetch_tracks_from_playlist(playlist_url):
        try:
        
            if "playlist" in playlist_url:
                playlist_id = playlist_url.split("/")[-1].split("?")[0]
            else:
                st.write("Invalid playlist URL.")
                return []

            results = sp.playlist_tracks(playlist_id)
            tracks = []
            for item in results['items']:
                track = item['track']
                if track:  
                    track_info = {
                        'name': track['name'],
                        'artist': track['artists'][0]['name'],
                        'url': track['external_urls']['spotify'],
                        'preview': track['preview_url'],
                        'popularity': track['popularity'],
                        'release_date': track['album']['release_date'],
                        'album_art': track['album']['images'][0]['url']
                    }
                    tracks.append(track_info)
            return tracks
        except Exception as e:
            st.write(f"Error fetching tracks from playlist: {e}")
            return []

    
    def get_enhanced_recommendations(mood, language, region, age):
    
        if mood.lower() == "sad" and language.lower() == "tamil":
            st.write(f"**Recommending Tamil songs based on your {mood} mood:**")
            random_playlist = random.choice(tamil_playlists)
            return fetch_tracks_from_playlist(random_playlist)

        
        mood_features = mood_features_map.get(mood)
        genre = random.choice(mood_genre_map[mood])

        age_group = get_age_group(age)
        age_genres = age_genre_map.get(age_group, [])

        seed_artists = language_artists_map.get(language, None)
        recommendations = None

        
        if seed_artists:
            try:
                recommendations = sp.recommendations(seed_artists=seed_artists, limit=50, market=region, **mood_features)
            except Exception as e:
                st.write(f"Error fetching recommendations with seed artists: {e}")

    
        if not recommendations or not recommendations['tracks']:
            try:
                recommendations = sp.recommendations(seed_genres=age_genres + [genre], limit=5, market=region, **mood_features)
            except Exception as e:
                st.write(f"Error fetching recommendations with seed genres: {e}")

        songs = []
        if recommendations and recommendations['tracks']:
            for track in recommendations['tracks']:
                song_data = {
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album_art': track['album']['images'][0]['url'],
                    'url': track['external_urls']['spotify'],
                    'preview': track['preview_url'],
                    'popularity': track['popularity'],
                    'release_date': track['album']['release_date']
                }
                songs.append(song_data)
        else:
            st.write("No recommendations available for the selected mood, language, and age.")

        return songs

    # Streamlit application layout
    st.title("Mood-Based Music Recommendation 🎵🔊🎧")

    # User input for feelings
    if 'user_feelings' not in st.session_state:
        st.session_state.user_feelings = ""
    if 'detected_mood' not in st.session_state:
        st.session_state.detected_mood = None

    st.session_state.user_feelings = st.text_area("Describe your feelings:", height=150, value=st.session_state.user_feelings)

    
    age = st.slider("Select your age:", 0, 100, 25)  

    
    if st.button('Analyze Feelings'):
        with st.spinner('Analyzing your feelings...'):
            st.session_state.detected_mood = enhanced_analyze_feelings(st.session_state.user_feelings)

        
        if st.session_state.detected_mood:
            fig = create_speedometer(st.session_state.detected_mood)
            st.plotly_chart(fig)

    
    languages = {
        'English': 'US',
        'Hindi': 'IN',
        'Tamil': 'IN',
        'Telugu': 'IN',
        'Kannada': 'IN',
        'Malayalam': 'IN',
        'Bengali': 'IN',
        'Punjabi': 'IN',
        'Marathi': 'IN',
        'Gujarati': 'IN',
        'French': 'FR',
        'Spanish': 'ES',
        'German': 'DE',
        'Brazilian Portuguese': 'BR',
        'Japanese': 'JP'
    }

    selected_language = st.selectbox("Select language/market for recommendations:", list(languages.keys()))

    
    if st.session_state.detected_mood:
        region_code = languages[selected_language]
        recommendations = get_enhanced_recommendations(st.session_state.detected_mood, selected_language, region_code, age)

        st.write(f"### Recommended Songs for {st.session_state.detected_mood.capitalize()} mood in {selected_language}:")
        
        for song in recommendations:
            st.image(song['album_art'], width=200)
            st.write(f"**{song['name']}** by {song['artist']}")
            st.write(f"[Listen on Spotify]({song['url']})")
            if song['preview']:
                st.audio(song['preview'])
            st.write(f"Popularity: {song['popularity']}, Released on: {song['release_date']}")
            st.write("---")

    
    st.sidebar.title("Additional Features")

    
    feedback = st.sidebar.text_area("Provide Feedback:", height=100)
    if st.sidebar.button("Submit Feedback"):
        if feedback:
            st.sidebar.success("Thank you for your feedback!")
        else:
            st.sidebar.warning("Please enter your feedback before submitting.")

    
    st.sidebar.subheader("Tips for Better Recommendations")
    st.sidebar.write("1. Be descriptive about your feelings.")
    st.sidebar.write("2. Use emotions or specific words to convey your mood.")
    st.sidebar.write("3. You can always try again with different inputs for varied results.")

    st.sidebar.subheader("For Voice Input")
    st.sidebar.write("1. Click the text box.")
    st.sidebar.write("2. Press Windows Key + H")
elif 'admin_logged_in' in st.session_state and st.session_state.admin_logged_in:
    st.write("### Admin Dashboard")
    st.write("Here you can manage users and view statistics.")
    
    
    st.subheader("User  Data")
    c.execute("SELECT username, phone, email, mood FROM users")
    users = c.fetchall()
    
    if users:
        for user in users:
            st.write(f"**Username:** {user[0]}, **Phone:** {user[1]}, **Email:** {user[2]}, **Mood:** {user[3]}")
    else:
        st.write("No users found.")

else:
    st.write("Please log in or sign up to access the application.")