from django.contrib import messages
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import hashlib
from admin_module.models import article_download, article_table, article_visit, ea_table, eb_table, gl_table, issue_table, journalpage_visit, notification_table, role_table, seat_table, designation_table, usertable, dept_table, journal_table, volume_table
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.hashers import make_password
import secrets


# Create your views here.

def login(request):
    return render(request, 'login.html')


def index(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "index.html", {"empid": empid})
    else:
        return redirect('/login')

def forgotpassword(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "forgotpassword.html", {"empid": empid})
    else:
        return redirect('/login')

def visit_c(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "visit_c.html", {"empid": empid})
    else:
        return redirect('/login')  

def download_c(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "download_c.html", {"empid": empid})
    else:
        return redirect('/login') 

def userlist(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "userlist.html", {"empid": empid})
    else:
        return redirect('/login')

def adminprofile(request):
    if request.session.has_key('empid'):
            empid = request.session.get('empid')
            user = get_object_or_404(ea_table, employee_id=empid)
            return render(request, 'adminprofile.html', {'user': user})
    else:
        return redirect('/login/')

def adminresetpassword(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']        
        user = get_object_or_404(ea_table, employee_id=empid)
        return render(request, "adminresetpassword.html", {"user": user})

    else:
        return redirect('/login/')

def create_j(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        departments = dept_table.objects.all()
        editors = ea_table.objects.filter(ea_type='editor')        
        return render(request, "create_j.html", {"empid": empid, 'departments': departments, 'editors': editors})
    else:
        return redirect('/login/')

def set_password(request):
    user = request.GET.get('user')
    request.session['token']=user
    return render(request, 'set_password.html')

def view_j(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        journals = journal_table.objects.all()  # Fetch all journals from the database
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


def add_editor(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "add_editor.html", {"empid": empid})
    else:
        return redirect('/login')


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


#ADD EDITOR 
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

        flag=0
        empidcheck = ''
        emailcheck = ''

        # Check if email already exists
        if ea_table.objects.filter(employee_id=employee_id).exists():
            flag = 1
            empidcheck = 'Employee Id alreaady exists'

        # Check if email already exists
        if ea_table.objects.filter(ea_email=ea_email).exists():
            flag = 1
            emailcheck = 'Email alreaady exists'
            
        if flag == 1:
            return render(request, 'add_editor.html', {'empidcheck': empidcheck, 'emailcheck': emailcheck})    
        
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

        desdata = designation_table()
        desdata.designation = designation
        desdata.save()

        sdata = seat_table()
        sdata.seat_name = role_name
        sdata.save()

        udata = usertable()
        udata.ea_id = eadata
        udata.seat_id = sdata
        udata.save()

         # Send email to the entered email address
        subject = 'Set Your Password'
        message = 'Click the link to set your password: http://127.0.0.1:8000/set_password/?user='+token
        html_message = render_to_string('email_template.html', {'message': message})
        plain_message = strip_tags(html_message)
        sender_email = 'subindax@gmail.com'  # Update with your email address
        send_mail(subject, plain_message, sender_email, [ea_email], html_message=html_message)
        
        messages.success(request, 'Added editor successfully. Now set your password using the mail we send to you.')
        return redirect('/add_editor/')

    # Render the form page
    return render(request, 'set_password.html', {'employee_id': employee_id})

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


def create_journal(request):
     if request.method == 'POST':
        journal_name = request.POST.get('journalName')
        department_id = request.POST.get('journalDepartment')
        editor_id = request.POST.get('editorId')

        if journal_name and department_id and editor_id:
            department = dept_table.objects.get(dept_id=department_id)
            # Get the editor instance using the editor_id
            editor = ea_table.objects.get(ea_id=editor_id)
            created_by = "Admin"  # Replace this with the actual logged-in admin's name

            # Create a new journal entry
            new_journal = journal_table.objects.create(
                journal_name=journal_name,
                dept_id=department,
                editor=editor,  # Assign the editor instance directly
                created_by=created_by
            )
        
        messages.success(request, 'Successfully created the journal.')    
        return redirect('/create_j/')  # Redirect to success page after creating journal
     return render(request, 'index.html')


def view_profile(request):
    empid = request.session.get('empid')
    user = get_object_or_404(ea_table, employee_id=empid)
    if user.ea_type == 'admin':
        return render(request, 'adminprofile.html', {'user': user})
    elif user.ea_type == 'editor':
        return render(request, 'editorprofile.html', {'user': user})
    else:
        return HttpResponse("Invalid user type", status=400)


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


def remove_journal(request, journal_id):
    journal = get_object_or_404(journal_table, journal_id=journal_id)

    if request.method == 'POST':
        # Collect related entries
        volumes = volume_table.objects.filter(journal_id=journal)
        issues = issue_table.objects.filter(volume_id__in=volumes)
        articles = article_table.objects.filter(issue_id__in=issues)
        eb_entries = eb_table.objects.filter(journal_id=journal)
        guidelines = gl_table.objects.filter(journal_id=journal)
        notifications = notification_table.objects.filter(journal_id=journal)
        article_visits = article_visit.objects.filter(article_id__in=articles)
        journal_visits = journalpage_visit.objects.filter(journal_id=journal)
        article_downloads = article_download.objects.filter(article_id__in=articles)

        # Delete related entries
        article_downloads.delete()
        article_visits.delete()
        notifications.delete()
        guidelines.delete()
        eb_entries.delete()
        articles.delete()
        issues.delete()
        volumes.delete()
        journal.delete()

        messages.success(request, 'Journal and all related entries have been successfully deleted.')
        return redirect('/view_j/')
    
    return redirect('/confirm_delete_journal/{}/'.format(journal_id))


def confirm_delete_journal(request, journal_id):
    journal = get_object_or_404(journal_table, journal_id=journal_id)

    # Collect details for confirmation
    volumes_count = volume_table.objects.filter(journal_id=journal).count()
    issues_count = issue_table.objects.filter(volume_id__journal_id=journal).count()
    articles_count = article_table.objects.filter(issue_id__volume_id__journal_id=journal).count()
    eb_entries_count = eb_table.objects.filter(journal_id=journal).count()
    guidelines_count = gl_table.objects.filter(journal_id=journal).count()
    notifications_count = notification_table.objects.filter(journal_id=journal).count()

    context = {
        'journal': journal,
        'volumes_count': volumes_count,
        'issues_count': issues_count,
        'articles_count': articles_count,
        'eb_entries_count': eb_entries_count,
        'guidelines_count': guidelines_count,
        'notifications_count': notifications_count,
    }

    return render(request, 'confirm_delete_journal.html', context)


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

                # Remove editor from other tables
                ea_table.objects.filter(ea_id=editor_id).delete()
                role_table.objects.filter(role_id=editor_id).delete()
                seat_table.objects.filter(seat_id=editor_id).delete()
                designation_table.objects.filter(designation_id=editor_id).delete()
                usertable.objects.filter(ea_id=editor_id).delete()

                messages.success(request, 'Editor has been successfully removed from all assigned journals and tables.')
                return redirect('/remove_editor/')
        
        return render(request, "remove_editor.html", {"empid": empid, "departments": departments})
    else:
        return redirect('/login/')

def get_editors_by_department(request, dept_id):
    editors = ea_table.objects.filter(dept_id=dept_id).values('ea_id', 'ea_name')
    return JsonResponse({'editors': list(editors)})

