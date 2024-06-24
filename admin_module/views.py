import logging
from django.contrib import messages
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import hashlib
from admin_module.models import author_table, ArticleDownload, ArticleVisit, JournalPageVisit, article_table, ea_table, eb_table, gl_table, issue_table, message_table, notification_table, review_table, role_table, seat_table, designation_table, usertable, dept_table, journal_table, volume_table
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.hashers import make_password
import secrets
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.db import transaction

# Create your views here.


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def login(request):
    return render(request, 'login.html')


def ea_login(request):
  if request.method == "POST":

        empid = request.POST.get("loginid")
        password = hashlib.sha1(request.POST.get("loginPassword").encode('utf-8')).hexdigest()

        try:
            
            user = ea_table.objects.get(employee_id=empid, password=password)
            utype=user.ea_type
            if utype == "admin":
                name = user.ea_name
                request.session['empid'] = empid
                request.session['admin_name'] = name
                return redirect("/index/")
            elif utype == "editor":
                name = user.ea_name
                request.session['empid'] = empid
                request.session['editor_name'] = name  
                return redirect("/editor_index/")
            else:
                return render(request,"login.html")
        except Exception:
            ea_table.DoesNotExist
            return render(request,"login.html",{"login_error":"Invalid Employee ID or Password"})


def logout(request):
   try:
      del request.session['empid']
      del request.session['name']
   except:
      pass
   return render(request,"login.html")

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def send_reset_email(user, email):
    token = get_random_string(30)
    user.token = token
    user.token_expiry = timezone.now() + timedelta(hours=1)  # Token is valid for 1 hour
    user.save()
    reset_link = f"http://127.0.0.1:8000/reset_pd/{user.token}/"
    send_mail(
        'Password Reset Request',
        f'Click the link to reset your password: {reset_link}',
        'from@example.com',
        [email],
        fail_silently=False,
    )

def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = author_table.objects.get(author_email=email)
            send_reset_email(user, email)
            messages.success(request, 'We have emailed you instructions for setting your password.')
        except author_table.DoesNotExist:
            try:
                user = ea_table.objects.get(ea_email=email)
                send_reset_email(user, email)
                messages.success(request, 'We have emailed you instructions for setting your password.')
            except ea_table.DoesNotExist:
                messages.error(request, 'Email address not found.')
        return redirect('/forgotpassword/')
    return render(request, 'forgotpassword.html')

def reset_pd(request, token):
    try:
        user = author_table.objects.get(token=token)
    except author_table.DoesNotExist:
        try:
            user = ea_table.objects.get(token=token)
        except ea_table.DoesNotExist:
            messages.error(request, 'This password reset link is invalid or has expired.')
            return redirect('/forgotpassword/')
    
    if user.token_expiry and user.token_expiry < timezone.now():
        messages.error(request, 'This password reset link is invalid or has expired.')
        return redirect('/forgotpassword/')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password == confirm_password:
            user.password = hashlib.sha1(new_password.encode('utf-8')).hexdigest()
            user.token = None
            user.token_expiry = None
            user.save()
            messages.success(request, 'Your password has been set. You can now log in.')
            return redirect('/login/')  # Adjust to your login URL name if different
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect(f'/reset_pd/{token}/')
    
    return render(request, 'reset_password.html', {'token': token})

#-----------------------------------------------------------------------------------------------------------------------------------------------
def index(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "index.html", {"empid": empid})
    else:
        return redirect('/login/')
    

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#ADD EDITOR 

