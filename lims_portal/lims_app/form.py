from django import forms
from .models import Reader,Book,Borrowing
from datetime import date
from django.core.exceptions import ValidationError
class ReaderForm(forms.ModelForm):
    class Meta:
        model = Reader
        fields = ["reader_name", "reader_contact", "reference_id", "reader_address"]
        
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'available_quantity']
        

class BorrowingForm(forms.ModelForm):
    class Meta:
        model = Borrowing
        fields = ['member_name', 'book']

    def clean(self):
        cleaned_data = super().clean()
        member = cleaned_data.get('member_name')
        today = date.today()

        # Check if member already borrowed today
        if member and Borrowing.objects.filter(member_name=member, borrowed_on=today).exists():
            raise ValidationError(f"{member} has already borrowed a book today!")

        return cleaned_data


#for filtering
class BorrowingFilterForm(forms.Form):
    member_name = forms.CharField(required=False, label="Member Name")
    due_date = forms.DateField(
        required=False,
        label="Due Date",
        widget=forms.DateInput(attrs={'type': 'date'})
    )