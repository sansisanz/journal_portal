from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render
import hashlib
from admin_module.models import ea_table, role_table, seat_table, designation_table, usertable, dept_table, journal_table
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
        empid = request.session['empid']
        return render(request, "adminprofile.html", {"empid": empid})
    else:
        return redirect('/login')

def adminresetpassword(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "adminresetpassword.html", {"empid": empid})
    else:
        return redirect('/login')

def create_j(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        departments = dept_table.objects.all()
        editors = ea_table.objects.filter(ea_type='editor')        
        return render(request, "create_j.html", {"empid": empid, 'departments': departments, 'editors': editors})
    else:
        return redirect('/login')

def set_password(request):
    user = request.GET.get('user')
    request.session['token']=user
    return render(request, 'set_password.html')

def view_j(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        journals = journal_table.objects.all()  # Fetch all journals from the database
        return render(request, "view_j.html", {"empid": empid, 'journals': journals})
    else:
        return redirect('/login')
 
def edit_j(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "edit_j.html", {"empid": empid})
    else:
        return redirect('/login')

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
        
        return redirect('/index/')

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
        return redirect('/create_j/')  # Redirect to success page after creating journal
     return render(request, 'index.html')


