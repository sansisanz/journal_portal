from django.shortcuts import render,redirect
from admin_module.models import ea_table, dept_table, gl_table, journal_table, volume_table, issue_table
# Create your views here.

def editor_article(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "article.html", {"empid": empid})
    else:
        return redirect('/login')

def editorialboard(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "editorialboard.html", {"empid": empid})
    else:
        return redirect('/login')

def editor_forgotpassword(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "forgot-password.html", {"empid": empid})
    else:
        return redirect('/login')

def editor_index(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "editorindex.html")
        
    return redirect('/login')

def add_vic(request, journal_id):
    if not request.session.has_key('empid'):
        return redirect('/login')

    empid = request.session['empid']
    user_name = request.session['editor_name']  # Assuming user's name is stored in session

    if request.method == 'POST':
        # Retrieve form data
        volume_name = request.POST.get('volume')
        cover_image = request.FILES.get('cover_image')
        num_issues = int(request.POST.get('num_issues'))

        # Get the journal corresponding to the provided journal_id
        journal = journal_table.objects.get(pk=journal_id)

        # Create a new volume entry for the journal
        new_volume = volume_table.objects.create(
            journal_id=journal, 
            volume=volume_name, 
            cover_image=cover_image, 
            created_by=user_name,
            status='active'
        )

        # Create issues for the volume
        for issue_number in range(1, num_issues + 1):
            issue_table.objects.create(
                volume_id=new_volume, 
                issue_no=str(issue_number),
                created_by=user_name,
                status='active'
            )

        # Redirect to a success page or back to the journal list
        return redirect('/editor_assignedjournal/')  # Change this to your success URL

    return render(request, 'add_vic.html', {'journal_id': journal_id})

def editor_profile(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "profile.html", {"empid": empid})
    else:
        return redirect('/login')

def editor_register(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "register.html", {"empid": empid})
    else:
        return redirect('/login')

def editor_resetpassword(request):
    
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "resetpassword.html", {"empid": empid})
    else:
        return redirect('/login')
    
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

def editor_updates(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "notifications.html", {"empid": empid})
    else:
        return redirect('/login')

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

def uploadArticle(request):   
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "uploadarticle.html", {"empid": empid})
    else:
        return redirect('/login')

def journaldetails(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "journaldetails.html", {"empid": empid})
    else:
        return redirect('/login')
    

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
                guideline = gl_table(journal_id=journal_id, heading=heading, content=content)
                guideline.save()

            return redirect('/editor_index/')  # Redirect to success page after form submission
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
 

def upddetails(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "upddetails.html", {"empid": empid})
    else:
        return redirect('/login')

def edit(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "edit.html", {"empid": empid})
    else:
        return redirect('/login')

def e_visits(request):
    
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "e_visits.html", {"empid": empid})
    else:
        return redirect('/login')

def e_downloads(request):
    
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "e_downloads.html", {"empid": empid})
    else:
        return redirect('/login')

def remove(request):
    
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "remove.html", {"empid": empid})
    else:
        return redirect('/login')

def editor_contact(request):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        return render(request, "editor_contact.html", {"empid": empid})
    else:
        return redirect('/login')