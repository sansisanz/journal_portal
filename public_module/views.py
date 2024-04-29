from django.shortcuts import render

# Create your views here.
def p_index(request):
    return render(request, 'p_index.html')

def p_alljournals(request):
    return render(request, 'p_alljournals.html')

def p_ethics(request):
    return render(request, 'p_ethics.html')

def p_guidelines(request):
    return render(request, 'p_guidelines.html')

def p_j(request):
    return render(request, 'p_j.html')

def p_journals(request):
    return render(request, 'p_journals.html')

def p_authorreg(request):
    return render(request, 'p_authorreg.html')

def p_userreg(request):
    return render(request, 'p_userreg.html')

def p_userprofile(request):
    return render(request, 'p_userprofile.html')


