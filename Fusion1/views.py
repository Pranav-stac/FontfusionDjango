import json
import os
import string
from django.conf import settings
from django.http import JsonResponse
from PIL import Image
import numpy as np
import torch
import base64
import io
import random
from .models_pytorch import get_latent, get_demo
import matplotlib.pyplot as plt
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from rest_framework import viewsets
from .models import FontModel
from .serializers import FontModelSerializer
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from PIL import Image
import numpy as np
import torch
from django.http import FileResponse
from django.conf import settings
from django.http import FileResponse, HttpResponseNotFound
from django.conf import settings
from PIL import Image
import os
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

import base64
import io
from .models_pytorch import Encoder, Decoder, get_latent, get_demo, plotter, get_predictions
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer

class UserCreate(APIView):
       def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
       def post(self, request):
           username = request.data.get('username')
           password = request.data.get('password')
           user = authenticate(username=username, password=password)
           if user:
               token, _ = Token.objects.get_or_create(user=user)
               return Response({'token': token.key})
           return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)





def handle_uploaded_image(image_file):
    """Process an uploaded image file and invert colors."""
    img = Image.open(image_file)
    img = img.convert('L')  # Convert to grayscale
    img = img.resize((64, 64))  # Resize image

    # Invert colors
    img = 255 - np.array(img)

    img = img.reshape(1, 1, 64, 64) / 270  # Normalize and reshape
    return img





@csrf_exempt
def find_image_path(image_name):
    """Find the path of an image by its name."""
    fonts_folder = os.path.join(settings.BASE_DIR, 'Fusion1', 'Fonts(New)')
    image_path = os.path.join(fonts_folder, image_name)
    return image_path if os.path.exists(image_path) else None


# def image_process_view(request):
#     if request.method == 'POST':
#         text_inputs = [request.POST.get('image1'), request.POST.get('image2')]

#         # Find image paths corresponding to the text inputs
#         image_paths = [find_image_path(name + '.png') for name in text_inputs]

#         # Check if all images are found
#         if None in image_paths:
#             return JsonResponse({'error': 'Could not find image(s) for the given text input(s)'}, status=400)

#         # Load and process images
#         images = [handle_uploaded_image(open(image_path, 'rb')) for image_path in image_paths]

#         with torch.no_grad():
#             latent = sum([get_latent(torch.tensor(im).float()) for im in images]) / len(images)
#             pred = get_demo(latent)
#             output_images = [Image.fromarray((img.numpy().squeeze() * 255).astype(np.uint8)) for img in pred]

#             # Convert output images to base64 to embed in HTML
#             encoded_imgs = []
#             for img in output_images:
#                 buffered = io.BytesIO()
#                 img.save(buffered, format="PNG")
#                 img_str = base64.b64encode(buffered.getvalue()).decode()
#                 encoded_imgs.append(img_str)

#             return render(request, 'image_output.html', {'images': encoded_imgs})
#     else:
#         return render(request, 'upload.html')

# @api_view(['POST'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def image_process_api(request):
#     if request.method == 'POST':
#         text_inputs = [request.POST.get('image1'), request.POST.get('image2')]
        
#         # Validate if both text inputs are provided
#         if None in text_inputs:
#             return JsonResponse({'error': 'Both text1 and text2 inputs are required'}, status=400)
        
#         # Find image paths corresponding to the text inputs
#         image_paths = [find_image_path(name + '.png') for name in text_inputs]

#         # Check if all images are found
#         if None in image_paths:
#             return JsonResponse({'error': 'Could not find image(s) for the given text input(s)'}, status=400)

#         # Load and process images
#         images = [handle_uploaded_image(open(image_path, 'rb')) for image_path in image_paths]

#         with torch.no_grad():
#             latent = sum([get_latent(torch.tensor(im).float()) for im in images]) / len(images)
#             pred = get_demo(latent)
#             output_images = [Image.fromarray(255 - (img.numpy().squeeze() * 255).astype(np.uint8)) for img in pred]  # Invert colors

