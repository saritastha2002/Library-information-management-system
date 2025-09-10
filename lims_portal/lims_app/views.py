from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import *
from .form import ReaderForm,Reader,Book
from django.db import IntegrityError
from django.db.models import Q 
from django.contrib import messages

def home(request):
    return render(request, "home.html",context={"current_tab" : "home"})

# Readers
def readers(request):
    return render(request, "readers.html",context={"current_tab" : "readers"})

def readers_tab(request):
    query = ''
    message = ''
    if request.method == "POST":
        query = request.POST.get('query', '').strip()
        if query:
            readers = Reader.objects.filter(reader_name__icontains=query)
            if not readers.exists():
                message = f"No readers matched '{query}'."
        else:
            readers = Reader.objects.all()
    else:
        readers = Reader.objects.all()

    return render(request, "readers.html", {
        "current_tab": "readers",
        "readers": readers,
        "query": query,
        "message": message
    })



def save_reader(request):
    if request.method == "POST":
        ref_id = request.POST.get('reader_ref_id', '').strip()
        name = request.POST.get('reader_name', '').strip()
        contact = request.POST.get('reader_contact', '').strip()
        address = request.POST.get('address', '').strip()

        # Check required fields
        if not ref_id or not name:
            readers = Reader.objects.all()
            return render(request, "readers.html", {
                "current_tab": "readers",
                "readers": readers,
                "duplicate_error": "Please fill in all required fields!"
            })

        # Check duplicates
        duplicate_exists = Reader.objects.filter(
            Q(reference_id=ref_id) | Q(reader_contact=contact)
        ).exists()

        if duplicate_exists:
            readers = Reader.objects.all()
            return render(request, "readers.html", {
                "current_tab": "readers",
                "readers": readers,
                "duplicate_error": "Reference ID or Contact already exists!"
            })

        # Save
        try:
            Reader.objects.create(
                reference_id=ref_id,
                reader_name=name,
                reader_contact=contact,
                reader_address=address,
                active=True
            )
        except IntegrityError:
            readers = Reader.objects.all()
            return render(request, "readers.html", {
                "current_tab": "readers",
                "readers": readers,
                "duplicate_error": "A reader with this Reference ID already exists!"
            })

    return redirect("readers_tab")


def update_reader(request, id):
    reader_obj = get_object_or_404(Reader, id=id)   # Capital 'R'

    if request.method == 'POST':
        form = ReaderForm(request.POST, instance=reader_obj)
        if form.is_valid():
            form.save()
            return redirect('readers_tab')
    else:
        form = ReaderForm(instance=reader_obj)

    return render(request, 'update_reader.html', {'form': form})

def delete_reader(request, id):
    reader_obj = Reader.objects.get(id=id)   # single object
    if request.method == 'POST':
        reader_obj.delete()
        return redirect('readers_tab')   # or 'readers_tab', depending on your urls.py
    return render(request, 'delete_reader.html', {'reader': reader_obj})


# Book
def book_list(request):
    query = request.GET.get('search', '')
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(genre__icontains=query)
        )
    else:
        books = Book.objects.all()
    
    return render(request, 'books.html', {'books': books, 'query': query})

def add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        genre = request.POST.get('genre')
        if title and author and genre:
            Book.objects.create(title=title, author=author, genre=genre)
            messages.success(request, "Book added successfully!")
        else:
            messages.error(request, "All fields are required.")
    return redirect('book_list')

def update_book(request, book_id):
    book = Book.objects.get(id=book_id)
    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.genre = request.POST.get('genre')
        book.available_quantity = request.POST.get('available_quantity', book.available_quantity)
        book.save()
        messages.success(request, "Book updated successfully!")
        return redirect('book_list')
    return render(request, 'update_book.html', {'book': book})


def delete_book(request, book_id):
    book = Book.objects.get(id=book_id)
    book.delete()
    messages.success(request, "Book deleted successfully!")
    return redirect('book_list')

# Increase quantity (e.g., when adding a new copy)
def increase_quantity(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.available_quantity += 1
    book.save()
    messages.success(request, f"Quantity increased for '{book.title}'")
    return redirect('book_list')

# Decrease quantity (e.g., when book is purchased)
def decrease_quantity(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if book.available_quantity > 0:
        book.available_quantity -= 1
        book.save()
        messages.success(request, f"Quantity decreased for '{book.title}'")
    else:
        messages.warning(request, f"'{book.title}' is out of stock!")
    return redirect('book_list')