from django.shortcuts import render,redirect
from django.db.models import Q
import hashlib
import random
from django.core.mail import send_mail
from django.contrib import messages
from admin_module.models import author_table, ea_table,volume_table,journal_table,dept_table,eb_table,notification_table

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
    j_data = journal_table.objects.all()

    return render(request, 'p_journals.html',{'jdata':j_data})

def p_authorreg(request):
    return render(request, 'p_authorreg.html')

def p_userreg(request):
    return render(request, 'p_userreg.html')

def p_userprofile(request):
    return render(request, 'p_userprofile.html')

def public_navbar(request):
    return render(request, 'public_navbar.html')

def p_home(request,id):
    j_data = journal_table.objects.get(journal_id=id)
    v_data = volume_table.objects.filter(journal_id=id).order_by('-volume_id').first()
    p_data = eb_table.objects.filter(journal_id=id)
    n_data = notification_table.objects.filter(journal_id=id)
    return render(request, 'p_home.html',{'jdata':j_data,'vdata':v_data,'pdata':p_data,'ndata':n_data})

def read(request):
    return render(request, 'read.html') 

def verify_author(request):
    return render(request, 'verify_author.html')

def read_article(request):
    return render(request, 'read_article.html')


#author registration
def author_registration(request):
    if request.method == 'POST':
        #To retriev data from POST request
        authortype = request.POST.get('author_type')
        authorname = request.POST.get('author_name')
        authoremail = request.POST.get('author_email')
        authormobile = request.POST.get('author_mobile')
        authordob = request.POST.get('author_dob')
        authoraddress = request.POST.get('author_address')
        authorinstitute = request.POST.get('author_institute')
        authorpassword = request.POST.get('author_password')
        authorconfirmpassword = request.POST.get('author_confirm_password')
        request.session["email"]=authoremail

        flag=0
        lenpassword = ''
        confirmpassword = ''
        mobilelen = ''
        emailcheck = ''

        #form validation
        # Check if password is less than 8
        if len(authorpassword) < 8:
           flag=1
           lenpassword = 'Password should be atleast 8 characters long'
        
        # Check if password confirmed is true
        if authorpassword != authorconfirmpassword:
            flag=1
            confirmpassword = 'Passwords do not match'
        
        # Check if mobile number is less than 10
        if len(authormobile) < 10:
            flag = 1
            mobilelen = 'Mobile number should be atleast 10 digits long.'
        
       # Check if email already exists
        if author_table.objects.filter(author_email=authoremail).exists():
            flag = 1
            emailcheck = 'Email alreaady exists'

        if flag == 1:
            return render(request, 'p_authorreg.html', {'lenpassword': lenpassword, 'confirmpassword': confirmpassword, 'mobilelen': mobilelen, 'emailcheck': emailcheck})
        
        else:
        # Hash the password
            hashed_password = hashlib.sha1(authorpassword.encode('utf-8')).hexdigest()

            token = ''.join(str(random.randint(0,9)) for _ in range(4))
            

            #author object and save to database
            author = author_table.objects.create(
                author_type=authortype,
                author_name=authorname,
                author_email=authoremail,
                author_mobile=authormobile,
                author_dob=authordob,
                author_address=authoraddress,
                author_institute=authorinstitute,
                author_password=hashed_password,
                verify=False,
                token = token,
            )             
                                 
            request.session["token"] = token
            msg = "your OTP for email verification is :" +str(token) 
            send_mail("email verification for author registration",msg,"subindax@gmail.com",[request.session["email"]],fail_silently = False) 
            return render(request,"verify_author.html")


def email_verification(request):
    if request.method == "POST":
        try:
            udata = author_table.objects.get(author_email=request.session["email"])
        except author_table.DoesNotExist:
            return render(request, "verify_author.html", {"fail": "Email Verification Failed"})    

        token = udata.token
        otp = request.POST.get("otp")
        if otp == token:
            udata.verify=True
            udata.save()
            messages.success(request, 'Email Successfully Verified.')
            return redirect('/p_index/#cta')
        else:
            return render(request, "verify_author.html", {"fail": "Email Verification Failed"})
        

    

def author_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = hashlib.sha1(request.POST.get("password").encode('utf-8')).hexdigest()

        try:
            user = author_table.objects.get(author_email=email, author_password=password)
            request.session['author_email'] = user.author_email
            request.session['author_name'] = user.author_name
            return redirect("/author_index/")  # Redirect to the author's home page
        except author_table.DoesNotExist:
            return render(request, "p_index.html", {"login_error": "Invalid Email or Password"})

    return render(request, "p_index.html#cta")

def author_logout(request):
    try:
        del request.session['author_email']
        del request.session['author_name']
    except KeyError:
        pass
    return redirect("/p_index/#cta")

        
def p_volume(request):
    return render(request, 'p_volume.html')
    
    
    