#             # Save output images to the 'PngNew' folder
#             output_folder = os.path.join(settings.BASE_DIR, 'PngNew')
#             if not os.path.exists(output_folder):
#                 os.makedirs(output_folder)

#             for idx, img in enumerate(output_images):
#                 image_path = os.path.join(output_folder, f'char_{idx}.png')
#                 img.save(image_path, format="PNG")

#             # Now place these images onto a template
#             template_path = "WhatsApp Image 2024-06-18 at 12.56.32 PM.jpeg"  # Adjust this path as needed
#             output_template_path = os.path.join(settings.BASE_DIR, 'output_template.png')
#             # place_letters_on_template(template_path, output_folder, output_template_path)

#             # Optionally convert to base64 to send in JSON
#             encoded_imgs = []
#             for idx, img in enumerate(output_images):
#                 buffered = io.BytesIO()
#                 img.save(buffered, format="PNG")
#                 img_str = base64.b64encode(buffered.getvalue()).decode()
#                 encoded_imgs.append(img_str)

#             return JsonResponse({'output_images': encoded_imgs})






from queue import Queue

# Create a queue to manage user requests sequentially
user_queue = Queue()
processing = False
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def send_font_file(request):
    user_id = request.user.id
    template_path = os.path.abspath(os.path.join(settings.MEDIA_ROOT, f"user_{user_id}_output_template.png"))
    print(f"Template path: {template_path}")

    generated_font_path = download_font(template_path)
    if generated_font_path:
        base, _ = os.path.splitext(generated_font_path)
        ttf_font_path = f"{base}.ttf"
        os.rename(generated_font_path, ttf_font_path)
        print(f"Renamed font file to: {ttf_font_path}")

        if os.path.exists(ttf_font_path):
            print(f"Font file found: {ttf_font_path}")
            return FileResponse(open(ttf_font_path, 'rb'), as_attachment=True, content_type='font/ttf')
        else:
            print("Font file not found after renaming.")
            return HttpResponseNotFound('The requested font file was not found after generation.')
    else:
        print("Failed to generate the font file.")
        return JsonResponse({'error': 'Failed to generate the font file'}, status=500)
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def image_process_api(request):
    if request.method == 'POST':
        user_id = request.user.id  # Assuming the user is authenticated
        output_file_path = os.path.join(settings.MEDIA_ROOT, f"user_{user_id}_output_template.png")

        text_inputs = [request.POST.get('image1'), request.POST.get('image2')]
        
        if None in text_inputs:
            return JsonResponse({'error': 'Both image1 and image2 inputs are required'}, status=400)
        
        image_paths = [find_image_path(name + '.png') for name in text_inputs]
        if None in image_paths:
            return JsonResponse({'error': 'Could not find image(s) for the given text input(s)'}, status=400)

        images = [handle_uploaded_image(open(image_path, 'rb')) for image_path in image_paths]
        output_images = []

        with torch.no_grad():
            latent = sum([get_latent(torch.tensor(im).float()) for im in images]) / len(images)
            pred = get_demo(latent)
            for img in pred:
                img_array = 255 - (img.numpy().squeeze() * 255).astype(np.uint8)
                img_pil = Image.fromarray(img_array)
                output_images.append(img_pil)

        # Save output images to the 'PngNew' folder
        output_folder = os.path.join(settings.BASE_DIR, 'PngNew')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for idx, img in enumerate(output_images):
            image_path = os.path.join(output_folder, f'char_{idx}.png')
            img.save(image_path, format="PNG")

        # Now place these images onto a template
        template_path = "WhatsApp Image 2024-06-18 at 12.56.32 PM.jpeg"  # Adjust this path as needed
        place_letters_on_template(template_path, output_folder, output_file_path)

        # Optionally convert to base64 to send in JSON
        encoded_imgs = []
        for idx, img in enumerate(output_images):
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            encoded_imgs.append(img_str)

        return JsonResponse({'file_path': output_file_path, 'output_images': encoded_imgs})
    else:
        return JsonResponse({'error': 'This endpoint only supports POST requests'}, status=405)

