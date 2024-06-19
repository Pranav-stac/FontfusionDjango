import os
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

import base64
import io
from .models_pytorch import Encoder, Decoder, get_latent, get_demo, plotter, get_predictions
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

@csrf_exempt
def image_process_view(request):
    if request.method == 'POST':
        text_inputs = [request.POST.get('image1'), request.POST.get('image2')]

        # Find image paths corresponding to the text inputs
        image_paths = [find_image_path(name + '.png') for name in text_inputs]

        # Check if all images are found
        if None in image_paths:
            return JsonResponse({'error': 'Could not find image(s) for the given text input(s)'}, status=400)

        # Load and process images
        images = [handle_uploaded_image(open(image_path, 'rb')) for image_path in image_paths]

        with torch.no_grad():
            latent = sum([get_latent(torch.tensor(im).float()) for im in images]) / len(images)
            pred = get_demo(latent)
            output_images = [Image.fromarray((img.numpy().squeeze() * 255).astype(np.uint8)) for img in pred]

            # Convert output images to base64 to embed in HTML
            encoded_imgs = []
            for img in output_images:
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                encoded_imgs.append(img_str)

            return render(request, 'image_output.html', {'images': encoded_imgs})
    else:
        return render(request, 'upload.html')

@csrf_exempt
def image_process_api(request):
    if request.method == 'POST':
        text_inputs = [request.POST.get('image1'), request.POST.get('image2')]
        
        # Validate if both text inputs are provided
        if None in text_inputs:
            return JsonResponse({'error': 'Both text1 and text2 inputs are required'}, status=400)
        
        # Find image paths corresponding to the text inputs
        image_paths = [find_image_path(name + '.png') for name in text_inputs]

        # Check if all images are found
        if None in image_paths:
            return JsonResponse({'error': 'Could not find image(s) for the given text input(s)'}, status=400)

        # Load and process images
        images = [handle_uploaded_image(open(image_path, 'rb')) for image_path in image_paths]

        with torch.no_grad():
            latent = sum([get_latent(torch.tensor(im).float()) for im in images]) / len(images)
            pred = get_demo(latent)
            output_images = [Image.fromarray(255 - (img.numpy().squeeze() * 255).astype(np.uint8)) for img in pred]  # Invert colors

            # Save output images to the 'PngNew' folder
            output_folder = os.path.join(settings.BASE_DIR, 'PngNew')
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            for idx, img in enumerate(output_images):
                image_path = os.path.join(output_folder, f'char_{idx}.png')
                img.save(image_path, format="PNG")

            # Now place these images onto a template
            template_path = "WhatsApp Image 2024-06-18 at 12.56.32 PM.jpeg"  # Adjust this path as needed
            output_template_path = os.path.join(settings.BASE_DIR, 'output_template.png')
            place_letters_on_template(template_path, output_folder, output_template_path)

            # Optionally convert to base64 to send in JSON
            encoded_imgs = []
            for idx, img in enumerate(output_images):
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                encoded_imgs.append(img_str)

            return JsonResponse({'output_images': encoded_imgs})
    else:
        return JsonResponse({'error': 'This endpoint only supports POST requests'}, status=405)
@csrf_exempt    
def send_font_file(request):
    # Call download_font to generate the font file
    template_path = "C:\\Users\\ADMIN\\Desktop\\Projects\\Font-FusionBackend\\FontFusion\\output_template.png"  # Adjust this path as needed
    generated_font_path = download_font(template_path)

    if generated_font_path:
        # Ensure the file has a .ttf extension
        base, _ = os.path.splitext(generated_font_path)
        ttf_font_path = f"{base}.ttf"
        os.rename(generated_font_path, ttf_font_path)

        # Check if the file exists after attempting to rename it
        if os.path.exists(ttf_font_path):
            return FileResponse(open(ttf_font_path, 'rb'), as_attachment=True, content_type='font/ttf')
        else:
            return HttpResponseNotFound('The requested font file was not found after generation.')
    else:
        return JsonResponse({'error': 'Failed to generate the font file'}, status=500)
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

# Example usage
def download_font(file_path):
    try:
        download_dir = r'C:\Users\ADMIN\Desktop\Projects\Font-FusionBackend\FontFusion\Fusion1'  # Specify your download directory
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "download.default_filename": "Myfont-Regular.ttf"  # Specify the desired filename with the .ttf extension
        }
        chrome_options.add_experimental_option("prefs", prefs)
    except Exception as e:
        print("An error occurred while setting up Chrome options:", e)
        return None

    try:
        os.environ['PATH'] += r"D:\Downloads\chromedriver-win64\chromedriver-win64\chromedriver-win64"
        driver = webdriver.Chrome(options=chrome_options)

        driver.get('https://www.calligraphr.com/en/')

        login_button = driver.find_element(By.ID, 'nav-login-button')
        login_button.click()

        email_input = driver.find_element(By.ID, 'id_username')
        password_input = driver.find_element(By.ID, 'id_password')

        email_input.send_keys('anandi.ket@somaiya.edu')
        password_input.send_keys('C@lligraphr')

        submit_button = driver.find_element(By.ID, 'login_button')
        submit_button.click()

        time.sleep(2)

        my_fonts_link = driver.find_element(By.ID, 'top-module-link-fonts')
        my_fonts_link.click()

        upload_template_link = driver.find_element(By.ID, 'fonts-tb-load-template')
        upload_template_link.click()

        time.sleep(4)

        file_input = driver.find_element(By.ID, 'template-upload-fileinput')

        file_input.send_keys(file_path)
        time.sleep(4)

        upload_button = driver.find_element(By.ID, 'upload-template-submit-files-button')
        upload_button.click()
        print('Template uploaded')

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'waiting-header'))
        )
        print("Loading indicator displayed")

        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, 'waiting-header'))
        )
        print("Loading indicator hidden")

        add_chars_button = driver.find_element(By.ID, 'upload-template-add-chars-button')
        add_chars_button.click()
        print('Characters uploaded')
        time.sleep(4)

        build_font_link = driver.find_element(By.ID, 'fonts-tb-build-font')
        build_font_link.click()

        build_button = driver.find_element(By.ID, 'build-font-submit-button')
        build_button.click()

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'waiting-header'))
        )
        print("Loading indicator displayed")

        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, 'waiting-header'))
        )
        print("Loading indicator hidden")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'result-font-link'))
        )

        download_link = driver.find_element(By.CLASS_NAME, 'result-font-link')
        download_link.click()
        print('Font downloaded')

        driver.implicitly_wait(10)

        print('Everything successfully executed')

    except Exception as e:
        print("An error occurred:", e)
        return None

    finally:
        driver.quit()

    # Return the path to the downloaded font file
    latest_file = max([os.path.join(download_dir, f) for f in os.listdir(download_dir)], key=os.path.getctime)
    print(latest_file)
    return latest_file

