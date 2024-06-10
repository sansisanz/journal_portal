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
from django.core.files.storage import FileSystemStorage
from admin_module.models import ArticleDownload, ArticleVisit, JournalPageVisit, article_table, author_table, ea_table, dept_table, gl_table, journal_table, notification_table, review_table, volume_table, issue_table, eb_table


# Create your views here.

#----------------------  HOME & SIDEBAR  -----------------------------------------------------------------------------------------------------------------------------------------

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
    

def editor_index(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "editorindex.html")
        
    return redirect('/login')

#-------------------    ASSIGNED JOURNALS    ------------------------------------------------------------------------------------------------------------------------------------

def assigned_journal(request):
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

    journal = journal_table.objects.get(pk=journal_id)
    current_open_volume = volume_table.objects.filter(journal_id=journal, status='open').first()
    current_open_issue = None
    if current_open_volume:
        current_open_issue = issue_table.objects.filter(volume_id=current_open_volume, status='open').first()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'add_vol':
            # Retrieve form data for adding volume
            volume_name = request.POST.get('volume')

            # Check if volume with the same name already exists
            existing_volume = volume_table.objects.filter(journal_id=journal, volume=volume_name).first()
            if existing_volume:
                if existing_volume.status == 'open':
                    messages.warning(request, 'Volume with the same name already exists.', extra_tags='add_vol_alert')
                    return render(request, 'add_vic.html', {
                        'journal_id': journal_id,
                        'volumes': volume_table.objects.filter(journal_id=journal_id),
                        'current_open_volume': current_open_volume,
                        'current_open_issue': current_open_issue,
                    })
                else:
                    # Update the existing volume to open status and close others
                    volume_table.objects.filter(journal_id=journal).update(status='closed')
                    issue_table.objects.filter(volume_id=existing_volume).update(status='closed')
                    existing_volume.status = 'open'
                    existing_volume.save()
                    messages.success(request, 'Volume added successfully.', extra_tags='add_vol_success')
                    return redirect('/add_vic/{}/'.format(journal_id))

            # Close all previous volumes and their issues
            for volume in volume_table.objects.filter(journal_id=journal):
                volume.status = 'closed'
                volume.save()
                issue_table.objects.filter(volume_id=volume).update(status='closed')

            # Create a new volume entry for the journal
            new_volume = volume_table.objects.create(
                journal_id=journal,
                volume=volume_name,
                created_by=user_name,
                status='open'
            )

            messages.success(request, 'Volume added successfully.', extra_tags='add_vol_success')
            return redirect('/add_vic/{}/'.format(journal_id))   # Change this to your success URL

        elif form_type == 'add_issue':
            # Retrieve form data for adding issue
            issue_number = int(request.POST.get('issue_number'))
            cover_image = request.FILES.get('cover_image')

            # Ensure the issue is being added to the currently open volume
            if not current_open_volume:
                messages.warning(request, 'No open volume to add the issue.', extra_tags='add_issue_alert')
                return render(request, 'add_vic.html', {
                    'journal_id': journal_id,
                    'volumes': volume_table.objects.filter(journal_id=journal_id),
                    'current_open_volume': current_open_volume,
                    'current_open_issue': current_open_issue,
                })

            volume_id = current_open_volume.volume_id

            # Check if the issue already exists
            existing_issue = issue_table.objects.filter(volume_id=volume_id, issue_no=str(issue_number)).first()
            if existing_issue:
                if existing_issue.status == 'open':
                    messages.warning(request, 'Issue already exists.', extra_tags='add_issue_alert')
                    return render(request, 'add_vic.html', {
                        'journal_id': journal_id,
                        'volumes': volume_table.objects.filter(journal_id=journal_id),
                        'current_open_volume': current_open_volume,
                        'current_open_issue': current_open_issue,
                    })
                else:
                    # Update the existing issue to open status and close others
                    issue_table.objects.filter(volume_id=volume_id).update(status='closed')
                    existing_issue.status = 'open'
                    existing_issue.save()
                    messages.success(request, 'Issue added successfully.', extra_tags='add_issue_success')
                    return redirect('/add_vic/{}/'.format(journal_id))

            # Close all previous issues of the current volume
            issue_table.objects.filter(volume_id=volume_id).update(status='closed')

            # Create a new issue for the selected volume
            new_issue = issue_table.objects.create(
                volume_id=volume_table.objects.get(pk=volume_id),
                issue_no=str(issue_number),
                cover_image=cover_image,
                created_by=user_name,
                status='open'
            )

            messages.success(request, 'Issue added successfully.', extra_tags='add_issue_success')
            return redirect('/add_vic/{}/'.format(journal_id))  # Change this to your success URL

    # On GET request, render the form with volume options
    return render(request, 'add_vic.html', {
        'journal_id': journal_id,
        'volumes': volume_table.objects.filter(journal_id=journal_id),
        'current_open_volume': current_open_volume,
        'current_open_issue': current_open_issue,
    })


