from django.db import models

# Create your models here.
class Request(models.Model):
    email = models.CharField(max_length=255, blank=False, null=True)
    github = models.CharField(max_length=255, blank=False, null=True)
    message = models.TextField()
    agree = models.BooleanField()
