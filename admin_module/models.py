from django.db import models

# Create your models here.


#author_table
class author_table(models.Model):
    author_id = models.BigAutoField(primary_key=True)
    author_type = models.CharField(max_length=50, default='')
    author_name = models.CharField(max_length=50)
    author_email = models.CharField(max_length=90)
    author_mobile = models.CharField(max_length=20)
    author_dob = models.DateField(default='')
    author_address = models.CharField(max_length=250)
    author_institute = models.CharField(max_length=100)
    author_designation = models.CharField(max_length=50)
    author_password = models.CharField(max_length=90)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    #created_by=models.CharField(max_length=50)
    status=models.CharField(max_length=25)
    verify = models.BooleanField(default=False)
    token = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        db_table="author_table"


#dept_table
class dept_table(models.Model):
    dept_id = models.BigAutoField(primary_key=True)
    dept_name = models.CharField(max_length=50)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table="dept_table"


#journal_table
class journal_table(models.Model):
    journal_id = models.BigAutoField(primary_key=True)
    dept_id = models.ForeignKey(dept_table,default="1",on_delete=models.SET_DEFAULT)
    journal_name = models.CharField(max_length=50)
    journal_aim = models.TextField()
    journal_ethics = models.TextField()
    journal_update = models.TextField(default='')
    update_link = models.CharField(max_length=60, default='')
    logo = models.CharField(max_length=100,default="")
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    created_by=models.CharField(max_length=50, default='')
    status=models.CharField(max_length=25)

    class Meta:
        db_table="journal_table"


#volume_table
class volume_table(models.Model):
    volume_id = models.BigAutoField(primary_key=True)
    journal_id = models.ForeignKey(journal_table,default="1",on_delete=models.SET_DEFAULT)
    volume_no = models.CharField(max_length=50)
    cover_image = models.CharField(max_length=100,default="")
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    created_by=models.CharField(max_length=50, default='')
    status=models.CharField(max_length=25)

    class Meta:
        db_table="volume_table"


#issue_table
class issue_table(models.Model):
    issue_id = models.BigAutoField(primary_key=True)
    volume_id = models.ForeignKey(dept_table,default="1",on_delete=models.SET_DEFAULT)
    issue_no =  models.CharField(max_length=50)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    created_by=models.CharField(max_length=50,default="")
    status=models.CharField(max_length=25)

    class Meta:
        db_table="issue_table"


#article_table
class article_table(models.Model):
    article_id = models.BigAutoField(primary_key=True)
    issue_id = models.ForeignKey(issue_table,default="1",on_delete=models.SET_DEFAULT)
    author_name = models.ForeignKey(author_table,default="1",on_delete=models.SET_DEFAULT,blank=True)
    article_title = models.CharField(max_length=90)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    created_by=models.CharField(max_length=50, default='')
    status=models.CharField(max_length=25)

    class Meta:
        db_table="article_table"


#eb_table
class eb_table(models.Model):
    board_id = models.BigAutoField(primary_key=True)
    journal_id = models.ForeignKey(journal_table,default="1",on_delete=models.SET_DEFAULT)
    editor_name = models.CharField(max_length=25, default="")
    editor_address = models.CharField(max_length=25, default="")
    editor_email = models.CharField(max_length=25, default="")
    editor_mobile = models.CharField(max_length=25, default="")
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    created_by= models.CharField(max_length=50, default="")
    status=models.CharField(max_length=25)

    class Meta:
        db_table="eb_table"


#guidelines_table
class gl_table(models.Model):
    gl_id = models.BigAutoField(primary_key=True)
    journal_id = models.ForeignKey(journal_table,default="1",on_delete=models.SET_DEFAULT)
    heading =  models.CharField(max_length=90)
    content =  models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    created_by= models.CharField(max_length=50, default="")
    status=models.CharField(max_length=25)


    class Meta:
        db_table="gl_table"


#article_visit
class article_visit(models.Model):
    art_visit_id = models.BigAutoField(primary_key=True)
    article_id = models.ForeignKey(article_table,default="1",on_delete=models.SET_DEFAULT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    created_by= models.CharField(max_length=50, default="")
    status = models.CharField(max_length=25)
    count = models.IntegerField()


    class Meta:
        db_table="article_visit"


#journal page visit
class journalpage_visit(models.Model):
    journal_visit_id = models.BigAutoField(primary_key=True)
    journal_id = models.ForeignKey(journal_table,default="1",on_delete=models.SET_DEFAULT)
    count = models.IntegerField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    created_by= models.CharField(max_length=50, default="")
    status=models.CharField(max_length=25)


    class Meta:
        db_table="journalpage_visit"


#article_download
class article_download(models.Model):
    dld_id = models.BigAutoField(primary_key=True)
    article_id = models.ForeignKey(article_table,default="1",on_delete=models.SET_DEFAULT)
    count = models.IntegerField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    created_by= models.CharField(max_length=50, default="")
    status=models.CharField(max_length=25)

    class Meta:
        db_table="article_download"


#editoradmin_table
class ea_table(models.Model):   
    ea_id = models.BigAutoField(primary_key=True, default="")
    employee_id = models.CharField(max_length=50, default="")
    ea_name = models.CharField(max_length=50)
    ea_email = models.CharField(max_length=90, default="")
    password = models.CharField(max_length=90)
    dept_id = models.ForeignKey(dept_table,default="1",on_delete=models.SET_DEFAULT)   
    ea_type = models.CharField(max_length=70, default="")
    token = models.CharField(max_length=90, default='')
    status = models.CharField(max_length=50, default="active")

    class Meta:
        db_table="ea_table"


#role_table
class role_table(models.Model):
    role_id = models.BigAutoField(primary_key=True)
    role_name = models.CharField(max_length=30)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    #created_by=models.CharField(max_length=50)
    status=models.CharField(max_length=25)
    
    class Meta:
        db_table="role_table"


#seat_table
class seat_table(models.Model):
    seat_id = models.BigAutoField(primary_key=True)
    seat_name = models.CharField(max_length=30)
    role_id = models.ForeignKey(role_table,default="1",on_delete=models.SET_DEFAULT)    
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    #created_by=models.CharField(max_length=50)
    status=models.CharField(max_length=25)

    class Meta:
        db_table="seat_table"        


#designation_table
class designation_table(models.Model):
    designation_id = models.BigAutoField(primary_key=True)
    designation = models.CharField(max_length=30)
    role_id = models.ForeignKey(role_table,default="1",on_delete=models.SET_DEFAULT)   
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    #created_by=models.CharField(max_length=50)
    status=models.CharField(max_length=25)

    class Meta:
        db_table="designation_table"        


#usertable
class usertable(models.Model):
    usertable_id = models.BigAutoField(primary_key=True)
    ea_id = models.ForeignKey(ea_table,default="1",on_delete=models.SET_DEFAULT)
    seat_id = models.ForeignKey(seat_table,default="1",on_delete=models.SET_DEFAULT)    

    class Meta:
        db_table="usertable"        