def escape_latex(text):
    """
    Escapes LaTeX special characters in the given text.
    """
    # List of LaTeX special characters that need to be escaped
    special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '[': r'\[',
        ']': r'\]',
        '"': r"''",
        '\\': r'\textbackslash{}',
        '~': r'\textasciitilde{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
        '^': r'\textasciicircum{}',
        '`': r'\textasciigrave{}'
    }
    # Replace each special character with its escaped version
    for key, value in special_chars.items():
        text = text.replace(key, value)
    return text

def convert_text_to_latex(text):
    """
    Converts plain text to a simple LaTeX document.
    """
    # Escape LaTeX special characters
    escaped_text = escape_latex(text)

    # Wrap the text in a basic LaTeX document structure
    latex_document = f"""
\\documentclass{{article}}
\\usepackage{{fontspec}}


\\newfontface\\customfont[Path=./FontFusion/Fusion1/Unconfirmed 831238.ttf]{{Unconfirmed 831238}}

\\begin{{document}}

{escaped_text}

\\end{{document}}
    """
    return latex_document

# Example usage


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def convert_to_latex(request):
    # Extract text from POST request
    try:
        data = json.loads(request.body)
        text = data['text']
    except (KeyError, json.JSONDecodeError) as e:
        return JsonResponse({'error': 'Invalid input data'}, status=400)

    # Convert text to LaTeX
    latex = convert_text_to_latex(text)

    # Return LaTeX code
    if latex:
        return JsonResponse({'latex': latex})
    else:
        return JsonResponse({'error': 'Failed to convert text to LaTeX'}, status=500)
@csrf_exempt
def send_random_font_file(request):
    # Define the directory where the font files are stored
    fonts_dir = os.path.join(settings.BASE_DIR, 'Fusion1', 'TTF')

    # Check if the directory exists and get the list of .ttf files
    if os.path.exists(fonts_dir):
        font_files = [f for f in os.listdir(fonts_dir) if f.endswith('.ttf')]
        if font_files:
            # Select a random font file
            random_font_file = random.choice(font_files)
            font_file_path = os.path.join(fonts_dir, random_font_file)

            # Send the selected font file
            return FileResponse(open(font_file_path, 'rb'), as_attachment=True, content_type='font/ttf')
        else:
            return HttpResponseNotFound('No font files found in the directory.')
    else:
        return HttpResponseNotFound('The specified font directory does not exist.')    

def place_letters_on_template(template_path, letters_folder, output_path):
    # Load the template
    template = Image.open(template_path)

    # Dimensions of each cell (you might need to adjust these)
    cell_width, cell_height = 140, 140  # Example dimensions

    # Starting positions of the first cell (you might need to adjust these)
    start_x, start_y = 290, 290  # Example starting positions

    # Load and place each letter image
    for i in range(26):  # Assuming only uppercase letters A-Z
        char = chr(ord('A') + i)
        image_filename = f"char_{i}.png"  # Construct filename based on index

        try:
            # Load the letter image
            letter_image_path = os.path.join(letters_folder, image_filename)
            letter_image = Image.open(letter_image_path)
            letter_image = letter_image.resize((cell_width, cell_height))

            # Calculate position based on the custom layout
            if i < 4:  # First line (A, B, C, D)
                x = start_x + (i % 4) * (cell_width)
                y = start_y
            elif i < 12:  # Second line (E, F, G, H, I, J, K, L)
                x = start_x-290 + ((i - 4) % 8) * (cell_width + 3)
                y = start_y + (cell_height + 40)
            elif i < 20:  # Third line (M, N, O, P, Q, R, S, T)
                x = start_x-290 + ((i - 12) % 8) * (cell_width + 3)
                y = start_y + 2 * (cell_height + 40)
            else:  # Fourth line (U, V, W, X, Y, Z)
                x = start_x-290 + ((i - 20) % 6) * (cell_width + 3)
                y = start_y + 3 * (cell_height + 40)

            # Paste the letter image onto the template
            template.paste(letter_image, (x, y))
        except FileNotFoundError:
            print(f"No image for {char}")

    # Save the modified template
    template.save(output_path)

