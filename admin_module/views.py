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

def visit_c(request):
    return render(request, 'visit_c.html')  

def download_c(request):
    return render(request, 'download_c.html')  

def userlist(request):
    return render(request, 'userlist.html')

def adminprofile(request):
    return render(request, 'adminprofile.html')

def adminresetpassword(request):
    return render(request, 'adminresetpassword.html')

def admin_sidebar(request):
    return render(request, 'admin_sidebar.html')

def create_j(request):
    return render(request, 'create_j.html')

def set_password(request):
    return render(request, 'set_password.html')

def view_j(request):
    return render(request, 'view_j.html')
 
def edit_j(request):
    return render(request, 'edit_j.html')