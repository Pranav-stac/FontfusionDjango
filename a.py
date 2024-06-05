import requests

# URL of the image_process_api endpoint
url = ' https://e100-2401-4900-1c2d-a7e9-e4b5-93a7-7b32-1b07.ngrok-free.app/image_process_api/'

# Path to the image files you want to send
image1_path = '10022.png'
image2_path = '10001.png'

# Prepare the files to be sent in the POST request
files = {
    'image1': open(image1_path, 'rb'),
    'image2': open(image2_path, 'rb')
}

# Send a POST request to the API endpoint
response = requests.post(url, files=files)

# Check the response from the API
if response.status_code == 200:
    # Request was successful
    output_image_data = response.json()['output_image']
    # Process the output_image_data as needed
else:
    # Request failed
    error_message = response.json()['error']
    print(f'Error: {error_message}')