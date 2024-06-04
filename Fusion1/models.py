from django.db import models

class FontModel(models.Model):
    # Your fields here
    name = models.CharField(max_length=100)
    # Add other fields as necessary
    