import tempfile
# def place_letters_on_template(template_path, letter_images, output_file_path):
#     template = Image.open(template_path)
#     cell_width, cell_height = 140, 140
#     start_x, start_y = 290, 290

#     for i, letter_image in enumerate(letter_images):
#         letter_image = letter_image.resize((cell_width, cell_height))
#         x = start_x + (i % 4) * (cell_width)  # Simplified positioning for demonstration
#         y = start_y + (i // 4) * (cell_height + 40)
#         template.paste(letter_image, (x, y))

#     template.save(output_file_path, format='PNG')
#     return output_file_path

# Example usage
# def download_font(file_path,user_id):
#     try:
#         download_dir = os.path.join(r'C:\Users\ADMIN\Desktop\Projects\Font-FusionBackend\FontFusion\Fusion1', f'user_{user_id}')# Specify your download directory
#         download_dir = os.path.abspath(download_dir)
#         if not os.path.exists(download_dir):
#           os.makedirs(download_dir)
#         chrome_options = webdriver.ChromeOptions()
#         # # chrome_options.add_experimental_option("prefs", prefs)
#         # chrome_options.add_argument("--headless")  # Run Chrome in headless mode
#         # chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
#         # chrome_options.add_argument("--no-sandbox")  # Bypass OS security model, required for running as root in Docker
#         # chrome_options.add_argument("--disable-dev-shm-usage")
#         prefs = {
#             "download.default_directory": download_dir,
#             "download.prompt_for_download": False,
#             "download.directory_upgrade": True,
#             "safebrowsing.enabled": True,
#             "download.default_filename": "Myfont-Regular.ttf"  # Specify the desired filename with the .ttf extension
#         }
#         chrome_options.add_experimental_option("prefs", prefs)
#         # chrome_options.add_argument("--headless")  # Run Chrome in headless mode
#         # chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
#         # chrome_options.add_argument("--no-sandbox")  # Bypass OS security model, required for running as root in Docker
#         # chrome_options.add_argument("--disable-dev-shm-usage")

#     except Exception as e:
#         print("An error occurred while setting up Chrome options:", e)
#         return None

#     try:
#         os.environ['PATH'] += r"D:\Downloads\chromedriver-win64\chromedriver-win64\chromedriver-win64"
#         driver = webdriver.Chrome(options=chrome_options)

#         driver.get('https://www.calligraphr.com/en/')

#         login_button = driver.find_element(By.ID, 'nav-login-button')
#         login_button.click()

#         email_input = driver.find_element(By.ID, 'id_username')
#         password_input = driver.find_element(By.ID, 'id_password')

#         email_input.send_keys('anandi.ket@somaiya.edu')
#         password_input.send_keys('C@lligraphr')

#         submit_button = driver.find_element(By.ID, 'login_button')
#         submit_button.click()

#         time.sleep(2)

#         my_fonts_link = driver.find_element(By.ID, 'top-module-link-fonts')
#         my_fonts_link.click()

#         upload_template_link = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fonts-tb-load-template")))
#         upload_template_link.click()

#         time.sleep(4)

#         file_input = driver.find_element(By.ID, 'template-upload-fileinput')

#         file_input.send_keys(file_path)
#         time.sleep(4)

#         upload_button = driver.find_element(By.ID, 'upload-template-submit-files-button')
#         upload_button.click()
#         print('Template uploaded')

#         WebDriverWait(driver, 10).until(
#             EC.visibility_of_element_located((By.CLASS_NAME, 'waiting-header'))
#         )
#         print("Loading indicator displayed")

