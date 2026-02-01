from django.db import models
from django.contrib.auth.models import AbstractUser


# Usuario de la aplicación

class Usuario(AbstractUser):
    
    def __str__(self):
        return self.email