import json, os, requests, subprocess

# Your Discogs username and API key
username = ''
api_key = ''

# The ID of the folder containing your collection
folder_id = 0

# Base URL for Discogs API
base_url = 'https://api.discogs.com'

# Endpoint for retrieving collection releases
endpoint = f'/users/{username}/collection/folders/{folder_id}/releases'

# Set up authentication headers
headers = {'User-Agent': 'MyDiscogsClient/1.0', 'Authorization': f'Discogs token={api_key}'}

# Make request to API
response = requests.get(base_url + endpoint, headers=headers)

directory = 'thumbs/'

# Make request to API and retrieve all pages of results
page = 1
thumbnails = []
while True:
    response = requests.get(base_url + endpoint, headers=headers, params={'page': page})
    response_data = response.json()
    # Extract album thumbnails from each release
    for release in response_data['releases']:
        # Check if release has an image and add it to the list of thumbnails
        if release['basic_information']['cover_image']:
            thumbnails.append(release['basic_information']['cover_image'])
    # Check if there are more pages of results
    if 'next' in response.links:
        page += 1
    else:
        break

for thumbnail in thumbnails:
    filename = thumbnail.split("/")[-1]
    file_path = f"{directory}{filename}"
    if os.path.isfile(file_path):
        print(f"{filename} already exists in {directory}")
    else:
        # Download the file using wget
        print(f"Downloading {filename} from {thumbnail} to {directory}")
        subprocess.run(['wget', '-P', directory, thumbnail])
