from django.contrib import messages
from django.shortcuts import get_object_or_404, render,redirect
from admin_module.models import article_table, author_table, dept_table, ea_table, issue_table, journal_table, review_table, volume_table
import hashlib
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.utils.dateformat import DateFormat
from django.contrib.auth.hashers import check_password, make_password
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail

# Create your views here.    
# Function to render the author's index page with submitted articles
def author_index(request):
    if request.session.has_key('author_email'):
        author_email = request.session['author_email']
        author = get_object_or_404(author_table, author_email=author_email)
        articles = article_table.objects.filter(author_id=author)
        article_details = []

        for article in articles:
            journal = article.issue_id.volume_id.journal_id
            author_names = ', '.join(filter(None, [article.author1, article.author2, article.author3]))
            submission_date = DateFormat(article.created_at).format('Y-m-d')
            article_details.append({
                'article_title': article.article_title,
                'journal_name': journal.journal_name,
                'author_names': author_names,
                'submission_date': submission_date,
                'status': article.status
            })

        return render(request, "author-index.html", {"author_email": author_email, "articles": article_details})
    else:
        return redirect('/p_index/#cta')   

#========================================================================================================================================================

def author_profile(request):
    if request.session.has_key('author_email'):
        author_email = request.session['author_email']
        author = get_object_or_404(author_table, author_email=author_email)
        
        if request.method == 'POST':
            # Update the author's details with form data
            author.author_name = request.POST.get('author_name')
            author.author_mobile = request.POST.get('author_mobile')
            author.author_address = request.POST.get('author_address')
            author.author_institute = request.POST.get('author_institute')
            author.save()
            
            # Add a success message
            messages.success(request, 'Profile changes saved successfully!')
            
            return redirect('author_profile')  # Redirect to the profile page
        
        return render(request, "author_profile.html", {"author": author})
    else:
        return redirect('/p_index/#cta')
    
def update_profile(request):
    if request.method == 'POST':
        # Retrieve form data
        name = request.POST.get('author_name')
        address = request.POST.get('author_address')
        mobile = request.POST.get('author_mobile')
        institute = request.POST.get('author_institute')
        
        # Update the user's profile in the database
        author_email = request.session.get('author_email')
        author = get_object_or_404(author_table, author_email=author_email)
        author.author_name = name
        author.author_address = address
        author.author_mobile = mobile
        author.author_institute = institute
        author.save()
        
        # Redirect back to the profile page with a success message
        messages.success(request, 'Profile changes saved successfully!')
        return redirect('author_profile')
    
    # Handle the case where the request method is not POST
    # This is to prevent direct access to the update profile URL
    return redirect('author_profile')

    
#========================================================================================================================================================

def author_forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            author = author_table.objects.get(author_email=email)
            token = get_random_string(50)
            author.token = token
            author.token_expiry = timezone.now() + timezone.timedelta(hours=1)
            author.save()
            
            reset_link = request.build_absolute_uri(f'/author_resetpswd/{token}/')
            send_mail(
                'Password Reset Request',
                f'Click the link below to reset your password:\n\n{reset_link}',
                'no-reply@example.com',
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'A password reset link has been sent to your email.')
            return redirect('/p_index/#cta/')
        except author_table.DoesNotExist:
            messages.error(request, 'Email address not found.')
            return render(request, "forgotpassword.html")
    
    return render(request, "forgotpassword.html")

def author_resetpswd(request, token):
    try:
        author = author_table.objects.get(token=token, token_expiry__gte=timezone.now())
        
        if request.method == 'POST':
            new_password = request.POST['new_password']
            confirm_password = request.POST['confirm_password']
            
            if len(new_password) < 8:
                messages.error(request, "New password must be at least 8 characters long.")
                return render(request, "resetpassword.html", {"token": token})
            
            if new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
                return render(request, "resetpassword.html", {"token": token})
            
            # Hash the new password before saving
            author.author_password = hashlib.sha1(new_password.encode('utf-8')).hexdigest()
            author.token = None
            author.token_expiry = None
            author.save()
            messages.success(request, "Password has been reset successfully.")
            return redirect('/p_index/#cta')
        
        return render(request, "resetpassword.html", {"token": token})
    except author_table.DoesNotExist:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return redirect('/author_forgotpassword/')


