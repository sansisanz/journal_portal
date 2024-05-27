from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from admin_module.models import article_table, ea_table, dept_table, gl_table, journal_table, notification_table, volume_table, issue_table, eb_table
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
        # Fetch journals assigned to the logged-in user
        journals = journal_table.objects.filter(editor__employee_id=empid)
        return render(request, "editorialboard.html", {"empid": empid, "journals": journals})
    else:
        return redirect('/login')
      
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
        
        return redirect('/editorialboard/')  # Redirect to a success page after saving
     else:
        return render(request,'add_editorial_board_member.html')

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
    return FileResponse(article.article_file)

def approve_article(request, article_id):
    article = get_object_or_404(article_table, pk=article_id)
    article.status = 'approved'
    article.save()
    return redirect('/view_articles/')

def reject_article(request, article_id):
    article = get_object_or_404(article_table, pk=article_id)
    article.status = 'rejected'
    article.save()
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
        volumes = getvolume(journal_id)
        
        return render(request, "edit_vic.html", {"empid": empid, "volumes": volumes, "journal_id": journal_id})
    else:
        return redirect('/login/')
    
def edit_volume(request, journal_id):
    if request.session.has_key('empid'):
        if request.method == 'POST':
            action = request.POST.get('action')
            volume_id = request.POST.get('volume')
            volume = get_object_or_404(volume_table, volume_id=volume_id)

            if action == 'updateVolume':
                volume_name = request.POST.get('volumeName')
                volume.volume = volume_name
                volume.save()
            elif action == 'updateCoverPhoto':
                cover_photo = request.FILES['coverPhoto']
                volume.cover_image = cover_photo
                volume.save()
            elif action == 'addMoreIssues':
                more_issues = int(request.POST.get('issueNumber'))
                for _ in range(more_issues):
                    new_issue = issue_table(volume_id=volume)
                    new_issue.save()
        
        return redirect('/edit_vic/{}/'.format(journal_id))
    else:
        return redirect('/login/')    

def remove(request, journal_id):
    if request.session.has_key('empid'):
        empid = request.session['empid']
        # Perform the removal operation here
        journal = journal_table.objects.get(journal_id=journal_id)
        journal.delete()
        return redirect('/upddetails/')
    else:
        return redirect('/login/')
        
#-------------------------------------------------------------------------------------------------------------------------------------    

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

