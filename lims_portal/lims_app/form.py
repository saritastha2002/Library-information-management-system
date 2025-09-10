from django import forms
from .models import Reader

class ReaderForm(forms.ModelForm):
    class Meta:
        model = Reader
        fields = ["reader_name", "reader_contact", "reference_id", "reader_address"]