from django.shortcuts import get_object_or_404, render,redirect
from admin_module.models import article_table, author_table, issue_table, journal_table, volume_table
import hashlib
from django.http import JsonResponse
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


def author_profile(request):
    if request.session.has_key('author_email'):
        author_email = request.session['author_email']
        return render(request, "author_profile.html", {"author_email": author_email})
    else:
        return redirect('/p_index/#cta')


def author_forgotpassword(request):
    if request.session.has_key('author_email'):
        author_email = request.session['author_email']
        return render(request, "author-forgotpassword.html", {"author_email": author_email})
    else:
        return redirect('/p_index/#cta')    


def author_resetpassword(request):
    if request.session.has_key('author_email'):
        author_email = request.session['author_email']
        return render(request, "author_resetpassword.html", {"author_email": author_email})
    else:
        return redirect('/p_index/#cta')

    
def author_submitarticle(request):
    if request.session.has_key('author_email'):
        author_email = request.session['author_email']
        journals = journal_table.objects.all()
        return render(request, "submit-article.html", {"author_email": author_email, "journals": journals})
    else:
        return redirect('/p_index/#cta')    


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
            authors = [request.POST.get(f'author{i+1}') for i in range(author_count)]

            # Get the logged-in author
            author_email = request.session.get('author_email')
            author = get_object_or_404(author_table, author_email=author_email)

            # Save the article file
            file_path = default_storage.save(f'articles/{article_file.name}', article_file)

            # Save article details
            article = article_table(
                issue_id=get_object_or_404(issue_table, pk=issue_id),
                author_id=author,
                article_title=article_title,
                created_by=author.author_name,
                status='pending approval',
                author1=authors[0] if author_count >= 1 else '',
                author2=authors[1] if author_count >= 2 else '',
                author3=authors[2] if author_count >= 3 else ''
            )
            article.save()

            return redirect('/author_index/')  # Redirect to a success page

        return redirect('submit_article')  # Redirect back to the form if not a POST request
    else:
        return redirect('/p_index/#cta')

# Function to dynamically load volumes based on the selected journal
def load_volumes(request):
    journal_id = request.GET.get('journal_id')
    volumes = volume_table.objects.filter(journal_id=journal_id).all()
    return JsonResponse(list(volumes.values('volume_id', 'volume')), safe=False)

# Function to dynamically load issues based on the selected volume
def load_issues(request):
    volume_id = request.GET.get('volume_id')
    issues = issue_table.objects.filter(volume_id=volume_id).all()
    return JsonResponse(list(issues.values('issue_id', 'issue_no')), safe=False)