#         WebDriverWait(driver, 30).until(
#             EC.invisibility_of_element_located((By.CLASS_NAME, 'waiting-header'))
#         )
#         print("Loading indicator hidden")

#         add_chars_button = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'upload-template-add-chars-button')))
#         add_chars_button.click()
#         print('Characters uploaded')
#         time.sleep(4)

#         build_font_link = driver.find_element(By.ID, 'fonts-tb-build-font')
#         build_font_link.click()

#         build_button = driver.find_element(By.ID, 'build-font-submit-button')
#         build_button.click()

#         WebDriverWait(driver, 10).until(
#             EC.visibility_of_element_located((By.CLASS_NAME, 'waiting-header'))
#         )
#         print("Loading indicator displayed")

#         WebDriverWait(driver, 30).until(
#             EC.invisibility_of_element_located((By.CLASS_NAME, 'waiting-header'))
#         )
#         print("Loading indicator hidden")

#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CLASS_NAME, 'result-font-link'))
#         )

#         download_link = driver.find_element(By.CLASS_NAME, 'result-font-link')
#         download_link.click()
#         print('Font downloaded')

#         driver.implicitly_wait(10)

#         print('Everything successfully executed')

#     except Exception as e:
#         print("An error occurred:", e)
#         return None

#     finally:
#         driver.quit()

#     # Check if there are files in the download directory
#     files = [os.path.join(download_dir, f) for f in os.listdir(download_dir)]
#     if not files:
#         print("No files found in the download directory.")
#         return None  # Handle the case where no files are found

#     # Find the most recently created file
#     latest_file = max(files, key=os.path.getctime)
#     print(latest_file)
#     return latest_file


def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Check for write permission
    if not os.access(directory, os.W_OK):
        raise PermissionError(f"Write permission is required for the directory: {directory}")

def download_font(file_path):
    try:
        # Use current working directory for downloads
        download_dir = os.getcwd()
        print(f"Download directory set to: {download_dir}")

        # Ensure the download directory exists and has write permissions
        ensure_directory_exists(download_dir)

        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        chrome_options.add_argument('--window-size=1920x1080')  # Ensure the headless browser has a window size

        # Initialize the Chrome driver
        driver = webdriver.Chrome(options=chrome_options)

        # Open the website
        driver.get('https://www.calligraphr.com/en/')

        # Log in to the website
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'nav-login-button'))
        ).click()
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'id_username'))
        ).send_keys('anandi.ket@somaiya.edu')
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'id_password'))
        ).send_keys('C@lligraphr')
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'login_button'))
        ).click()

        # Navigate to 'My Fonts'
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'top-module-link-fonts'))
        ).click()

        # Upload the template
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'fonts-tb-load-template'))
        ).click()
        
        time.sleep(4)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'template-upload-fileinput'))
        ).send_keys(file_path)
        
        time.sleep(4)
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'upload-template-submit-files-button'))
        ).click()
        
        print('Template uploaded')
        
        # Wait for the loading indicator to appear and then disappear
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'waiting-header'))
        )
        print("Loading indicator displayed")
        
        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, 'waiting-header'))
        )
        print("Loading indicator hidden")

        # Add characters
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'upload-template-add-chars-button'))
        ).click()
        
        print('Characters uploaded')
        
        time.sleep(4)
        
        # Build the font
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'fonts-tb-build-font'))
        ).click()
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'build-font-submit-button'))
        ).click()
        
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'waiting-header'))
        )
        print("Loading indicator displayed")
        
        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, 'waiting-header'))
        )
        print("Loading indicator hidden")

        # Download the font
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'result-font-link'))
        ).click()
        
        print('Font download initiated')
        
        time.sleep(10)  # Wait for the download to complete

        # Get the path where the font is downloaded
        downloaded_file_path = os.path.join(download_dir, "Myfont-Regular.ttf")
        
        if os.path.exists(downloaded_file_path):
            print('Font downloaded successfully at:', downloaded_file_path)
            return downloaded_file_path
        else:
            print("Font download failed")
            return None

    except Exception as e:
        print("An error occurred:", e)
        return None

    finally:
        driver.quit()

