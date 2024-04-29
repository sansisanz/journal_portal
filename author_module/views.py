from django.shortcuts import render

# Create your views here.
def author_index(request):
    return render(request, 'author-index.html')

def author_profile(request):
    return render(request, 'author_profile.html')

def author_forgotpassword(request):
    return render(request, 'author-forgotpassword.html')

def author_resetpassword(request):
    return render(request, 'author_resetpassword.html')

def author_submitarticle(request):
    return render(request, 'submit-article.html')