def author_resetpassword(request):
    if request.session.has_key('author_email'):
        author_email = request.session['author_email']
        author = author_table.objects.get(author_email=author_email)
        
        if request.method == 'POST':
            new_password = request.POST['new_password']
            confirm_password = request.POST['confirm_password']
            
            if len(new_password) < 8:
                messages.error(request, "New password must be at least 8 characters long.")
                return render(request, "author_resetpassword.html", {"author_email": author_email})

            if new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
                return render(request, "author_resetpassword.html", {"author_email": author_email})
            
            # Hash the new password before saving
            author.author_password = hashlib.sha1(new_password.encode('utf-8')).hexdigest()
            author.save()
            messages.success(request, "Password has been reset successfully.")
            return redirect('/author_resetpassword/')
        
        return render(request, "author_resetpassword.html", {"author_email": author_email})
    else:
        return redirect('/p_index/#cta')


#========================================================================================================================================================
def author_sidebar(request):

    if request.session.has_key('author_email'):
        author_email = request.session['author_email']
        user = author_table.objects.get(author_email=author_email)
        context = {
                'author_email': author_email,
                'author_name': user.author_name
        }
        return render(request, "editor_sidebar.html", {"author_email": author_email}, context)
    else:
        return redirect('/p_index/#cta')   

#========================================================================================================================================================
    
def author_submitarticle(request):
    if request.session.has_key('author_email'):
        author_email = request.session['author_email']
        author = get_object_or_404(author_table, author_email=author_email)
        departments = dept_table.objects.all()
        return render(request, "submit-article.html", {"author_name": author.author_name, "departments": departments})
    else:
        return redirect('/p_index/#cta')

def article_submission(request):
    if request.session.has_key('author_email'):
        if request.method == "POST":
            journal_id = request.POST.get('journalName')
            article_title = request.POST.get('articleTitle')
            article_file = request.FILES.get('articleFile')
            author_count = int(request.POST.get('authorCount'))
            authors = [request.POST.get(f'author{i}') for i in range(1, author_count + 1)]

            # Get the logged-in author
            author_email = request.session.get('author_email')
            author = get_object_or_404(author_table, author_email=author_email)

            # Get the open volume and issue for the selected journal
            open_volume = get_object_or_404(volume_table, journal_id=journal_id, status='open')
            open_issue = get_object_or_404(issue_table, volume_id=open_volume.volume_id, status='open')

            try:
                # Get the editor/admin with ea_id = 100 from ea_table
                editor_admin = get_object_or_404(ea_table, ea_id=100)

                # Save article details with ea_id set to editor/admin instance
                article = article_table(
                    issue_id=open_issue,
                    author_id=author,
                    article_title=article_title,
                    created_by=author.author_name,
                    status='pending approval',
                    author1=authors[0] if len(authors) > 0 else '',
                    author2=authors[1] if len(authors) > 1 else '',
                    author3=authors[2] if len(authors) > 2 else '',
                    article_file=article_file,
                    ea_id=editor_admin  # Assign editor/admin instance, not just ea_id
                )
                article.save()

                return redirect('/author_index/')  # Redirect to a success page after saving

            except ea_table.DoesNotExist:
                # Handle case where ea_id=100 does not exist in ea_table
                return render(request, 'error_page.html', {'error_message': 'Editor/Admin not found'})

        return redirect('submit_article')  # Redirect back to the form if not a POST request
    else:
        return redirect('/p_index/#cta')
    
def load_journals(request):
    department_id = request.GET.get('department_id')
    journals = journal_table.objects.filter(dept_id=department_id).all()
    return JsonResponse(list(journals.values('journal_id', 'journal_name')), safe=False)

#========================================================================================================================================================

def author_review(request):
    if request.session.has_key('author_email'):
        author_email = request.session['author_email']
        author = get_object_or_404(author_table, author_email=author_email)
        
        # Fetch articles authored by the current author
        articles = article_table.objects.filter(author_id=author)
        
        # Fetch reviews for these articles
        reviews = review_table.objects.filter(article_id__in=articles).select_related('article_id', 'editor_id')
        
        return render(request, "author_review.html", {'author': author, 'reviews': reviews})
    
    return redirect('/p_index/#cta')
    
#========================================================================================================================================================