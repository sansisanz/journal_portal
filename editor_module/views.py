from django.shortcuts import render
# Create your views here.

def editor_article(request):
    return render(request, "article.html")

def editorialboard(request):
    return render(request, 'editorialboard.html')

def editor_ethics(request):
    return render(request, 'Ethics.html')

def editor_forgotpassword(request):
    return render(request, 'forgot-password.html')

def editor_guidelines(request):
    return render(request, 'Guidelines.html')

def editor_index(request):
    return render(request, 'editorindex.html')

def editor_journal(request):
    return render(request, 'editorjournal.html')

def editor_login(request):
    return render(request, 'login.html')

def editor_profile(request):
    return render(request, 'profile.html')

def editor_register(request):
    return render(request, 'register.html')

def editor_resetpassword(request):
    return render(request, 'resetpassword.html')

def editor_updates(request):
    return render(request, 'updates.html')

def editor_aims(request):
    return render(request, 'aims.html')