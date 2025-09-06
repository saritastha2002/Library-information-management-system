from django.shortcuts import render

def home(request):
    return render(request, "home.html",context={"current_tab" : "home"})

def readers(request):
    return render(request, "readers.html",context={"current_tab" : "readers"})
