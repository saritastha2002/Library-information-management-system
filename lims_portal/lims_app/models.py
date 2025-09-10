from django.db import models

# Create your models here.

class Reader(models.Model):
    reference_id = models.CharField(max_length=50, unique=True)   # unique
    reader_name = models.CharField(max_length=100)
    reader_contact = models.CharField(max_length=50, blank=True, null=True, unique=True)  # unique
    reader_address = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.reference_id} - {self.reader_name}"
