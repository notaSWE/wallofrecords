import boto3
import json
import os
import requests

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

def handler(event, context):
    # Try to get required environment variables
    try:
        api_key = os.environ['USER_API_KEY']
        bucket_name = os.environ['BUCKET_NAME']
        username = os.environ['USER_NAME']
    except:
        return {
            'statusCode': 400,
            'body': 'Failed to get environment variables'
        }

    # The ID of the folder containing your collection
    folder_id = 0

    # Lambda temp storage directory
    tempdir = '/tmp/'

    # Base URL for Discogs API
    base_url = 'https://api.discogs.com'

    # Endpoint for retrieving collection releases
    endpoint = f'/users/{username}/collection/folders/{folder_id}/releases'

    # Set up authentication headers
    headers = {'User-Agent': 'MyDiscogsClient/1.0', 'Authorization': f'Discogs token={api_key}'}

    # Keep track of number of album images
    im_count = 0

    # Make request to API; paginate if needed (pagination broken currently)
    page = 1
    thumbnails = []
    output = {}

    while True:
        response = requests.get(base_url + endpoint, headers=headers, params={'page': page})
        response_data = response.json()

        # Extract album thumbnails from each release
        for release in response_data['releases']:
            # Check if release has an image and add it to the list of thumbnails
            if release['basic_information']['cover_image']:
                url = release['basic_information']['cover_image']
                resource_url = release['basic_information']['resource_url']
                thumbnails.append(url)
                output[url] = resource_url               
        # Check if there are more pages of results
        if 'next' in response.links:
            page += 1
        else:
            break
    
    # Don't need the API key anymore
    headers = {'User-Agent': 'MyDiscogsClient/1.0'}

    for thumbnail in thumbnails:
        fname = thumbnail.split("/")[-1]
        # Check to see if thumbnail exists in thumbs/ and download if not
        try:
            s3_client.head_object(Bucket=bucket_name, Key=f'thumbs/{fname}')
        except:
            # Download the file from the URL to a file in /tmp/
            local_path = f'{tempdir}{fname}'
            with open(local_path, 'wb') as fileToWrite:
                response = requests.get(thumbnail, headers=headers)
                fileToWrite.write(response.content)

            # Upload the file to S3
            with open(local_path, 'rb') as fileToWrite:
                s3_client.put_object(Body=fileToWrite, Bucket=bucket_name, Key=f'thumbs/{fname}', ContentType='image/jpeg')

            # Remove the file from /tmp/
            os.remove(local_path)
            im_count += 1

    # Check to see if index.html exists in bucket; if not, check im_count and modify/upload to s3
    if im_count > 0:
        try:
            s3_client.head_object(Bucket=bucket_name, Key="index.html")
        except:
            # Set directory variable adhering to s3 bucket name
            thumbs_dir = f"https://{bucket_name}.s3.amazonaws.com/thumbs/"

            # Read the contents of your index.html file
            with open('index.html', 'r') as f:
                html = f.read()
            
            modified_html = html.replace("const bucketName = 'REPLACEWITHDYNAMICALLYNAMEDS3BUCKETNAME';", f"const bucketName = '{bucket_name}';")
            # Upload the modified HTML file to S3
            s3 = boto3.client('s3')
            s3.put_object(Body=modified_html, Bucket=bucket_name, Key='index.html', ContentType='text/html')
    else:
        print("No images written; index.html probably already exists.")

    return {
        'statusCode': 200,
    }