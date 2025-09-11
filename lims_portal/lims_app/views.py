from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import *
from .form import *
from django.db import IntegrityError
from django.db.models import Q , Sum
from django.contrib import messages
from datetime import date,timedelta
from django.core.paginator import Paginator
from django.db import transaction


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

    # Pagination: 5 readers per page
    paginator = Paginator(readers, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "readers.html", {
        "current_tab": "readers",
        "readers": page_obj,   # page_obj पास गरियो
        "query": query,
        "message": message
    })



def save_reader(request):
    readers = Reader.objects.all()  # get all readers for rendering

    if request.method == "POST":
        ref_id = request.POST.get('reader_ref_id', '').strip()
        name = request.POST.get('reader_name', '').strip()
        contact = request.POST.get('reader_contact', '').strip()
        address = request.POST.get('address', '').strip()

        # Check required fields
        if not ref_id or not name:
            return render(request, "readers.html", {
                "current_tab": "readers",
                "readers": readers,
                "duplicate_error": "Please fill in all required fields!",
                "show_add_modal": True   # <-- keep modal open
            })

        # Check duplicates
        duplicate_exists = Reader.objects.filter(
            Q(reference_id=ref_id) | Q(reader_contact=contact)
        ).exists()

        if duplicate_exists:
            return render(request, "readers.html", {
                "current_tab": "readers",
                "readers": readers,
                "duplicate_error": "Reference ID or Contact already exists!",
                "show_add_modal": True   # <-- keep modal open
            })

        # Save new reader
        try:
            Reader.objects.create(
                reference_id=ref_id,
                reader_name=name,
                reader_contact=contact,
                reader_address=address,
                active=True
            )
            messages.success(request, "Reader added successfully!")
            return redirect("readers_tab")

        except IntegrityError:
            return render(request, "readers.html", {
                "current_tab": "readers",
                "readers": readers,
                "duplicate_error": "A reader with this Reference ID already exists!",
                "show_add_modal": True
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
    books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(genre__icontains=query)
        )

    paginator = Paginator(books, 5)  # pagination
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Count for display
    total_books = Book.objects.count()   # unique book titles
    total_quantity = Book.objects.aggregate(Sum('available_quantity'))['available_quantity__sum'] or 0

    return render(request, 'books.html', {
        'page_obj': page_obj,
        'query': query,
        'total_books': total_books,
        'total_quantity': total_quantity,
    })

    

def add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        genre = request.POST.get('genre', '').strip()

        if not title or not author or not genre:
            messages.error(request, "All fields are required.")
            return redirect('book_list')

        try:
            Book.objects.create(title=title, author=author, genre=genre)
            messages.success(request, "Book added successfully!")
        except IntegrityError:
            messages.error(request, "Book already listed!")   # 👈 duplicate title case

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

# my bag

def records_tab(request):
    form = BorrowingFilterForm(request.GET or None)
    records = Borrowing.objects.select_related('member', 'book').all()

    if form.is_valid():
        member_name = form.cleaned_data.get('member_name')
        due_date = form.cleaned_data.get('due_date')

        if member_name:
            records = records.filter(
                Q(member__reader_name__icontains=member_name) |
                Q(member__reference_id__icontains=member_name)
            )
        if due_date:
            records = records.filter(due_date=due_date)

    paginator = Paginator(records, 5)  # 5 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'records.html', {
        'current_tab': 'records',
        'form': form,
        'page_obj': page_obj
    })


def add_borrowing(request):
    today = date.today()
    due_date = today + timedelta(days=7)

    if request.method == 'POST':
        form = BorrowingForm(request.POST)
        if form.is_valid():
            book = form.cleaned_data['book']

            if book.available_quantity <= 0:
                messages.error(request, f"'{book.title}' is out of stock! Cannot borrow.")
                return redirect('records_tab')

            # Use transaction to ensure both actions happen together
            with transaction.atomic():
                # Decrease available quantity
                book.available_quantity -= 1
                book.save()

                # Save borrowing record
                borrowing = form.save(commit=False)
                borrowing.borrowed_on = today
                borrowing.due_date = due_date
                borrowing.save()

            messages.success(request, "Borrowing record added successfully!")
            return redirect('records_tab')  # redirect after POST
    else:
        form = BorrowingForm()

    return render(request, 'add_borrowing.html', {
        'form': form,
        'current_tab': 'records',
        'today': today,
        'due_date': due_date
    })
    
    # Return
  
def return_book(request, borrowing_id):
    borrowing = Borrowing.objects.get(id=borrowing_id)
    book = borrowing.book
    book.available_quantity += 1
    book.save()
    borrowing.delete()
    messages.success(request, f"Book '{book.title}' returned successfully!")
    return redirect('records_tab')

def returns_tab(request):
    records = Borrowing.objects.all().order_by('-borrowed_on')
    paginator = Paginator(records, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'return_borrowing.html', {
        'page_obj': page_obj,
        'current_tab': 'returns'
    })