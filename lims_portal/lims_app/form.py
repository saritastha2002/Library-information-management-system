from django import forms
from .models import Reader,Book

class ReaderForm(forms.ModelForm):
    class Meta:
        model = Reader
        fields = ["reader_name", "reader_contact", "reference_id", "reader_address"]
        
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'available_quantity']