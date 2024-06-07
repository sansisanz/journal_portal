import json
import os
from PyPDF2 import PdfMerger
from weasyprint import HTML, html
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from django.views.decorators.http import require_POST
from admin_module.models import ArticleDownload, ArticleVisit, JournalPageVisit, article_table, author_table, ea_table, dept_table, gl_table, journal_table, notification_table, review_table, volume_table, issue_table, eb_table
# Create your views here.

def editor_article(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "article.html", {"empid": empid})
    else:
        return redirect('/login/')

def editorialboard(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        # Fetch journals assigned to the logged-in user
        journals = journal_table.objects.filter(editor__employee_id=empid)
        return render(request, "editorialboard.html", {"empid": empid, "journals": journals})
    else:
        return redirect('/login/')
      
def add_editorial_board_member(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        user_name = request.session['editor_name']
    
    if request.method == 'POST':
        journals = request.POST.get('journalname')
        editor_name = request.POST.get('full_name')
        editor_address = request.POST.get('office_address')
        editor_email = request.POST.get('email_address')
        editor_mobile = request.POST.get('phone_number')
        photo = request.FILES.get('Upload Photo')
        created_by = user_name  # You need to set the creator value

        # Check if a member with the same details already exists
        existing_member = eb_table.objects.filter(
            journal_id=journals,
            editor_name=editor_name,
            editor_address=editor_address,
            editor_email=editor_email,
            editor_mobile=editor_mobile
        ).exists()

        if existing_member:
            messages.warning(request, 'A member with the same details already exists.')
            return redirect('/editorialboard/')  # Redirect to the same page
        else:
            editor = ea_table.objects.get(employee_id=empid)
            editor_id = editor.ea_id
            journal = journal_table.objects.get(journal_id=journals)

            # Create an Editorial Board Member object
            new_member = eb_table(
                journal_id=journal,
                editor_name=editor_name,
                editor_address=editor_address,
                editor_email=editor_email,
                editor_mobile=editor_mobile,
                created_by=user_name,
                status="Active",  # Set the default status
                photo=photo
            )
            new_member.save()
            messages.success(request, 'New member added successfully.')
            return redirect('/editorialboard/')  # Redirect to a success page after saving
    else:
        return render(request, 'editorialboard.html')
     


def editor_forgotpassword(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "forgot-password.html", {"empid": empid})
    else:
        return redirect('/login/')

def editor_index(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "editorindex.html")
        
    return redirect('/login')

#------------------------------------------------------------------------------------------------------------------------------------

def editor_assignedjournal(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        # Fetch the logged-in editor
        editor = ea_table.objects.get(employee_id=empid)
        # Fetch journals assigned to the editor
        journals = journal_table.objects.filter(editor=editor)
        # Create a list of dictionaries to pass to the template
        journal_data = []
        for index, journal in enumerate(journals, start=1):
            journal_data.append({
                'si_no': index,
                'journal_name': journal.journal_name,
                'dept_name': journal.dept_id.dept_name,
                'journal_id': journal.journal_id
            })
        return render(request, "assignedjournal.html", {"journal_data": journal_data})
    else:
        return redirect('/login')
    
def add_vic(request, journal_id):
    if not request.session.has_key('empid'):
        return redirect('/login')

    empid = request.session['empid']
    user_name = request.session['editor_name']

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'add_vol':
            # Retrieve form data for adding volume
            volume_name = request.POST.get('volume')

            # Get the journal corresponding to the provided journal_id
            journal = journal_table.objects.get(pk=journal_id)

            # Check if volume with the same name already exists
            existing_volume = volume_table.objects.filter(journal_id=journal, volume=volume_name).first()
            if existing_volume:
                if existing_volume.status == 'active':
                    messages.warning(request, 'Volume with the same name already exists.', extra_tags='add_vol_alert')
                    return render(request, 'add_vic.html', {
                        'journal_id': journal_id,
                        'volumes': volume_table.objects.filter(journal_id=journal_id, status='active')
                    })
                else:
                    # Update the existing volume to active status
                    existing_volume.status = 'active'
                    existing_volume.save()
                    messages.success(request, 'Volume added successfully.', extra_tags='add_vol_success')
                    return redirect('/add_vic/{}/'.format(journal_id))

            # Create a new volume entry for the journal
            new_volume = volume_table.objects.create(
                journal_id=journal,
                volume=volume_name,
                created_by=user_name,
                status='active'
            )

            messages.success(request, 'Volume added successfully.', extra_tags='add_vol_success')
            return redirect('/add_vic/{}/'.format(journal_id))   # Change this to your success URL

        elif form_type == 'add_issue':
            # Retrieve form data for adding issue
            volume_id = request.POST.get('volume_id')
            issue_number = int(request.POST.get('issue_number'))
            cover_image = request.FILES.get('cover_image')

            # Check if the issue already exists
            existing_issue = issue_table.objects.filter(volume_id=volume_id, issue_no=str(issue_number)).first()
            if existing_issue:
                if existing_issue.status == 'active':
                    messages.warning(request, 'Issue already exists.', extra_tags='add_issue_alert')
                    return render(request, 'add_vic.html', {
                        'journal_id': journal_id,
                        'volumes': volume_table.objects.filter(journal_id=journal_id, status='active')
                    })
                else:
                    # Update the existing issue to active status
                    existing_issue.status = 'active'
                    existing_issue.save()
                    messages.success(request, 'Issue added successfully.', extra_tags='add_issue_success')
                    return redirect('/add_vic/{}/'.format(journal_id))

            # Create a new issue for the selected volume
            issue_table.objects.create(
                volume_id=volume_table.objects.get(pk=volume_id),
                issue_no=str(issue_number),
                cover_image=cover_image,
                created_by=user_name,
                status='active'
            )

            messages.success(request, 'Issue added successfully.', extra_tags='add_issue_success')
            return redirect('/add_vic/{}/'.format(journal_id))  # Change this to your success URL

    # On GET request, render the form with volume options
    return render(request, 'add_vic.html', {
        'journal_id': journal_id,
        'volumes': volume_table.objects.filter(journal_id=journal_id, status='active')
    })


#---------------------------------------------------------------------------------------------------------------

def editorprofile(request):

    if request.session.has_key('empid'):
            empid = request.session.get('empid')
            user = get_object_or_404(ea_table, employee_id=empid)
            return render(request, 'editorprofile.html', {'user': user})
    else:
        return redirect('/login/')
    

def editorresetpassword(request):
    
    if request.session.has_key('empid'):
        empid = request.session['empid']        
        user = get_object_or_404(ea_table, employee_id=empid)
        return render(request, "adminresetpassword.html", {"user": user})

    else:
        return redirect('/login/')
    
#---------------------------------------------------------------------------------------------------------------    
    
def editor_sidebar(request):

    if request.session.has_key('empid'):
        empid = request.session['empid']

        user = ea_table.objects.get(employee_id=empid)
        context = {
                'empid': empid,
                'name': user.ea_name,
                'email': user.ea_email
        }
        return render(request, "editor_sidebar.html", {"empid": empid}, context)
    else:
        return redirect('/login')    
    
#---------------------------------------------------------------------------------------------------------------    

def notifications(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        # Fetch journals assigned to the logged-in user
        journals = journal_table.objects.filter(editor__employee_id=empid)
        return render(request, "notifications.html", {"empid": empid, "journals": journals})
    else:
        return redirect('/login')
    
def notify(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        if request.method == 'POST':
            journal_id = request.POST.get('journalname')
            notification = request.POST.get('volume')
            link = request.POST.get('next_volume')

            # Get the editor's ID (ea_id) based on the employee_id
            editor = ea_table.objects.get(employee_id=empid)
            editor_id = editor.ea_id

            # Get the selected journal
            journal = journal_table.objects.get(journal_id=journal_id)

            # Create and save the new notification
            new_notification = notification_table(
                journal_id=journal,
                notification=notification,
                link=link,
                created_by=editor.ea_name,
                status='active'
            )
            new_notification.save()

            return redirect('/editor_index/')  # Redirect to a success page after form submission
        else:
            # Fetch journals assigned to the logged-in user
            editor = ea_table.objects.get(employee_id=empid)
            journals = journal_table.objects.filter(editor=editor)

            return render(request, "notifications.html", {"journals": journals})
    else:
        return redirect('/login')
    
#---------------------------------------------------------------------------------------------------------------    
def view_articles(request):   
    if request.session.has_key('empid'):
        empid = request.session['empid']
        # Fetch journals assigned to the logged-in user
        journals = journal_table.objects.filter(editor__employee_id=empid)

        # Fetch articles related to those journals
        articles = article_table.objects.filter(issue_id__volume_id__journal_id__in=journals)

        return render(request, "view_articles.html", {"empid": empid, "articles": articles})
    else:
        return redirect('/login') 

def view_article(request, article_id):
    article = get_object_or_404(article_table, pk=article_id)
    # Assuming the article_file field contains the path to the PDF file
    pdf_path = os.path.join(settings.MEDIA_ROOT, str(article.article_file))
    with open(pdf_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(pdf_path)
        return response

def approve_article(request, article_id):
    article = get_object_or_404(article_table, pk=article_id)
    
    if article.status == 'approved':
        messages.warning(request, 'The article has already been approved.')
    else:
        # Update article status
        article.status = 'approved'
        article.save()
        
        # Generate the PDF from the template
        pdf_file_path = generate_article_pdf(article)
        
        # Merge the generated PDF with the article's PDF
        merged_pdf_path = merge_pdfs(pdf_file_path, article.article_file.path)
        
        # Update the article file with the merged PDF
        article.article_file.name = os.path.relpath(merged_pdf_path, settings.MEDIA_ROOT)
        article.save()
        
        # Add a success message
        messages.success(request, 'The article has been successfully approved.')
    
    return redirect('/view_articles/')

def generate_article_pdf(article):
    # Fetch related details
    journal = article.issue_id.volume_id.journal_id
    department = journal.dept_id.dept_name
    volume = article.issue_id.volume_id.volume
    issue = article.issue_id.issue_no
    
    # Prepare context for the template
    context = {
        'journal_name': journal.journal_name,
        'department': department,
        'volume': volume,
        'issue': issue,
        'article_title': article.article_title,
        'authors': ', '.join(filter(None, [article.author1, article.author2, article.author3])),
        'url': f'{settings.MEDIA_URL}merged_pdfs/article_{os.path.basename(article.article_file.name)}',
        'published_by': journal.journal_name,
    }
    
    # Render HTML content from template
    html_content = render_to_string('pdftemp.html', context)
    
    # Define the path for the generated PDF
    generated_pdfs_dir = os.path.join(settings.MEDIA_ROOT, 'generated_pdfs')
    os.makedirs(generated_pdfs_dir, exist_ok=True)
    pdf_file_path = os.path.join(generated_pdfs_dir, f'{article.article_id}_pg1.pdf')
    
    # Generate PDF file from HTML content
    HTML(string=html_content).write_pdf(pdf_file_path)
    
    return pdf_file_path

def merge_pdfs(generated_pdf_path, article_pdf_path):
    merger = PdfMerger()
    
    # Append the generated PDF first, then the article PDF
    merger.append(generated_pdf_path)
    merger.append(article_pdf_path)
    
    merged_pdfs_dir = os.path.join(settings.MEDIA_ROOT, 'merged_pdfs')
    os.makedirs(merged_pdfs_dir, exist_ok=True)
    merged_pdf_path = os.path.join(merged_pdfs_dir, f'article_{os.path.basename(article_pdf_path)}')
    with open(merged_pdf_path, 'wb') as merged_file:
        merger.write(merged_file)
    
    return merged_pdf_path

def reject_article(request, article_id):
    article = get_object_or_404(article_table, pk=article_id)
    
    if article.status == 'pending approval':
        article.status = 'rejected'
        article.save()
        messages.success(request, 'The article has been rejected.')
    elif article.status == 'rejected':
        messages.warning(request, 'The article has already been rejected.')
    else:
        messages.warning(request, 'The article cannot be rejected.')
    
    return redirect('/view_articles/')

def accept_article(request, article_id):
    article = get_object_or_404(article_table, pk=article_id)
    
    if article.status == 'pending approval':
        article.status = 'accepted'
        article.save()
        messages.success(request, 'The article has been accepted for peer review.')
    elif article.status == 'accepted':
        messages.warning(request, 'The article has already been accepted.')
    else:
        messages.warning(request, 'The article cannot be accepted.')
    
    return redirect('/view_articles/')

#---------------------------------------------------------------------------------------------------------------    

def journaldetails(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        # Fetch journals assigned to the logged-in user
        journals = journal_table.objects.filter(editor__employee_id=empid)
        return render(request, "journaldetails.html", {"empid": empid, "journals": journals})
    else:
        return redirect('/login')


def journal_details(request):
    if request.session.has_key('empid'):
        if request.method == 'POST':
            empid = request.session['empid']
            journal_id = request.POST.get('journalname')
            aims_scope = request.POST.get('aimsScope')
            ethics = request.POST.get('ethics')

            # Get the editor's ID (ea_id) based on the employee_id
            editor = ea_table.objects.get(employee_id=empid)
            editor_id = editor.ea_id

            # Save aims_scope and ethics to journal_table
            journal = journal_table.objects.get(journal_id=journal_id)
            journal.journal_aim = aims_scope
            journal.journal_ethics = ethics
            journal.save()

            # Save guidelines to gl_table
            total_contents = int(request.POST.get('totalContents'))
            for i in range(1, total_contents + 1):
                heading = request.POST.get(f'heading_{i}')
                content = request.POST.get(f'content_{i}')
                guideline = gl_table(journal_id=journal, heading=heading, content=content)
                guideline.save()

            return redirect('/editor_index/')  # Redirect to success page after form submission
    else:
        return redirect('/login')
 
#---------------------------------------------------------------------------------------------------------------

def upddetails(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        
        # Fetch journals assigned to the logged-in user
        journals = journal_table.objects.filter(editor__employee_id=empid)

        # Prepare the data for the template
        journal_data = []
        for journal in journals:
            volumes = volume_table.objects.filter(journal_id=journal.journal_id)
            total_volumes = volumes.count()
            total_issues = issue_table.objects.filter(volume_id__in=volumes).count()
            total_articles = article_table.objects.filter(issue_id__in=issue_table.objects.filter(volume_id__in=volumes)).count()
            
            journal_data.append({
                'journal_id': journal.journal_id,
                'journal_name': journal.journal_name,
                'total_volumes': total_volumes,
                'total_issues': total_issues,
                'total_articles': total_articles
            })

        return render(request, "upddetails.html", {"empid": empid, "journal_data": journal_data})
    else:
        return redirect('/login/')

def edit_vic(request, journal_id):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        
        # Fetch volumes for the selected journal
        volumes = volume_table.objects.filter(journal_id=journal_id)
        
        return render(request, "edit_vic.html", {"empid": empid, "volumes": volumes, "journal_id": journal_id})
    else:
        return redirect('/login/')

def edit_volume(request, journal_id):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        editor = ea_table.objects.get(employee_id=request.session['empid'])
        editor_name = editor.ea_name

        if request.method == 'POST':
            volume_id = request.POST.get('volume')
            volume = get_object_or_404(volume_table, volume_id=volume_id)

            # Update Volume Name
            if request.POST.get('updateVolume') == 'on':
                volume_name = request.POST.get('volumeName')
                if volume_name:
                    volume.volume = volume_name
                    volume.save()
                    messages.success(request, 'Volume name updated successfully.')

            # Update Cover Photo
            if request.POST.get('updateCoverPhoto') == 'on':
                if 'coverPhoto' in request.FILES:
                    cover_photo = request.FILES['coverPhoto']
                    volume.cover_image = cover_photo
                    volume.save()
                    messages.success(request, 'Cover photo updated successfully.')

            # Add More Issues
            if request.POST.get('addMoreIssues') == 'on':
                more_issues = request.POST.get('issueNumber')
                if more_issues:
                    more_issues = int(more_issues)
                    last_issue = issue_table.objects.filter(volume_id=volume).order_by('issue_no').last()
                    start_issue_no = int(last_issue.issue_no) + 1 if last_issue else 1


                    for i in range(more_issues):
                        new_issue = issue_table(
                            volume_id=volume,
                            issue_no=start_issue_no + i,
                            created_by=editor_name,
                            status='active'
                        )
                        new_issue.save()
                    messages.success(request, f'{more_issues} issues added successfully.')

        return redirect('/edit_vic/{}/'.format(journal_id))
    else:
        return redirect('/login/')

    #------------------------------------------------------------------------------------------------------------------------------------------------------- 
def remove(request, journal_id):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        
        # Fetch volumes, issues, and articles for the selected journal
        volumes = volume_table.objects.filter(journal_id=journal_id)
        issues = issue_table.objects.filter(volume_id__journal_id=journal_id)
        articles = article_table.objects.filter(issue_id__volume_id__journal_id=journal_id)

        # Fetch journal details
        journal = get_object_or_404(journal_table, journal_id=journal_id)
        guidelines = gl_table.objects.filter(journal_id=journal_id)

        return render(request, "remove.html", {
            "empid": empid,
            "volumes": volumes,
            "issues": issues,
            "articles": articles,
            "journal_id": journal_id,
            "journal": journal,
            "guidelines": guidelines
        })
    else:
        return redirect('/login/')

def remove_volume(request, journal_id):
    if request.method == 'POST':
        # Logic to handle form submission for volume removal
        # Retrieve selected volume_id from POST data
        volume_id = request.POST.get('volume_id')
        
        # Set volume and issues as inactive
        volume = volume_table.objects.get(pk=volume_id)
        volume.status = 'inactive'
        volume.save()
        
        issues = issue_table.objects.filter(volume_id=volume_id)
        for issue in issues:
            issue.status = 'inactive'
            issue.save()
        
        # Set articles status as 'removed'
        articles = article_table.objects.filter(issue_id__volume_id=volume_id)
        for article in articles:
            article.status = 'removed'
            article.save()
        
        # Redirect to remove view with journal_id
        return redirect(f'/remove/{journal_id}/')
    else:
        # Handle GET request (display confirmation message or modal)
        return render(request, 'confirmation_modal.html', {
            'journal_id': journal_id,
            # Pass any additional data needed for confirmation
        })  
    
def remove_issue(request, journal_id):
    if request.method == 'POST':
        volume_id = request.POST.get('volume_id')
        issue_id = request.POST.get('issue_id')

        # Set issue status to inactive
        issue = issue_table.objects.get(pk=issue_id)
        issue.status = 'inactive'
        issue.save()

        # Set articles status to 'removed' for articles under the removed issue
        articles = article_table.objects.filter(issue_id=issue_id)
        for article in articles:
            article.status = 'removed'
            article.save()

        return redirect(f'/remove/{journal_id}/')
    else:
        volumes = volume_table.objects.filter(journal_id=journal_id, status='active')
        return render(request, 'remove_issue.html', {'volumes': volumes, 'journal_id': journal_id})
        
#-------------------------------------------------------------------------------------------------------------------------------------    

def edit(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "edit.html", {"empid": empid})
    else:
        return redirect('/login')
#--------------------------------------------------------------------------------

def e_visits(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        # Get the logged-in editor
        editor = ea_table.objects.get(employee_id=empid)
        
        # Get the journals associated with the editor
        journals = journal_table.objects.filter(editor=editor)
        return render(request, "e_visits.html", {"empid": empid, "journals": journals})
    else:
        return redirect('/login')    

def get_journals_by_editor(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        editor = ea_table.objects.get(employee_id=empid)
        journals = journal_table.objects.filter(editor=editor).values('journal_id', 'journal_name')
        return JsonResponse(list(journals), safe=False)
    return JsonResponse([], safe=False)

def get_volumes_by_journal(request):
    journal_id = request.GET.get('journal_id')
    volumes = volume_table.objects.filter(journal_id=journal_id).values('volume_id', 'volume')
    return JsonResponse(list(volumes), safe=False)

def get_issues_by_volume(request):
    volume_id = request.GET.get('volume_id')
    issues = issue_table.objects.filter(volume_id=volume_id).values('issue_id', 'issue_no')
    return JsonResponse(list(issues), safe=False)

def get_articles_by_issue(request):
    issue_id = request.GET.get('issue_id')
    articles = article_table.objects.filter(issue_id=issue_id).values('article_id', 'article_title', 'download_count')
    return JsonResponse(list(articles), safe=False)
        
def get_journal_visit_count(request):
    journal_id = request.GET.get('journal_id')
    visit_count = JournalPageVisit.objects.filter(journal_id=journal_id).count()
    return JsonResponse({'visit_count': visit_count})

def get_article_visit_count(request):
    article_id = request.GET.get('article_id')
    visit_count = ArticleVisit.objects.filter(article_id=article_id).count()
    return JsonResponse({'visit_count': visit_count})

def get_article_download_count(request):
    article_id = request.GET.get('article_id')
    download_count = ArticleDownload.objects.filter(article_id=article_id).count()
    return JsonResponse({'download_count': download_count})


#---------------------------------------------------------------------------------------------------------------

def editor_contact(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        # Fetch journals assigned to the logged-in user
        journals = journal_table.objects.filter(editor__employee_id=empid)
        departments = dept_table.objects.all()
        return render(request, "editor_contact.html", {"empid": empid, "journals": journals, 'departments':departments})
    else:
        return redirect('/login')
    
def add_contact(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        user_name = request.session['editor_name']

    if request.method == 'POST':
        journals = request.POST.get('journal_id')
        departments = request.POST.get('dept_id')
        editor_email = request.POST.get('email_address')
        editor_mobile = request.POST.get('phone_number')
        created_by = user_name  # You need to set the creator value

        editor = ea_table.objects.get(employee_id=empid)
        editor_id = editor.ea_id
        journal = journal_table.objects.get(journal_id=journals)

        # Create an Editorial Board Member object
        journal.email=editor_email
        journal.phone=editor_mobile
        created_by=user_name
        status="Active"  # Set the default status
       
        journal.save()
        
        return redirect('/editor_index/')  # Redirect to a success page after saving
    else:
        return render(request,'add_contact.html')
    
#-----------------------------------------------------------------------------------------------------

def edit_journals(request, journal_id):
    if 'empid' in request.session:
        empid = request.session['empid']
        jdata = get_object_or_404(journal_table, journal_id=journal_id)
        ebdata = eb_table.objects.filter(journal_id=journal_id)
        volumes = volume_table.objects.filter(journal_id=journal_id)
        notifications = notification_table.objects.filter(journal_id=journal_id)
        contact = get_object_or_404(journal_table, journal_id=journal_id)
        gdata = gl_table.objects.filter(journal_id=journal_id)

        return render(request, "edit_journals.html", {
            "empid": empid,
            "jdata": jdata,
            "ebdata": ebdata,
            "volumes": volumes,
            "notifications": notifications,
            "contact": contact,
            "gdata": gdata,
            "journal_id": journal_id
        })
    else:
        return redirect('/login/')

def update_volume_name(request, volume_id):
    if request.method == 'POST':
        volume_id = request.POST.get('volume_id')
        new_volume_name = request.POST.get('volume_name')
        volume = get_object_or_404(volume_table, volume_id=volume_id)
        volume.volume = new_volume_name
        volume.save()
        messages = ["Volume name updated successfully."]
        return redirect(f'/edit_journal/{volume.journal_id}/')
    
    if request.method == 'GET' and request.is_ajax():
        volume = get_object_or_404(volume_table, volume_id=volume_id)
        return JsonResponse({'volume_name': volume.volume})
    
#-------------------------------------------------------------------------------------------------------

def contact_edit(request,journal_id):
    if request.method == 'POST':
        mobile = request.POST.get("contact")
        email = request.POST.get("mail")
        cdata = journal_table.objects.get(journal_id=journal_id)
        cdata.phone = mobile
        cdata.email = email
        cdata.save()

    return render(request,"edit_journals.html")

#--------------------------------------------------------------------------------------------------------

def details_edit(request,journal_id):
    if request.method == 'POST':
        aim = request.POST.get("aimsScope")
        ethics = request.POST.get("ethics")
        ghead = request.POST.get("heading")
        guidecontent = request.POST.get("content")
        ddata = journal_table.objects.get(journal_id=journal_id)
        ddata.journal_aim = aim
        ddata.journal_ethics = ethics
        ddata.heading = ghead
        ddata.content = guidecontent
        ddata.save()

    return render(request,"edit_journals.html")

#-----------------------------------------------------------------------------------------------------------

def get_notification_details(request, notification_id):
    try:
        notification = notification_table.objects.get(notification_id=notification_id)
        data = {
            'notification': notification.notification,
            'link': notification.link
            # Add other fields as needed
        }
        return JsonResponse(data)
    except notification_table.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)
    
#-------------------------------------------------------------------------------------------------------------

def get_editor_details(request, editor_id):
    editor = get_object_or_404(eb_table, pk=editor_id)
    editor_details = {
        'editor_name':editor.editor_name,
        'editor_address': editor.editor_address,
        'editor_email': editor.editor_email,
        'editor_mobile': editor.editor_mobile,
        'photo': editor.photo.url if editor.photo else ''  # Assuming photo is a FileField or ImageField
    }
    return JsonResponse(editor_details)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def editor_review(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        
        # Fetch the editor object
        editor = ea_table.objects.get(employee_id=empid)
        
        # Fetch journals assigned to the editor
        journals = journal_table.objects.filter(editor=editor)
        
        # Fetch articles with status 'accepted' from those journals
        articles = article_table.objects.filter(issue_id__volume_id__journal_id__in=journals, status='accepted')

        if request.method == "POST":
            article_id = request.POST.get('article_id')
            review_text = request.POST.get('review')
            if article_id and review_text:
                article = article_table.objects.get(article_id=article_id)
                review = review_table(article_id=article, editor_id=editor, review=review_text, status='active')
                review.save()

                # Fetch author details
                author = article.author_id

                # Send email to the author
                send_mail(
                    'Your Article Review',
                    f'Dear {author.author_name},\n\nYour article "{article.article_title}" has received a review:\n\n"{review_text}"\n\nBest regards,\nEditorial Team',
                    'your-email@example.com',
                    [author.author_email],
                    fail_silently=False,
                )

                # Add success message
                messages.success(request, 'Review submitted successfully and email sent to the author.')

        return render(request, "editor_review.html", {'articles': articles})
        
    return redirect('/login/')


    
def editor_submitarticle(request):
    if request.session.has_key('empid'):
        ea_email = request.session['empid']
        departments = dept_table.objects.all()
        return render(request, "editor_submitarticle.html", {"ea_email": ea_email, "departments": departments})
    else:
        return redirect('/p_index/#cta') 

def earticle_submission(request):
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
            empid = request.session.get('empid')
            editor = get_object_or_404(ea_table, employee_id=empid)
            author = get_object_or_404(author_table, author_id=100)

            # Save article details
            article = article_table(
                issue_id=get_object_or_404(issue_table, pk=issue_id),
                ea_id=editor,
                article_title=article_title,
                created_by=editor.ea_name,
                status='approved',
                author_id = author,
                author1=authors[0] if author_count >= 1 else '',
                author2=authors[1] if author_count >= 2 else '',
                author3=authors[2] if author_count >= 3 else '',
                article_file=article_file  # Save the uploaded file
            )
            article.save()
            messages.success(request,'succesfully uploaded')
            return redirect('/editor_submitarticle/')  # Redirect to a success page

        return redirect('submit_article')  # Redirect back to the form if not a POST request
    else:
        return redirect('/p_index/#cta')  