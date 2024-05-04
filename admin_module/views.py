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

def visits(request):
    return render(request, 'visits.html')  

def downloads(request):
    return render(request, 'downloads.html')  

def userlist(request):
    return render(request, 'userlist.html')

def admin_profile(request):
    return render(request, 'admin_profile.html')

def admin_resetpassword(request):
    return render(request, 'admin_resetpassword.html')

def set_password(request):
    return render(request, 'set_password.html')

def admin_navbar(request):
    return render(request, 'admin_navbar.html')

def create_journal(request):
    return render(request, 'create_journal.html') 

def view_journals(request):
    return render(request, 'view_journals.html')

def visit_counts(request):
    return render(request, 'visit_counts.html')
    
def user_access(request):
    return render(request, 'user_access.html')    