#-------------------    ADD DETAILS    ------------------------------------------------------------------------------------------------------------------------------------

def add_details(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        journals = journal_table.objects.filter(editor__employee_id=empid, status='active')
        return render(request, "add_details.html", {"empid": empid, "journals": journals})
    else:
        return redirect('/login')

def journal_details(request):
    if request.session.has_key('empid'):
        if request.method == 'POST':
            empid = request.session['empid']
            journal_id = request.POST.get('journalname')
            options = request.POST.getlist('options')

            journal = journal_table.objects.get(journal_id=journal_id)

            if 'aimsScope' in options:
                aims_scope = request.POST.get('aimsScope', '').strip()
                if aims_scope:
                    journal.journal_aim = aims_scope

            if 'ethics' in options:
                ethics = request.POST.get('ethics', '').strip()
                if ethics:
                    journal.journal_ethics = ethics

            journal.save()

            if 'guidelines' in options:
                total_contents = int(request.POST.get('totalContents', 0))
                for i in range(1, total_contents + 1):
                    heading = request.POST.get(f'heading_{i}', '').strip()
                    content = request.POST.get(f'content_{i}', '').strip()
                    if heading and content:
                        guideline = gl_table(journal_id=journal, heading=heading, content=content)
                        guideline.save()

            success_message = "Journal details have been successfully updated."
            journals = journal_table.objects.filter(editor__employee_id=empid, status='active')
            return render(request, "add_details.html", {
                "empid": empid,
                "journals": journals,
                "success_message": success_message,
                "selected_journal_id": journal_id,
                "aims_scope": journal.journal_aim,
                "ethics": journal.journal_ethics
            })
    else:
        return redirect('/login')
    
#----------------------------    ADD EB     ---------------------------------------------------------------------------------------------------------------------------------

def editorialboard(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        # Fetch journals assigned to the logged-in user
        journals = journal_table.objects.filter(editor__employee_id=empid, status='active')
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
     
#------------------------------------------------------------------------------------------------------------------------------------


def editor_article(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "article.html", {"empid": empid})
    else:
        return redirect('/login/')
    

def editor_forgotpassword(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "forgot-password.html", {"empid": empid})
    else:
        return redirect('/login/')
    
#---------------------------------ADD NOTIFICATIONS-------------------------------------------------------------------------

def notifications(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        # Fetch journals assigned to the logged-in user
        journals = journal_table.objects.filter(editor__employee_id=empid, status='active')
        return render(request, "notifications.html", {"empid": empid, "journals": journals})
    else:
        return redirect('/login')
    
def notify(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        if request.method == 'POST':
            journal_id = request.POST.get('journalname')
            notification = request.POST.get('volume')
            input_type = request.POST.get('input_type')

            link = ''
            if input_type == 'url':
                link = request.POST.get('next_volume_url')
            elif input_type == 'file' and 'next_volume_file' in request.FILES:
                next_volume_file = request.FILES['next_volume_file']
                fs = FileSystemStorage()
                filename = fs.save(next_volume_file.name, next_volume_file)
                link = fs.url(filename)

            editor = ea_table.objects.get(employee_id=empid)
            journal = journal_table.objects.get(journal_id=journal_id)

            new_notification = notification_table(
                journal_id=journal,
                notification=notification,
                link=link,
                created_by=editor.ea_name,
                status='active'
            )
            new_notification.save()

            messages.success(request, 'Notification added successfully!')
            return redirect('/notify/')
        else:
            editor = ea_table.objects.get(employee_id=empid)
            journals = journal_table.objects.filter(editor=editor, status='active')
            return render(request, "notifications.html", {"journals": journals})
    else:
        return redirect('/login/')

#----------------------------------- add contact ---------------------------------------------------------------------- 

def editor_contact(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        # Fetch journals assigned to the logged-in user
        journals = journal_table.objects.filter(editor__employee_id=empid)
        departments = dept_table.objects.all()
        return render(request, "editor_contact.html", {"empid": empid, "journals": journals, 'departments':departments})
    else:
        return redirect('/login/')
    
def add_contact(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        user_name = request.session['editor_name']

        if request.method == 'POST':
            journals = request.POST.get('journal_id')
            editor_email = request.POST.get('email_address')
            editor_mobile = request.POST.get('phone_number')
            created_by = user_name  # You need to set the creator value

            # Fetch the journal object
            journal = journal_table.objects.get(journal_id=journals, status='active')

            # Check if email and phone number already exist for the journal
            existing_email = journal.email
            existing_phone = journal.phone

            # Update the email and phone number only if they are not already present
            if not existing_email:
                journal.email = editor_email
            if not existing_phone:
                journal.phone = editor_mobile

            # Save the changes
            journal.save()

            # Redirect to the same page with a success message
            return redirect('/editor_contact/', {'success_message': 'Contact info added successfully'})

        else:
            return render(request, 'editorindex.html')

    else:
        return redirect('/login/')
    
#---------------------------   JOURNAL LIST    ------------------------------------------------------------------------------------ 

def upddetails(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        
        # Fetch journals assigned to the logged-in user
        journals = journal_table.objects.filter(editor__employee_id=empid, status='active')

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

#______________________    MAnAGE VOLUMES      __________________________________________________________
  
from django.db.models import Count

def manage_volume(request, journal_id):
    if 'empid' in request.session:
        empid = request.session['empid']
        journal = get_object_or_404(journal_table, journal_id=journal_id)
        
        # Annotate volumes with the count of distinct issues
        volumes = journal.volume_table_set.annotate(
            num_issues=Count('issue_table', distinct=True),
        ).all()
        
        for volume in volumes:
            # Calculate the total number of articles for each volume
            volume.num_articles = sum(
                issue.article_table_set.count()
                for issue in volume.issue_table_set.all()
            )
        
        return render(request, "manage_volume.html", {
            "empid": empid,
            "journal_id": journal_id,
            "volumes": volumes,
        })
    else:
        return redirect('/login/')

def update_volume_name(request):
    if request.method == 'POST':
        volume_id = request.POST.get('volume_id')
        new_volume_name = request.POST.get('volume_name')
        try:
            volume = volume_table.objects.get(pk=volume_id)
            volume.volume = new_volume_name
            volume.save()
            return JsonResponse({'message': 'Volume name updated successfully'})
        except volume_table.DoesNotExist:
            return JsonResponse({'error': 'Volume not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def remove_volume(request):
    if request.method == 'POST':
        volume_id = request.POST.get('volume_id')
        
        try:
            with transaction.atomic():
                volume = get_object_or_404(volume_table, pk=volume_id)
                
                # Set the volume to inactive
                volume.status = 'inactive'
                volume.save()

                # Set all related issues to inactive
                issue_table.objects.filter(volume_id=volume_id).update(status='inactive')

                # Set all related articles to inactive
                article_table.objects.filter(issue_id__volume_id=volume_id).update(status='inactive')

            return JsonResponse({'message': 'Volume and related items set to inactive successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

#______________________________   MANAGE ISSUES   ________________________________________________________________________________
def manage_issues(request, journal_id):
    if request.method == 'POST':
        # Handle form submission
        volume_id = request.POST.get('volume')
        issue_id = request.POST.get('issue')
        cover_image = request.FILES.get('cover_image')

        # Update issue details
        issue = issue_table.objects.get(pk=issue_id)
        issue.cover_image = cover_image
        issue.save()

        return redirect('manage_issues', journal_id=journal_id)

    else:
        # Fetch volumes and issues for the selected journal
        volumes = volume_table.objects.filter(journal_id=journal_id)
        issues = issue_table.objects.none()  # Initially, no issues
        selected_issue = None

        # Fetch selected issue details if available
        issue_id = request.GET.get('issue')
        if issue_id:
            selected_issue = issue_table.objects.get(pk=issue_id)
            issues = issue_table.objects.filter(volume_id=selected_issue.volume_id)

        return render(request, 'manage_issue.html', {'journal_id': journal_id, 'volumes': volumes, 'issues': issues, 'selected_issue': selected_issue})

def remove_issue(request, journal_id):
    if request.method == 'POST':
        issue_id = request.POST.get('issue')
        issue = issue_table.objects.get(pk=issue_id)
        issue.status = 'inactive'
        issue.save()
        return redirect('manage_issues', journal_id=journal_id)
    else:
        return redirect('manage_issues', journal_id=journal_id)

#___________________________________________________________________________________________________________________

def manage_notification(request, journal_id):
    if 'empid' in request.session:
        empid = request.session['empid']
        journal = get_object_or_404(journal_table, journal_id=journal_id)
        active_notifications = notification_table.objects.filter(journal_id=journal, status='active')
        return render(request, "manage_notification.html", {
            "empid": empid,
            "journal_id": journal_id,
            "active_notifications": active_notifications,
        })
    else:
        return redirect('/login/')

@csrf_exempt
def edit_notification(request):
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        notification = get_object_or_404(notification_table, notification_id=notification_id)
        notification_text = request.POST.get('notification')
        link = request.POST.get('link')

        if notification_text:
            notification.notification = notification_text
        if link:
            notification.link = link
        if 'file' in request.FILES:
            file = request.FILES['file']
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'notifications'))
            filename = fs.save(file.name, file)
            notification.link = fs.url(filename)

        notification.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
def remove_notification(request):
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        notification = get_object_or_404(notification_table, notification_id=notification_id)
        notification.status = 'inactive'
        notification.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
#___________________________________________________________________________________________________________________

def manage_article(request, journal_id):
    if 'empid' in request.session:
        empid = request.session['empid']
        journals = journal_table.objects.filter(editor__employee_id=empid, status='active')
        
        # Fetch articles related to the specified journal
        articles = article_table.objects.filter(issue_id__volume_id__journal_id=journal_id, status='approved')
        
        return render(request, "manage_article.html", {
            "empid": empid,
            "journals": journals,
            "articles": articles,
        })
    else:
        return redirect('/login/')


#___________________________________________________________________________________________________________________

#--------------------------------------------------------------------------------------------------------------- 
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
    

    
#---------------------------------------------------------------------------------------------------------------    


    
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


 
#---------------------------------------------------------------------------------------------------------------

def e_visits(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        editor = ea_table.objects.get(employee_id=empid)
        journals = journal_table.objects.filter(editor=editor)
        return render(request, "e_visits.html", {"empid": empid, "journals": journals})
    else:
        return redirect('/login')

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
    articles = article_table.objects.filter(issue_id=issue_id).values('article_id', 'article_title')
    return JsonResponse(list(articles), safe=False)

def get_journal_visit_count(request):
    journal_id = request.GET.get('journal_id')
    print(f"Received journal_id: {journal_id}")  # Debug statement
    visit_count = JournalPageVisit.objects.filter(journal_id=journal_id).count()
    print(f"Visit count for journal_id {journal_id}: {visit_count}")  # Debug statement
    return JsonResponse({'visit_count': visit_count})

def get_article_visit_count(request):
    article_id = request.GET.get('article_id')
    print(f"Received article_id: {article_id}")  # Debug statement
    visit_count = ArticleVisit.objects.filter(article_id=article_id).count()
    print(f"Visit count for article_id {article_id}: {visit_count}")  # Debug statement
    return JsonResponse({'visit_count': visit_count})

def get_article_download_count(request):
    article_id = request.GET.get('article_id')
    print(f"Received article_id: {article_id}")  # Debug statement
    download_count = ArticleDownload.objects.filter(article_id=article_id).count()
    print(f"Download count for article_id {article_id}: {download_count}")  # Debug statement
    return JsonResponse({'download_count': download_count})


#---------------------------------------------------------------------------------------------------------------


    
#-----------------------------------------------------------------------------------------------------

 
#_____________________________________________________________________________________________________________________________________________
    
 


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
            # Set email and phone to empty strings
            journal.email = ''
            journal.phone = ''
            journal.save()  # Save changes
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


    
def editor_submitarticle(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        departments = dept_table.objects.all()
        return render(request, "editor_submitarticle.html", {"empid": empid, "departments": departments})
    else:
        return redirect('/editor_index/') 

def earticle_submission(request):
    if request.session.has_key('empid'):
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

            # Save article details
            article = article_table(
                issue_id=get_object_or_404(issue_table, pk=issue_id),
                ea_id=editor,
                article_title=article_title,
                created_by=editor.ea_name,
                status='approved',
                editor_id = editor,
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
        return redirect('/editor_index/')  
    
    #-------------------------------------------------------------------------------------------------
