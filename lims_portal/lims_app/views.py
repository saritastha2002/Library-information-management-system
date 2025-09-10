from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import *
from .form import ReaderForm,Reader
from django.db import IntegrityError
from django.db.models import Q 

def home(request):
    return render(request, "home.html",context={"current_tab" : "home"})

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