# Example usage:

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def decode_image(request):
    if request.method == 'POST':
        try:
            print("Received raw data:", request.body)
            data = json.loads(request.body)
            images = data['images']

            directory = 'GenTTF'
            if not os.path.exists(directory):
                os.makedirs(directory)

            for idx, base64_image in enumerate(images):
                image_data = base64.b64decode(base64_image)
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((64, 64))
                image.save(os.path.join(directory, f'char_{idx}.png'), 'PNG')

            # Corrected the use of raw strings for Windows paths
            place_images_on_template(
                template_path=r'C:\Users\ADMIN\Desktop\Projects\Font-FusionBackend\FontFusionBackend\FontFusion\WhatsApp Image 2024-06-18 at 12.56.32 PM.jpeg',
                images_folder=r'C:\Users\ADMIN\Desktop\Projects\Font-FusionBackend\FontFusionBackend\FontFusion\GenTTF',
                output_path=r'C:\Users\ADMIN\Desktop\Projects\Font-FusionBackend\FontFusionBackend\Fusion1\final_template.png',
                num_images=26,  # Assuming 26 images
                prefix="char_"  # Assuming files are named like 'containsdbdgg0.png', 'containsdbdgg1.png', etc.
            )

            return JsonResponse({'message': f'{len(images)} images processed and saved successfully'}, status=200)
        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({'error': str(e)}, status=400)
        except json.JSONDecodeError as json_err:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'This endpoint only supports POST requests'}, status=405)

def place_images_on_template(template_path, images_folder, output_path, num_images, prefix="char_"):
    from PIL import Image
    import os

    template = Image.open(template_path)
    cell_width, cell_height = 140, 140
    start_x, start_y = 290, 290

    for i in range(num_images):
        image_filename = f"{prefix}{i}.png"
        try:
            image_path = os.path.join(images_folder, image_filename)
            image = Image.open(image_path)
            image = image.resize((cell_width, cell_height))

            x, y = calculate_position(i, start_x, start_y, cell_width, cell_height)
            template.paste(image, (x, y))
        except FileNotFoundError:
            print(f"No image found for index {i}")

    template.save(output_path)
    

def calculate_position(index, start_x, start_y, cell_width, cell_height):
    if index < 4:
        x = start_x + (index % 4) * (cell_width)
        y = start_y
    elif index < 12:
        x = start_x - 290 + ((index - 4) % 8) * (cell_width + 3)
        y = start_y + (cell_height + 40)
    elif index < 20:
        x = start_x - 290 + ((index - 12) % 8) * (cell_width + 3)
        y = start_y + 2 * (cell_height + 40)
    else:
        x = start_x - 290 + ((index - 20) % 6) * (cell_width + 3)
        y = start_y + 3 * (cell_height + 40)
    return x, y

def handwritten(request):
    user_id = request.user.id
    template_path = r'C:\Users\ADMIN\Desktop\Projects\Font-FusionBackend\FontFusionBackend\Fusion1\final_template.png'
    print(f"Template path: {template_path}")

    generated_font_path = download_font(template_path)
    if generated_font_path:
        base, _ = os.path.splitext(generated_font_path)
        ttf_font_path = f"{base}.ttf"
        os.rename(generated_font_path, ttf_font_path)
        print(f"Renamed font file to: {ttf_font_path}")

        if os.path.exists(ttf_font_path):
            print(f"Font file found: {ttf_font_path}")
            return FileResponse(open(ttf_font_path, 'rb'), as_attachment=True, content_type='font/ttf')
        else:
            print("Font file not found after renaming.")
            return HttpResponseNotFound('The requested font file was not found after generation.')
    else:
        print("Failed to generate the font file.")
        return JsonResponse({'error': 'Failed to generate the font file'}, status=500)