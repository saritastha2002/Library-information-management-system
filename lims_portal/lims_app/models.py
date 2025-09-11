from django.db import models
from datetime import timedelta
from django.utils.timezone import now


# Create your models here.

class Reader(models.Model):
    reference_id = models.CharField(max_length=50, unique=True)   # unique
    reader_name = models.CharField(max_length=100)
    reader_contact = models.CharField(max_length=50, blank=True, null=True, unique=True)  # unique
    reader_address = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.reference_id} - {self.reader_name}"
    
    
class Book(models.Model):
    title = models.CharField(max_length=200,unique=True)
    author = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    available_quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title
    
    

class Borrowing(models.Model):
    member = models.ForeignKey(
        'Reader', 
        on_delete=models.CASCADE,
        limit_choices_to={'active': True}  # only active members
    )
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    borrowed_on = models.DateField(auto_now_add=True)
    due_date = models.DateField()

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = (self.borrowed_on or now().date()) + timedelta(days=7)
        super().save(*args, **kwargs)
    @property
    def member_name(self):
        return self.member.reader_name


    def __str__(self):
        return f"{self.member.reader_name} - {self.book.title}"