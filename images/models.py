from django.db import models
from store.validators import validate_file_size

# Create your models here.

class Image(models.Model):
    image = models.ImageField(
        upload_to="images",
        validators=[validate_file_size])