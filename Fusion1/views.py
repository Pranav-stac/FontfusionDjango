import os
from django.conf import settings
from django.http import JsonResponse
from PIL import Image
import numpy as np
import torch
import base64
import io
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
            output_images = [Image.fromarray((img.numpy().squeeze() * 255).astype(np.uint8)) for img in pred]

            # Convert output images to base64 to send in JSON
            encoded_imgs = []
            for img in output_images:
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                encoded_imgs.append(img_str)

            return JsonResponse({'output_images': encoded_imgs})
    else:
        return JsonResponse({'error': 'This endpoint only supports POST requests'}, status=405)
