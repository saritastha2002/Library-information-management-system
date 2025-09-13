from django.db import models
from datetime import timedelta
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser


# Create your models here.
# Custom User Model with roles
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('librarian', 'Librarian'),
        ('member', 'Member'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    
    def is_librarian(self):
        return self.role == 'librarian' or self.is_admin()
    
    def is_member(self):
        return self.role == 'member'

class Reader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
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
    returned = models.BooleanField(default=False) 
    

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = (self.borrowed_on or now().date()) + timedelta(days=7)
        super().save(*args, **kwargs)
    @property
    def member_name(self):
        return self.member.reader_name


    @property
    def is_overdue(self):
        from datetime import date
        return date.today() > self.due_date
    
    def __str__(self):
        return f"{self.member.reader_name} - {self.book.title}"