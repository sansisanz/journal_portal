from django.shortcuts import render

# Create your views here.

def login(request):
    return render(request, 'login.html')

def index(request):
    return render(request, 'index.html')

def editor(request):
    return render(request, 'editor.html')

def journal(request):
    return render(request, 'journal.html')   

def forgotpassword(request):
    return render(request, 'forgotpassword.html')     

def vd(request):
    return render(request, 'vd.html')     

def visits(request):
    return render(request, 'visits.html')  

def downloads(request):
    return render(request, 'downloads.html')  

def userlist(request):
    return render(request, 'userlist.html')