def add_editor(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        
        # Fetch departments and roles from the database
        departments = dept_table.objects.all()
        roles = role_table.objects.all()

        return render(request, "add_editor.html", {"empid": empid, "departments": departments, "roles": roles})
    else:
        return redirect('/login/')

def addeditor(request):
    if request.method == 'POST':
        # Extract data from the submitted form
        employee_id = request.POST.get('employeeId')
        ea_name = request.POST.get('editorName')
        ea_email = request.POST.get('editorEmail')
        role_name = request.POST.get('roleName')
        designation = request.POST.get('designation')
        department_name = request.POST.get('department')

        # Generate a unique string token
        token = secrets.token_urlsafe(16)  # Adjust the length as needed

        flag = 0
        empidcheck = ''
        emailcheck = ''

        # Check if employee ID already exists
        if ea_table.objects.filter(employee_id=employee_id).exists():
            flag = 1
            empidcheck = 'Employee Id already exists'

        # Check if email already exists
        if ea_table.objects.filter(ea_email=ea_email).exists():
            flag = 1
            emailcheck = 'Email already exists'
        
        if flag == 1:
            # Fetch departments and roles again for rendering the form
            departments = dept_table.objects.all()
            roles = role_table.objects.all()
            return render(request, 'add_editor.html', {
                'empidcheck': empidcheck, 
                'emailcheck': emailcheck,
                'departments': departments,
                'roles': roles,
            })

        if dept_table.objects.filter(dept_name=department_name).exists():
            deptdata = dept_table.objects.get(dept_name=department_name)
        else:
            deptdata = dept_table()
            deptdata.dept_name = department_name
            deptdata.save()

        eadata = ea_table()
        eadata.employee_id = employee_id
        eadata.ea_name = ea_name
        eadata.ea_email = ea_email
        eadata.ea_type = "editor"
        eadata.dept_id = deptdata
        eadata.token = token
        eadata.status = "inactive"
        eadata.save()

        # Save data into role_table
        if role_table.objects.filter(role_name=role_name).exists():
            rdata = role_table.objects.get(role_name=role_name)
        else:
            rdata = role_table()
            rdata.role_name = role_name
            rdata.save()
        
        # Save data to designation_table
        if designation_table.objects.filter(designation=designation).exists():
            desdata = designation_table.objects.get(designation=designation)
        else:
            desdata = designation_table()
            desdata.designation = designation
            desdata.save()
        
        # Save data to seat_table
        if seat_table.objects.filter(seat_name=role_name).exists():
            sdata = seat_table.objects.get(seat_name=role_name)
        else:
            sdata = seat_table()
            sdata.seat_name = role_name
            sdata.save()
    
        # Save data to usertable
        udata = usertable()
        udata.ea_id = eadata
        udata.seat_id = sdata
        udata.save()

        # Send email to the entered email address
        subject = 'Set Your Password'
        message = 'Click the link to set your password: http://127.0.0.1:8000/set_password/?user='+token
        html_message = render_to_string('email_template.html', {'message': message})
        plain_message = strip_tags(html_message)
        sender_email = 'subindax@gmail.com'
        send_mail(subject, plain_message, sender_email, [ea_email], html_message=html_message)
        
        messages.success(request, 'Added editor successfully. Now set your password using the mail we sent to you.')
        return redirect('/add_editor/')
    
    # Fetch departments and roles again for rendering the form
    departments = dept_table.objects.all()
    roles = role_table.objects.all()
    return render(request, 'add_editor.html', {'departments': departments, 'roles': roles})

#SET PASSWORD TO NEWLY ADDED EDITOR
def set_password(request):
    user = request.GET.get('user')
    request.session['token']=user
    return render(request, 'set_password.html')

def setpassword(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        token = request.session['token']

        if not password or not confirm_password:
            return HttpResponse("Password cannot be empty")

        if password != confirm_password:
            return HttpResponse("Passwords do not match")

        if len(password) < 8:
            return HttpResponse("Password should be at least 8 characters long")

        # Find the user by token
        user = ea_table.objects.get(token=token)

        # Hash the password
        hashed_password = hashlib.sha1(password.encode('utf-8')).hexdigest()

        # Set the hashed password for the user
        user.password = hashed_password
        user.status = "active"
        user.save()

        return redirect('/login/')  # Redirect to login page after setting password

    return HttpResponse("Invalid Request")

def remove_editor(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        departments = dept_table.objects.all()
        
        if request.method == 'POST':
            dept_id = request.POST.get('dept_id')
            editor_id = request.POST.get('editor_id')
            
            if dept_id and editor_id:
                # Remove editor from the journals in the specified department
                journals = journal_table.objects.filter(dept_id=dept_id, editor_id=editor_id)
                for journal in journals:
                    journal.editor_id = None
                    journal.save()

                # Remove editor from articles
                articles = article_table.objects.filter(ea_id=editor_id)
                for article in articles:
                    article.ea_id = None
                    article.save()

                # Remove editor from messages
                messages_table = message_table.objects.filter(ea_id=editor_id)
                for msg in messages_table:
                    msg.ea_id = None
                    msg.save()

                # Remove editor from reviews
                reviews = review_table.objects.filter(editor_id=editor_id)
                for review in reviews:
                    review.editor_id = None
                    review.save()

                # Set status to inactive in ea_table
                ea_table.objects.filter(ea_id=editor_id).update(status='inactive')
                
                # Set status to inactive in usertable
                usertable.objects.filter(ea_id=editor_id).update(status='inactive')

                messages.success(request, 'Editor has been successfully removed from all assigned journals and tables.')
                return redirect('/remove_editor/')
        
        return render(request, "remove_editor.html", {"empid": empid, "departments": departments})
    else:
        return redirect('/login/')

def get_editors_by_department(request, dept_id):
    try:
        editors = ea_table.objects.filter(dept_id=dept_id).values('ea_id', 'ea_name')
        return JsonResponse({'editors': list(editors)})
    except Exception as e:
        print(f"Error fetching editors for department {dept_id}: {e}")
        return JsonResponse({'error': 'Error fetching editors'}, status=500)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def create_j(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        departments = dept_table.objects.all()
        editors = ea_table.objects.filter(ea_type='editor')        
        return render(request, "create_j.html", {"empid": empid, 'departments': departments, 'editors': editors})
    else:
        return redirect('/login/')
    

def create_journal(request):
    if request.method == 'POST':
        journal_name = request.POST.get('journalName')
        department_id = request.POST.get('journalDepartment')
        editor_id = request.POST.get('editorId')
        issn_number = request.POST.get('issnNumber')
        ugc_care_list_number = request.POST.get('ugcCareNumber')
        national_registration_number = request.POST.get('registrationNumber')

        if journal_name and department_id and editor_id and issn_number and ugc_care_list_number and national_registration_number:
            # Ensure all required fields are provided
            if len(issn_number) < 8 or len(ugc_care_list_number) < 8 or len(national_registration_number) < 8:
                messages.error(request, 'ISSN, UGC CARE, and Registration numbers must be at least 8 characters long.')
            else:
                try:
                    department = dept_table.objects.get(dept_id=department_id)
                    editor = ea_table.objects.get(ea_id=editor_id)
                    created_by = "admin"

                    new_journal = journal_table.objects.create(
                        journal_name=journal_name,
                        dept_id=department,
                        editor=editor,
                        created_by=created_by,
                        status='active',
                        issn_number=issn_number,
                        ugc_care_list_number=ugc_care_list_number,
                        national_registration_number=national_registration_number
                    )

                    messages.success(request, 'Journal created successfully.')
                    return redirect('/create_j/')
                except dept_table.DoesNotExist:
                    messages.error(request, 'Department does not exist.')
                except ea_table.DoesNotExist:
                    messages.error(request, 'Editor does not exist.')
                except Exception as e:
                    messages.error(request, f'Error creating journal: {str(e)}')

        else:
            messages.error(request, 'All fields are required.')

    # Fetch departments and editors regardless of POST or GET request
    departments = dept_table.objects.all()
    editors = ea_table.objects.filter(ea_type='editor', status='active')

    return render(request, "create_j.html", {"departments": departments, "editors": editors})
    
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------    
def view_j(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        journals = journal_table.objects.filter(status='active')
        csrf_token = request.COOKIES['csrftoken']  # Fetch the CSRF token
        return render(request, "view_j.html", {"empid": empid, "journals": journals, "csrf_token": csrf_token})
    else:
        return redirect('/login/')


def edit_j(request, journal_id):
    empid = request.session.get('empid')
    if empid is None:
        return redirect(f'/login/?next=/edit_j/{journal_id}/')
    
    journal = get_object_or_404(journal_table, journal_id=journal_id)
    departments = dept_table.objects.all()
    editors = ea_table.objects.all()
    
    # Get all messages for the request
    message_list = messages.get_messages(request)
    
    return render(request, 'edit_j.html', {
        'journal': journal, 
        'departments': departments, 
        'editors': editors, 
        'empid': empid,
        'message_list': message_list
    })

def update_journal(request, journal_id):
    if request.method == 'POST':
        empid = request.session.get('empid')
        if empid is None:
            return HttpResponse("Unauthorized", status=401)

        journal = get_object_or_404(journal_table, journal_id=journal_id)
        journal_name = request.POST.get('journal_name')
        dept_id = request.POST.get('dept_id')
        editor_id = request.POST.get('editor_id')

        # Update the journal object with the new values
        journal.journal_name = journal_name
        journal.dept_id_id = dept_id
        journal.editor_id = editor_id

        # Save the changes to the database
        journal.save()

        messages.success(request, 'Journal updated successfully.')
        return redirect('/view_j/')

    else:
        return HttpResponse("Invalid method", status=405)  

def confirm_delete_journal(request, journal_id):
    try:
        journal = get_object_or_404(journal_table, journal_id=journal_id)

        volumes_count = volume_table.objects.filter(journal_id=journal, status='active').count()
        issues_count = issue_table.objects.filter(volume_id__journal_id=journal, status='active').count()
        articles_count = article_table.objects.filter(issue_id__volume_id__journal_id=journal, status='active').count()
        eb_entries_count = eb_table.objects.filter(journal_id=journal, status='active').count()
        guidelines_count = gl_table.objects.filter(journal_id=journal, status='active').count()
        notifications_count = notification_table.objects.filter(journal_id=journal, status='active').count()

        response_data = {
            'volumes_count': volumes_count,
            'issues_count': issues_count,
            'articles_count': articles_count,
            'eb_entries_count': eb_entries_count,
            'guidelines_count': guidelines_count,
            'notifications_count': notifications_count,
        }
        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def remove_journal(request, journal_id):
    if request.method == 'POST':
        try:
            journal = get_object_or_404(journal_table, journal_id=journal_id)
            journal.status = 'inactive'
            journal.save()
            
            volume_table.objects.filter(journal_id=journal).update(status='inactive')
            issue_table.objects.filter(volume_id__journal_id=journal).update(status='inactive')
            article_table.objects.filter(issue_id__volume_id__journal_id=journal).update(status='inactive')
            eb_table.objects.filter(journal_id=journal).update(status='inactive')
            gl_table.objects.filter(journal_id=journal).update(status='inactive')
            notification_table.objects.filter(journal_id=journal).update(status='inactive')
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------    

def visit_c(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        departments = dept_table.objects.all()
        return render(request, "visit_c.html", {"empid": empid, 'departments': departments})
    else:
        return redirect('/login/')  


logger = logging.getLogger(__name__)

def get_journals_by_dept(request):
    dept_id = request.GET.get('dept_id')
    if not dept_id:
        return JsonResponse({'error': 'Department ID not provided'}, status=400)
    
    try:
        dept_id = int(dept_id)
        journals = journal_table.objects.filter(dept_id=dept_id)
        journal_list = list(journals.values('journal_id', 'journal_name', 'visit_count'))
        return JsonResponse(journal_list, safe=False)
    except ValueError:
        return JsonResponse({'error': 'Invalid Department ID'}, status=400)
    except Exception as e:
        logger.error(f"Error fetching journals for department ID {dept_id}: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
def get_journals_by_department(request):
    dept_id = request.GET.get('dept_id')
    journals = journal_table.objects.filter(dept_id=dept_id).values('journal_id', 'journal_name')
    return JsonResponse(list(journals), safe=False)

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
    articles = article_table.objects.filter(issue_id=issue_id).values('article_id', 'article_title', 'visit_count', 'download_count')
    return JsonResponse(list(articles), safe=False)
        
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def adminprofile(request):
    if request.session.has_key('empid'):
            empid = request.session.get('empid')
            user = get_object_or_404(ea_table, employee_id=empid)
            return render(request, 'adminprofile.html', {'user': user})
    else:
        return redirect('/login/')
    
def update_profile(request):
    if request.method == 'POST':
        empid = request.session.get('empid')
        user = get_object_or_404(ea_table, employee_id=empid)
        
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        
        user.ea_mobile = mobile if mobile != "No mobile number provided" else ''
        user.ea_address = address if address != "No address provided" else ''
        
        user.save()
        messages.success(request, 'Profile updated successfully.')
        
        if user.ea_type == 'admin':
            return redirect('/adminprofile/')
        elif user.ea_type == 'editor':
            return redirect('/editorprofile/')
        else:
            return HttpResponse("Invalid user type", status=400)
    else:
        return HttpResponse("Invalid method", status=405)    
   

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------    

def adminresetpassword(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']        
        user = get_object_or_404(ea_table, employee_id=empid)
        return render(request, "adminresetpassword.html", {"user": user})

    else:
        return redirect('/login/')
 
def reset_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('currentPassword')
        new_password = request.POST.get('newPassword')
        repeat_password = request.POST.get('repeatPassword')

        if not request.session.has_key('empid'):
            return redirect('/login/')

        empid = request.session['empid']
        try:
            user = ea_table.objects.get(employee_id=empid)
            hashed_current_password = hashlib.sha1(current_password.encode('utf-8')).hexdigest()
            

            if user.password != hashed_current_password:
                messages.error(request, "Current password is incorrect.")
                return redirect(f'/{user.ea_type}resetpassword/')
            
            if len(new_password) < 8:
                messages.error(request, "New password must be at least 8 characters long.")
                return redirect(f'/{user.ea_type}resetpassword/')

            if new_password != repeat_password:
                messages.error(request, "New password and repeated password do not match.")
                return redirect(f'/{user.ea_type}resetpassword/')

            user.password = hashlib.sha1(new_password.encode('utf-8')).hexdigest()
            user.save()

            messages.success(request, "Password reset successfully.")
            return redirect(f'/{user.ea_type}resetpassword/')
        except ea_table.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect(f'/{user.ea_type}resetpassword/')
        
    user = ea_table.objects.get(employee_id=empid)
    utype=user.ea_type
    if utype == "admin":
        return redirect('/adminresetpassword/')
    return redirect('/editorresetpassword/')
 

#-----------------------------------  MANAGE   -----------------------------------------------------------------------------------------------------------------------------    
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


#______________________    MANAGE VOLUMES      __________________________________________________________

def manage_volume(request, journal_id):
    if 'empid' in request.session:
        empid = request.session['empid']
        journal = get_object_or_404(journal_table, journal_id=journal_id)

        # Filter volumes based on status
        volumes = volume_table.objects.filter(
            journal_id=journal_id,
            status__in=['active', 'open', 'closed']
        )

        volume_data = []
        for volume in volumes:
            total_issues = issue_table.objects.filter(volume_id=volume.volume_id).exclude(status='inactive').count()
            approved_articles = article_table.objects.filter(issue_id__volume_id=volume.volume_id, status='approved')

            # Get the count and titles of approved articles
            approved_articles_count = approved_articles.count()
            approved_article_titles = [article.article_title for article in approved_articles]
            approved_articles_display = f"{approved_articles_count} ({', '.join(approved_article_titles)})" if approved_articles_count else "0"

            volume_data.append({
                'volume_id': volume.volume_id,
                'volume': volume.volume,
                'total_issues': total_issues,
                'approved_articles_display': approved_articles_display,
            })

        return render(request, "manage_volume.html", {
            "empid": empid,
            "journal_id": journal_id,
            "volumes": volume_data,
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

def remove_issue(request, journal_id):
    if 'empid' in request.session:
        if request.method == 'POST':
            issue_id = request.POST.get('remove_issue_id')
            issue = get_object_or_404(issue_table, pk=issue_id)
            
            if issue.status == 'open':
                # Find the most recent closed issue in the same volume
                previous_issue = issue_table.objects.filter(volume_id=issue.volume_id, status='closed').order_by('-created_at').first()
                if previous_issue:
                    previous_issue.status = 'open'
                    previous_issue.save()
            
            elif issue.status == 'closed':
                # Decrement issue_no for all later issues in the same volume
                issue_table.objects.filter(volume_id=issue.volume_id, issue_no__gt=issue.issue_no).update(issue_no=F('issue_no') - 1)
            
            # Set the current issue to inactive
            issue.status = 'inactive'
            issue.save()
            # Set all approved articles in the current issue to inactive
            article_table.objects.filter(issue_id=issue, status='approved').update(status='inactive')

            messages.success(request, 'Issue and its approved articles were set to inactive successfully.')
        return redirect(f'/manage_issue/{journal_id}/')
    else:
        return redirect('/login/')
    
def manage_issue(request, journal_id):
    if 'empid' in request.session:
        empid = request.session['empid']
        
        # Fetch issues with status other than 'inactive'
        issues = issue_table.objects.filter(volume_id__journal_id=journal_id).exclude(status='inactive').select_related('volume_id')

        # Add volume name, article count, and article titles to each issue
        for issue in issues:
            approved_articles = article_table.objects.filter(issue_id=issue, status='approved')
            issue.total_articles = approved_articles.count()
            issue.article_titles = ', '.join(approved_articles.values_list('article_title', flat=True))
            issue.volume = issue.volume_id.volume

        return render(request, 'manage_issue.html', {
            'journal_id': journal_id,
            'issues': issues,
        })
    else:
        return redirect('/login/')
    
#_______________________________________   MANMAGE AIM AND SCOPES ______________________________________________________________________________________________________    

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
            
#_____________________________________  MANAGE GUIDELINES   ________________________________________________________________________________________________________   

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
        success_message = request.GET.get('success_message', '')
        error_message = request.GET.get('error_message', '')
        return render(request, 'manage_gl.html', {
            'guidelines': guidelines,
            'success_message': success_message,
            'error_message': error_message,
            'journal_id': journal_id,  # Pass journal_id to the template context
        })
    else:
        return redirect('/login/')


#________________________________   MANAGE ETHICS   _____________________________________________________________________________________________________________    

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
#________________________________   MANAGE EDITORIAL BOARD   _____________________________________________________________________________________________________________    

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
            return JsonResponse({'success': True, 'message': 'Member updated successfully'})
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
            return JsonResponse({'success': True, 'message': 'Member removed successfully'})
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
#_________________________    MANAGE CONTACT    ____________________________________________________________________________________________________________________   

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

#______________________   MANAGE NOTIFICATIONS   _____________________________________________________________________________________________

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

#________________________ MANAGE ARTICLES  ___________________________________________________________________________________________

def manage_article(request, journal_id):
    if 'empid' in request.session:
        empid = request.session['empid']
        journals = journal_table.objects.filter(editor__employee_id=empid, status='active')
        articles = article_table.objects.filter(issue_id__volume_id__journal_id=journal_id, status='approved')
        
        return render(request, "manage_article.html", {
            "empid": empid,
            "journals": journals,
            "articles": articles,
        })
    else:
        return redirect('/login/')

def edit_article(request, article_id):
    article = get_object_or_404(article_table, article_id=article_id)
    
    if request.method == 'POST':
        article.article_title = request.POST.get('article_title', article.article_title)
        
        if 'article_file' in request.FILES:
            article.article_file = request.FILES['article_file']
        
        article.save()
        return redirect(f'/manage_article/{article.issue_id.volume_id.journal_id.journal_id}/')

    return render(request, "edit_article.html", {"article": article})

def remove_article(request, article_id):
    if request.method == 'POST':
        article = get_object_or_404(article_table, article_id=article_id)
        article.status = 'inactive'
        article.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})





