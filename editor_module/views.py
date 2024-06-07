import os, logging, json
from venv import logger
from PyPDF2 import PdfMerger
from django.views.decorators.csrf import csrf_exempt
from weasyprint import HTML, html
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import FileResponse, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from django.db import transaction
from django.db.models import Count
from django.views.decorators.http import require_POST
from admin_module.models import ArticleDownload, ArticleVisit, JournalPageVisit, article_table, ea_table, dept_table, gl_table, journal_table, notification_table, review_table, volume_table, issue_table, eb_table
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
     
def edit_journals(request, journal_id):
    if 'empid' in request.session:
        empid = request.session['empid']
        jdata = get_object_or_404(journal_table, journal_id=journal_id)
                
        return render(request, "edit_journals.html", {
            "empid": empid,
            "journal_id": journal_id,
        })
    else:
        return redirect('/login/')    
#_____________________________________________________________________________________________________________________________________________
    
def manage_volume(request, journal_id):
    if 'empid' in request.session:
        empid = request.session['empid']
        journal = get_object_or_404(journal_table, journal_id=journal_id)
        # Here you can retrieve all volumes related to the journal
        volumes = journal.volume_table_set.all()
        return render(request, "manage_volume.html", {
            "empid": empid,
            "journal_id": journal_id,
            "volumes": volumes,
        })
    else:
        return redirect('/login/')
    
def update_volume_name(request):
    if request.method == 'POST' and request.is_ajax():
        volume_id = request.POST.get('volume_id')
        new_volume_name = request.POST.get('volume_name')
        volume = get_object_or_404(volume_table, volume_id=volume_id)
        volume.volume = new_volume_name
        volume.save()
        return JsonResponse({'message': 'Volume name updated successfully'})
    return JsonResponse({'error': 'Invalid request'})


