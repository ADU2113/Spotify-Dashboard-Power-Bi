import requests
import pandas as pd

# Function to get Spotify access token
def get_spotify_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    response = requests.post(auth_url, data={
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    })
    
    if response.status_code != 200:
        print("Error fetching token:", response.json())
        return None
    
    return response.json().get('access_token')

# Function to search for a track and get its ID
def search_track(track_name, artist_name, token):
    query = f"{track_name} artist:{artist_name}"
    url = f"https://api.spotify.com/v1/search?q={requests.utils.quote(query)}&type=track"

    response = requests.get(url, headers={'Authorization': f'Bearer {token}'})
    json_data = response.json()

    try:
        return json_data['tracks']['items'][0]['id']
    except (KeyError, IndexError, TypeError):
        return None

# Function to get track details (album image URL)
def get_track_details(track_id, token):
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    response = requests.get(url, headers={'Authorization': f'Bearer {token}'})
    
    if response.status_code != 200:
        return None
    
    json_data = response.json()
    images = json_data.get('album', {}).get('images', [])
    return images[0]['url'] if images else None

# Your Spotify API Credentials
client_id = '6efcb4c87b534ab98b3faa11f89ea24e'
client_secret = '002f2657765e461e8e8146bb6b835ad8'

# Get Access Token
access_token = get_spotify_token(client_id, client_secret)

if access_token:
    # Read CSV file (update the file path as needed)
    df_spotify = pd.read_csv('spotify-2023.csv', encoding='ISO-8859-1')

    # Ensure 'image_url' column exists
    if 'image_url' not in df_spotify.columns:
        df_spotify['image_url'] = None

    # Loop through DataFrame to fetch track details
    for i, row in df_spotify.iterrows():
        track_id = search_track(row['track_name'], row['artist_name'], access_token)
        if track_id:
            df_spotify.at[i, 'image_url'] = get_track_details(track_id, access_token)

    # Save the updated DataFrame
    df_spotify.to_csv('updated_file.csv', index=False)
    print("Updated file saved as 'updated_file.csv'")
else:
    print("Failed to authenticate with Spotify API. Please check your credentials.")

