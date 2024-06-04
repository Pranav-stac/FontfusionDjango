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
import matplotlib.pyplot as plt


# Create your views here.
def index(request):
       context = {}  # You can pass data to the template with context
       return render(request, 'index.html', context)
class FontModelViewSet(viewsets.ModelViewSet):
    queryset = FontModel.objects.all()
    serializer_class = FontModelSerializer
def handle_uploaded_image(image_file):
    """Process an uploaded image file."""
    img = Image.open(image_file)
    img = img.convert('L')  # Convert to grayscale
    img = img.resize((64, 64))  # Resize image
    img = np.array(img).reshape(1, 1, 64, 64) / 255.0  # Normalize and reshape
    return img

def image_process_view(request):
    if request.method == 'POST':
        image_files = request.FILES.getlist('images')  # Get images from form data
        images = [handle_uploaded_image(img_file) for img_file in image_files]
        
        # Assuming the functions get_latent, get_demo, plotter, and get_predictions are defined
        with torch.no_grad():
            latent = sum([get_latent(torch.tensor(im).float()) for im in images]) / len(images)
            pred = get_demo(latent)
            # Convert tensor to PIL Image for display
            output_images = [Image.fromarray((img.numpy().squeeze() * 255).astype(np.uint8)) for img in pred]
            
            # Convert images to base64 to embed in HTML
            encoded_imgs = []
            for img in output_images:
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                encoded_imgs.append(img_str)
            
            return render(request, 'image_output.html', {'images': encoded_imgs})
    else:
        return render(request, 'upload.html')
 # Disable CSRF token for simplicity, consider using proper authentication for production
def image_process_api(request):
    if request.method == 'POST':
        # Access uploaded images directly from request.FILES
        image1 = Image.open(request.FILES['image1'])
        image2 = Image.open(request.FILES['image2'])

        # Process images
        images = [handle_uploaded_image(image1), handle_uploaded_image(image2)]

        with torch.no_grad():
            latent = sum([get_latent(torch.tensor(im).float()) for im in images]) / len(images)
            pred = get_demo(latent)
            output_image = Image.fromarray((pred.numpy().squeeze() * 255).astype(np.uint8))

            # Convert output image to base64 to send in JSON
            buffered = io.BytesIO()
            output_image.save(buffered, format="PNG")
            encoded_img = base64.b64encode(buffered.getvalue()).decode()

            return JsonResponse({'output_image': encoded_img})
    else:
        return JsonResponse({'error': 'This endpoint only supports POST requests'}, status=405)