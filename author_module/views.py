from django.contrib import messages
from django.shortcuts import get_object_or_404, render,redirect
from admin_module.models import article_table, author_table, dept_table, issue_table, journal_table, review_table, volume_table
import hashlib
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.utils.dateformat import DateFormat

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

#def author_forgotpassword(request):
    if request.session.has_key('author_email'):
        author_email = request.session['author_email']
        return render(request, "author-forgotpassword.html", {"author_email": author_email})
    else:
        return redirect('/p_index/#cta')    


#def author_resetpassword(request):
    if request.session.has_key('author_email'):
        author_email = request.session['author_email']
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

# Function to handle form submission
def article_submission(request):
    if request.session.has_key('author_email'):
        if request.method == "POST":
            journal_id = request.POST.get('journalName')
            volume_id = request.POST.get('volume')
            issue_id = request.POST.get('issueNumber')
            article_title = request.POST.get('articleTitle')
            article_file = request.FILES.get('articleFile')
            author_count = int(request.POST.get('authorCount'))
            authors = [request.POST.get(f'author{i}') for i in range(1, author_count + 1)]

            # Get the logged-in author
            author_email = request.session.get('author_email')
            author = get_object_or_404(author_table, author_email=author_email)

            # Save article details
            article = article_table(
                issue_id=get_object_or_404(issue_table, pk=issue_id),
                author_id=author,
                article_title=article_title,
                created_by=author.author_name,
                status='pending approval',
                author1=authors[0] if len(authors) > 0 else '',
                author2=authors[1] if len(authors) > 1 else '',
                author3=authors[2] if len(authors) > 2 else '',
                article_file=article_file  # Save the uploaded file
            )
            article.save()

            return redirect('/author_index/')  # Redirect to a success page

        return redirect('submit_article')  # Redirect back to the form if not a POST request
    else:
        return redirect('/p_index/#cta')

    
def load_journals(request):
    department_id = request.GET.get('department_id')
    journals = journal_table.objects.filter(dept_id=department_id).all()
    return JsonResponse(list(journals.values('journal_id', 'journal_name')), safe=False)

def load_volumes(request):
    journal_id = request.GET.get('journal_id')
    volumes = volume_table.objects.filter(journal_id=journal_id).all()
    return JsonResponse(list(volumes.values('volume_id', 'volume')), safe=False)

def load_issues(request):
    volume_id = request.GET.get('volume_id')
    issues = issue_table.objects.filter(volume_id=volume_id).all()
    return JsonResponse(list(issues.values('issue_id', 'issue_no')), safe=False)

#========================================================================================================================================================

def author_review(request):
    if request.session.has_key('author_email'):
        author_email = request.session['author_email']
        return render(request, "author_review.html", {"author_email": author_email})
    else:
        return redirect('/p_index/#cta')

def view_review(request):
    if request.session.has_key('author_email'):
        author_email = request.session['author_email']
        author = get_object_or_404(author_table, author_email=author_email)
        articles = article_table.objects.filter(author_id=author.author_id)
        article_ids = articles.values_list('article_id', flat=True)
        
        # Retrieve the review objects from the database using the article_ids
        reviews = review_table.objects.filter(article_id__in=article_ids).select_related('article_id', 'editor_id')
        
        # Pass the reviews queryset to the template for rendering
        return render(request, 'author_review.html', {'reviews': reviews})
    else:
        # Handle the case when the author is not logged in
        return HttpResponse("You must be logged in as an author to view reviews.")
    
#========================================================================================================================================================