def remove_volume(request):
    if request.method == 'POST' and request.is_ajax():
        volume_id = request.POST.get('volume_id')
        try:
            with transaction.atomic():
                volume = get_object_or_404(volume_table, volume_id=volume_id)
                
                # Set the volume to inactive
                volume.status = 'inactive'
                volume.save()

                # Set all related issues to inactive
                issues = issue_table.objects.filter(volume_id=volume_id)
                for issue in issues:
                    issue.status = 'inactive'
                    issue.save()

                # Set all related articles to inactive
                articles = article_table.objects.filter(issue_id__volume_id=volume_id)
                for article in articles:
                    article.status = 'inactive'
                    article.save()

            return JsonResponse({'message': 'Volume and related items set to inactive successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    return JsonResponse({'error': 'Invalid request'})   


#_____________________________________________________________________________________________________________________________________________


def manage_isssues(request, journal_id):
    if 'empid' in request.session:
        empid = request.session['empid']
        jdata = get_object_or_404(journal_table, journal_id=journal_id)
                
        return render(request, "manage_volume.html", {
            "empid": empid,
            "journal_id": journal_id,
        })
    else:
        return redirect('/login/') 
#_____________________________________________________________________________________________________________________________________________    

def manage_aim(request, journal_id):
    if 'empid' in request.session:
        empid = request.session['empid']
        journal = get_object_or_404(journal_table, journal_id=journal_id)
        success_message = ""
        error_message = ""

        if request.method == "POST":
            action = request.POST.get('action')
            if action == 'remove':
                journal.journal_aim = ''
                journal.save()
                success_message = "Aim has been successfully removed."
            elif action == 'save':
                new_aim = request.POST.get('journal_aim')
                if new_aim:
                    journal.journal_aim = new_aim
                    journal.save()
                    success_message = "Aim has been successfully updated."
                else:
                    error_message = "Aim cannot be empty when saving."

        return render(request, "manage_aim.html", {
            "empid": empid,
            "journal_id": journal_id,
            "journal_aim": journal.journal_aim,
            "success_message": success_message,
            "error_message": error_message,
        })
    else:
        return redirect('/login/')

    
#_____________________________________________________________________________________________________________________________________________   

@csrf_exempt
def update_row(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        row_id = data.get('id')
        heading = data.get('heading')
        content = data.get('content')

        try:
            guideline = get_object_or_404(gl_table, gl_id=row_id)
            guideline.heading = heading
            guideline.content = content
            guideline.save()
            return JsonResponse({'success': True})
        except gl_table.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Row does not exist'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def remove_row(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        row_id = data.get('id')

        try:
            guideline = get_object_or_404(gl_table, gl_id=row_id)
            guideline.status = 'inactive'
            guideline.save()
            return JsonResponse({'success': True})
        except gl_table.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Row does not exist'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

def manage_gl(request, journal_id):
    if 'empid' in request.session:
        empid = request.session['empid']
        journal = get_object_or_404(journal_table, journal_id=journal_id)
        guidelines = gl_table.objects.filter(journal_id=journal_id, status='active')
        return render(request, 'manage_gl.html', {'guidelines': guidelines})
    else:
        return redirect('/login/')    

#_____________________________________________________________________________________________________________________________________________    

def manage_ethics(request, journal_id):
    if 'empid' in request.session:
        empid = request.session['empid']
        journal = get_object_or_404(journal_table, journal_id=journal_id)
        success_message = ""
        error_message = ""

        if request.method == "POST":
            action = request.POST.get('action')
            if action == 'remove':
                journal.journal_ethics = ''
                journal.save()
                success_message = "Ethics have been successfully removed."
            elif action == 'save':
                new_ethics = request.POST.get('journal_ethics')
                if new_ethics:
                    journal.journal_ethics = new_ethics
                    journal.save()
                    success_message = "Ethics have been successfully updated."
                else:
                    error_message = "Ethics cannot be empty when saving."

        return render(request, "manage_ethics.html", {
            "empid": empid,
            "journal_id": journal_id,
            "journal_ethics": journal.journal_ethics,
            "success_message": success_message,
            "error_message": error_message,
        })
    else:
        return redirect('/login/')
#_____________________________________________________________________________________________________________________________________________    
@csrf_exempt
def update_eb_member(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        photo = request.FILES.get('photo')

        try:
            member = get_object_or_404(eb_table, board_id=id)
            member.editor_name = name
            member.editor_email = email
            member.editor_mobile = mobile
            member.editor_address = address
            if photo:
                member.photo = photo
            member.save()
            return JsonResponse({'success': True})
        except eb_table.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Member does not exist'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def remove_eb_member(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')

        try:
            member = get_object_or_404(eb_table, board_id=id)
            member.status = 'inactive'
            member.save()
            return JsonResponse({'success': True})
        except eb_table.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Member does not exist'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

def manage_eb(request, journal_id):
    if 'empid' in request.session:
        empid = request.session['empid']
        journal = get_object_or_404(journal_table, journal_id=journal_id)
        members = eb_table.objects.filter(journal_id=journal_id, status='active')
        return render(request, "manage_eb.html", {
            "empid": empid,
            "journal_id": journal_id,
            "members": members
        })
    else:
        return redirect('/login/')
#_____________________________________________________________________________________________________________________________________________   

def manage_contact(request, journal_id):
    if 'empid' in request.session:
        empid = request.session['empid']
        jdata = get_object_or_404(journal_table, journal_id=journal_id)
        contacts = journal_table.objects.filter(journal_id=journal_id)
        return render(request, "manage_contact.html", {
            "empid": empid,
            "journal_id": journal_id,
            "contacts": contacts
        })
    else:
        return redirect('/login/')
    
def update_contact(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        name = data.get('name')
        mobile = data.get('mobile')
        email = data.get('email')

        try:
            journal = get_object_or_404(journal_table, journal_id=id)
            journal.phone = mobile
            journal.email = email
            journal.save()
            return JsonResponse({'success': True})
        except journal_table.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Journal does not exist'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

def remove_contact(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')

        try:
            journal = get_object_or_404(journal_table, journal_id=id)
            journal.delete()
            return JsonResponse({'success': True})
        except journal_table.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Journal does not exist'})

    return JsonResponse({'success': False, 'error': 'Invalid request'}) 

   
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


    
