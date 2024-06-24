import os
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.db.models import Q
import hashlib
import random
from django.db.models import F
from django.core.mail import send_mail
from django.contrib import messages
from django.template.loader import render_to_string
from admin_module.models import  message_table, ArticleDownload, ArticleVisit, JournalPageVisit, article_table, author_table, ea_table, issue_table,volume_table,journal_table,dept_table,eb_table,notification_table,gl_table
from editor_module.views import add_watermark_and_page_numbers, generate_article_pdf, merge_pdfs

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
    volumes = volume_table.objects.filter(journal_id=journal_id).exclude(status='inactive')

    # Create a list to store volume and issue information
    volume_issues_list = []

    for volume in volumes:
        # Retrieve issues for each volume that are either 'open' or 'closed'
        issues = issue_table.objects.filter(volume_id=volume.volume_id).exclude(status='inactive').order_by('-created_at')

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

    # Check if the journal status is closed
    if j_data.status.lower() != 'active':
        return redirect('/p_index/')  # name of the view you want to redirect to

    # Fetch the latest issue for the journal
    latest_issue = issue_table.objects.filter(volume_id__journal_id=id).order_by('-issue_id').first()
    
    # Fetch editorial board and notifications data
    p_data = eb_table.objects.filter(journal_id=id, status='active')
    n_data = notification_table.objects.filter(journal_id=id, status='active')

    # Check for journal ethics and submission guidelines
    has_ethics = bool(j_data.journal_ethics)
    has_guidelines = gl_table.objects.filter(journal_id=id).exists()

    # Check for a banner
    has_banner = bool(j_data.banner)

    # Get the client's IP address
    ip_address = get_client_ip(request)

    # Log the visit count or perform other tracking here

    context = {
        'jdata': j_data,
        'latest_issue': latest_issue,
        'pdata': p_data,
        'ndata': n_data,
        'has_ethics': has_ethics,
        'has_guidelines': has_guidelines,
        'has_banner': has_banner,
        'visit_count': j_data.visit_count,
    }

    return render(request, 'p_home.html', context)

