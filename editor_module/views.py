from django.shortcuts import render
# Create your views here.

def editor_article(request):
    return render(request, "article.html")

def editorialboard(request):
    return render(request, 'editorialboard.html')

def editor_forgotpassword(request):
    return render(request, 'forgot-password.html')

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
    return render(request, 'notifications.html')

def editor_assignedjournal(request):
    return render(request, 'assignedjournal.html')

def uploadArticle(request):
    return render(request, 'uploadarticle.html')

def journaldetails(request):
    return render(request, 'journaldetails.html')

def upddetails(request):
    return render(request, 'upddetails.html')

def edit(request):
    return render(request, 'edit.html')

def e_visits(request):
    return render(request, 'e_visits.html')

def e_downloads(request):
    return render(request, 'e_downloads.html')

def remove(request):
    return render(request, 'remove.html')

def editor_contact(request):
    return render(request, 'editor_contact.html')