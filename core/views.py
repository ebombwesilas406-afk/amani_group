from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,'core/home.html')

def about(request):
    return render(request,'core/about.html')

def contact(request):
    return render(request,'core/contact.html')

def updates(request):
    return render(request,'core/updates.html')

def rules(request):
    return render(request,'core/rules.html')

def operations(request):
    return render(request,'core/operations.html')

def membership(request):
    return render(request,'core/membership.html')