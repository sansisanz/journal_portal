import os
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.db.models import Q
import hashlib
import random
from django.db.models import F
from django.core.mail import send_mail
from django.contrib import messages
from admin_module.models import  ArticleDownload, ArticleVisit, JournalPageVisit, article_table, author_table, ea_table, issue_table,volume_table,journal_table,dept_table,eb_table,notification_table,gl_table

# Create your views here.

#--------------------   p_index    ---------------------------------------------------------------------------------------------------------------------
def p_index(request):
    latest_issues = (
        issue_table.objects.filter(status='open')
        .order_by('-created_at')[:3]
    )
    
    # Preparing data to be passed to the template
    issues_data = []
    for issue in latest_issues:
        volume = volume_table.objects.get(volume_id=issue.volume_id.volume_id)
        journal = journal_table.objects.get(journal_id=volume.journal_id.journal_id)
        issues_data.append({
            'journal_name': journal.journal_name,
            'volume': volume.volume,
            'issue_no': issue.issue_no,
            'published_date': issue.created_at,
            'cover_image': issue.cover_image.url,
            'journal_id': journal.journal_id,
        })
    
    context = {'issues_data': issues_data}
    return render(request, 'p_index.html', context)


def p_journals(request):
    j_data = journal_table.objects.all()

    return render(request, 'p_journals.html',{'jdata':j_data})

#---------------------------------------------------------------------------------------------------------------------------------------------------

def p_ethics(request,id):
    e_data = journal_table.objects.get(journal_id=id)
    return render(request, 'p_ethics.html',{'edata':e_data,})

def p_guidelines(request,id):
    g_data = gl_table.objects.filter(journal_id=id)
    return render(request, 'p_guidelines.html',{'gdata':g_data,})

#---------------------------------------------------------------------------------------------------------------------------------------------------

def p_alljournals(request, journal_id):
    # Retrieve the selected journal
    selected_journal = journal_table.objects.get(journal_id=journal_id)

    # Retrieve all volumes for the selected journal that are active
    volumes = volume_table.objects.filter(journal_id=journal_id, status__in=['open', 'closed'])

    # Create a list to store volume and issue information
    volume_issues_list = []

    for volume in volumes:
        # Retrieve issues for each volume that are either 'open' or 'closed'
        issues = issue_table.objects.filter(volume_id=volume.volume_id, status__in=['open', 'closed']).order_by('-created_at')

        # Count the number of issues for the volume
        issue_count = issues.count()

        for index, issue in enumerate(issues):
            cover_image_url = issue.cover_image.url if issue.cover_image else 'admin_module/static/img/book_cover.jpeg'
            volume_issues_list.append({
                'volume': volume.volume,
                'issue_no': issue.issue_no if issue_count > 1 else None,  # Only include issue number if there are multiple issues
                'cover_image': cover_image_url,
                'created_at': issue.created_at,
                'issue_id': issue.issue_id  # Add issue_id to the dictionary
            })

    # Sort the volume_issues_list by created_at in descending order
    volume_issues_list = sorted(volume_issues_list, key=lambda x: x['created_at'], reverse=True)

    return render(request, 'p_alljournals.html', {'selected_journal': selected_journal, 'volume_issues_list': volume_issues_list})


#---------------------------------------------------------------------------------------------------------------------------------------------------

def p_home(request, id):
    # Fetch the journal data
    j_data = get_object_or_404(journal_table, journal_id=id)
    
    # Fetch the latest issue for the journal
    latest_issue = issue_table.objects.filter(volume_id__journal_id=id).order_by('-issue_id').first()
    
    # Fetch editorial board and notifications data
    p_data = eb_table.objects.filter(journal_id=id)
    n_data = notification_table.objects.filter(journal_id=id)
    
    # Get the client's IP address
    ip_address = get_client_ip(request)
    
    # Check if there's already a visit record for this IP address
    visit_record, created = JournalPageVisit.objects.get_or_create(
        journal_id=j_data,
        ip_address=ip_address
    )
    
    if created:
        # Increment the visit count for the journal if it's a new visit
        j_data.visit_count = F('visit_count') + 1
        j_data.save()
        # Refresh the journal data to get the updated visit count
        j_data.refresh_from_db()
    
    return render(request, 'p_home.html', {
        'jdata': j_data,
        'latest_issue': latest_issue,
        'pdata': p_data,
        'ndata': n_data,
        'visit_count': j_data.visit_count  # Pass the visit count to the template
    })

#---------------------------------------------------------------------------------------------------------------------------------------------------

def p_authorreg(request):
    return render(request, 'p_authorreg.html')

def p_userreg(request):
    return render(request, 'p_userreg.html')

def p_userprofile(request):
    return render(request, 'p_userprofile.html')

def public_navbar(request):
    return render(request, 'public_navbar.html')

def get_client_ip(request):
    """Utility function to get the client's IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



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

#----------------------------------------------------------------------------------------------------------------------------------#
def issue_detail(request, issue_id):
    selected_issue = get_object_or_404(issue_table, issue_id=issue_id)
    articles = article_table.objects.filter(issue_id=issue_id, status='approved')
    
    articles_list = []
    for article in articles:
        authors = [article.author1, article.author2, article.author3]
        authors = [author.strip() for author in authors if author.strip()]
        authors_str = ', '.join(authors[:-1]) + ' and ' + authors[-1] if len(authors) > 1 else authors[0]
        articles_list.append({
            'id': article.article_id,
            'title': article.article_title,
            'authors': authors_str
        })
    
    return render(request, 'issue_detail.html', {'selected_issue': selected_issue, 'articles_list': articles_list})

def flipbook(request, article_id):
    article = get_object_or_404(article_table, pk=article_id)
    # Increment the visit count for the article directly in the article_table
    article_table.objects.filter(article_id=article_id).update(visit_count=F('visit_count') + 1)
    
    # Save the IP address in ArticleVisit
    ArticleVisit.objects.create(article_id=article, ip_address=request.META['REMOTE_ADDR'])
    return render(request, 'flipbook.html', {'article': article})

def download_article(request, article_id):
    article = get_object_or_404(article_table, pk=article_id)
    file_path = article.article_file.path
    file_name = os.path.basename(file_path)

    # Increment the download count for the article
    article.download_count = F('download_count') + 1
    article.save()
    
    # Save the IP address in ArticleDownload
    ArticleDownload.objects.create(article_id=article, ip_address=request.META['REMOTE_ADDR'])
    
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

def read_article(request, article_id):
    article = get_object_or_404(article_table, pk=article_id)
    
    # Increment the visit count for the article directly in the article_table
    article_table.objects.filter(article_id=article_id).update(visit_count=F('visit_count') + 1)
    
    # Save the IP address in ArticleVisit
    ArticleVisit.objects.create(article_id=article, ip_address=request.META['REMOTE_ADDR'])
    
    return redirect(f'/flipbook/{article_id}/')

#----------------------------------------------------------------------------------------------------------------------------------#