def get_client_ip(request):
    # Function to get client IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def search_results(request, journal_id):
    query = request.GET.get('q')
    journal = get_object_or_404(journal_table, pk=journal_id)
    
    # Collecting content from the journal's various sections
    results = []
    
    if query:
        # Search in journal aim
        index = journal.journal_aim.lower().find(query.lower())
        if index != -1:
            results.append({
                'section': 'Aim & Scopes',
                'url': f'/p_home/{journal.journal_id}/#aimscope?q={query}&index={index}',
                'context': journal.journal_aim,
                'index': index
            })

        # Search in journal ethics
        index = journal.journal_ethics.lower().find(query.lower())
        if index != -1:
            results.append({
                'section': 'Ethics & Disclosure',
                'url': f'/p_ethics/{journal.journal_id}/?q={query}&index={index}',
                'context': journal.journal_ethics,
                'index': index
            })

        # Search in journal_table for p_home sections
        contact_results = journal_table.objects.filter(email__icontains=query) | journal_table.objects.filter(phone__icontains=query)
        for contact in contact_results:
            results.append({
                'section': 'Contact',
                'url': f'/p_home/{journal.journal_id}/#contact?q={query}&index={index}',
                'context': contact.email or contact.phone,
                'index': (contact.email or contact.phone).lower().find(query.lower())
            })

        journal_update_results = notification_table.objects.filter(notification__icontains=query)
        for update in journal_update_results:
            results.append({
                'section': 'Journal Notifications',
                'url': update.link,
                'context': update.notification,
                'index': update.notification.lower().find(query.lower())
            })

        editorial_results = eb_table.objects.filter(editor_name__icontains=query)
        for editor in editorial_results:
            results.append({
                'section': 'Editorial Board',
                'url': f'p_home/{journal.journal_id}/#editorialboard/?q={query}&index={index}',
                'context': editor.editor_name,
                'index': editor.editor_name.lower().find(query.lower())
            })

        # Search in gl_table for p_guidelines.html
        guidelines_results = gl_table.objects.filter(heading__icontains=query) | gl_table.objects.filter(content__icontains=query)
        for guideline in guidelines_results:
            index = guideline.heading.lower().find(query.lower())
            if index == -1:
                index = guideline.content.lower().find(query.lower())
            results.append({
                'section': 'Guidelines',
                'url': f'/p_guidelines/{journal.journal_id}/',
                'context': guideline.heading if guideline.heading.lower().find(query.lower()) != -1 else guideline.content,
                'index': index
            })

        # Search in issue_table for issue_detail.html
        issue_results = issue_table.objects.filter(issue_no__icontains=query)
        for issue in issue_results:
            results.append({
                'section': 'Issue',
                'url': f'/issue_detail/{issue.issue_id}/?q={query}&index={issue.issue_no.lower().find(query.lower())}',
                'context': issue.issue_no,
                'index': issue.issue_no.lower().find(query.lower())
            })

        # Search articles within each issue for issue_detail.html
        article_results = article_table.objects.filter(article_title__icontains=query)
        for article in article_results:
            issue = article.issue_id
            results.append({
                'section': 'Article',
                'url': f'/issue_detail/{issue.issue_id}/?q={query}&index={article.article_title.lower().find(query.lower())}',
                'context': article.article_title,
                'index': article.article_title.lower().find(query.lower())
            })

        # Search in volume_table for p_alljournals.html
        volume_results = volume_table.objects.filter(volume__icontains=query)
        for volume in volume_results:
            results.append({
                'section': 'Volume',
                'url': f'/p_alljournals/{journal.journal_id}/?q={query}&index={index}',
                'context': volume.volume,
                'index': volume.volume.lower().find(query.lower())
            })
    

        # Add other search conditions here
        # ...

    context = {
        'query': query,
        'results': results,
        'journal': journal,
    }
    
    return render(request, 'search_results.html', context)
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
            'authors': authors_str,
            'visit_count': article.visit_count,
            'download_count': article.download_count
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
    original_file_path = article.article_file.path
    file_name = os.path.basename(original_file_path)
    
    # Path to the watermarked PDF
    watermarked_pdf_path = os.path.join(settings.MEDIA_ROOT, 'merged_pdfs', f'watermarked_{file_name}')
    
    # Check if watermarked PDF exists
    if os.path.exists(watermarked_pdf_path):
        file_path = watermarked_pdf_path
    else:
        # Generate the watermarked PDF if it does not exist
        generated_pdf_path = generate_article_pdf(article, request)
        merged_pdf_path = merge_pdfs(generated_pdf_path, original_file_path, article.issue_id.volume_id.journal_id.journal_name, article)
        file_path = merged_pdf_path
    
    # Increment the download count for the article
    article.download_count = F('download_count') + 1
    article.save()
    
    # Save the IP address in ArticleDownload
    ArticleDownload.objects.create(article_id=article, ip_address=request.META['REMOTE_ADDR'])
    
    # Serve the file
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
def d_flipbook(request, article_id):
    article = get_object_or_404(article_table, pk=article_id)
    
    # Increment the visit count for the article directly in the article_table
    article_table.objects.filter(article_id=article_id).update(visit_count=F('visit_count') + 1)
    
    # Save the IP address in ArticleVisit
    ArticleVisit.objects.create(article_id=article, ip_address=request.META['REMOTE_ADDR'])
    
    return render(request, 'd_flipbook.html', {'article': article})

#--------------------------------------------------------------------------------------------------------------------------------------------

def message(request):
    if request.method == 'POST':
        # Get the form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message_content = request.POST.get('message')
        journal_id = request.POST.get('journal_id')  # Get the journal_id from the form data

        # Validate the form data (basic validation)
        if not name or not email or not subject or not message_content or not journal_id:
            return JsonResponse({'success': False, 'error': 'All fields are required.'})

        # Fetch the journal from the database
        try:
            journal = journal_table.objects.get(pk=journal_id)
        except journal_table.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Journal not found.'})

        # Fetch the editor for the journal
        editor = journal.editor
        if not editor or editor.status.lower() != 'active':
            return JsonResponse({'success': False, 'error': 'Editor not found or not active.'})

        # Save the message to the database
        new_message = message_table(
            journal_id=journal,
            ea_id=editor,
            msg_name=name,
            msg_email=email,
            subject=subject,
            message=message_content
        )
        new_message.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})
