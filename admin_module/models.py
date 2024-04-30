from django.db import models

# Create your models here.

#ea_table 
class ea_table(models.Model):
    ea_name=models.CharField(max_length=50)
    ea_email=models.CharField(max_length=50)
    ea_phone=models.CharField(max_length=20, default='')
    ea_dob=models.DateField(default='')
    ea_teacherid=models.CharField(max_length=20)
    ea_journalname=models.CharField(max_length=100)
    ea_type=models.CharField(max_length=25)
    password=models.CharField(max_length=90)
    otp=models.IntegerField()
    verification=models.BooleanField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=25)


    class Meta:
        db_table="ea_table"


#author_table
class author_table(models.Model):
    author_id = models.BigAutoField(primary_key=True)
    author_name = models.CharField(max_length=50)
    author_email = models.CharField(max_length=25)
    author_mobile = models.CharField(max_length=20)
    author_dob = models.DateField(default='')
    author_address = models.CharField(max_length=250)
    author_institute = models.CharField(max_length=100)
    author_designation = models.CharField(max_length=50)
    author_password = models.CharField(max_length=90)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=25)

    class Meta:
        db_table="author_table"


#user_table
class user_table(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    user_name = models.CharField(max_length=50)
    user_email = models.CharField(max_length=50)
    user_mobile = models.CharField(max_length=25)
    user_password = models.CharField(max_length=90)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=25)

    class Meta:
        db_table="user_table"

#dept_table
class dept_table(models.Model):
    dept_id = models.BigAutoField(primary_key=True)
    dept_name = models.CharField(max_length=50)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=25)

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
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=25)

    class Meta:
        db_table="journal_table"


#volume_table
class volume_table(models.Model):
    volume_id = models.BigAutoField(primary_key=True)
    journal_id = models.ForeignKey(journal_table,default="1",on_delete=models.SET_DEFAULT)
    volume_no = models.CharField(max_length=50)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
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
    status=models.CharField(max_length=25)

    class Meta:
        db_table="issue_table"

#author_colab
class author_colab(models.Model):
    colab_id = models.BigAutoField(primary_key=True)
    author_name = models.ForeignKey(author_table,default="1",on_delete=models.SET_DEFAULT,blank=True)
    second_author = models.CharField(max_length=50)
    third_author = models.CharField(max_length=50)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=25)


    class Meta:
        db_table="author_colab"



#article_table
class article_table(models.Model):
    article_id = models.BigAutoField(primary_key=True)
    issue_id = models.ForeignKey(issue_table,default="1",on_delete=models.SET_DEFAULT)
    author_name = models.ForeignKey(author_table,default="1",on_delete=models.SET_DEFAULT,blank=True)
    colab_id = models.ForeignKey(author_colab,default="1",on_delete=models.SET_DEFAULT,blank=True)
    article_title = models.CharField(max_length=90)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=25)

    class Meta:
        db_table="article_table"


#eb_table
class eb_table(models.Model):
    board_id = models.BigAutoField(primary_key=True)
    journal_id = models.ForeignKey(journal_table,default="1",on_delete=models.SET_DEFAULT)
    id = models.ForeignKey(ea_table,default="1",on_delete=models.SET_DEFAULT)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=25)

    class Meta:
        db_table="eb_table"


#gl_table
class gl_table(models.Model):
    gl_id = models.BigAutoField(primary_key=True)
    journal_id = models.ForeignKey(journal_table,default="1",on_delete=models.SET_DEFAULT)
    heading =  models.CharField(max_length=90)
    content =  models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=25)


    class Meta:
        db_table="gl_table"


#art_visit
class art_visit(models.Model):
    art_visit_id = models.BigAutoField(primary_key=True)
    article_id = models.ForeignKey(article_table,default="1",on_delete=models.SET_DEFAULT)
    avisit_date = models.DateField(default='')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=25)


    class Meta:
        db_table="art_visit"


#issue_visit
class journal_visit(models.Model):
    journal_visit_id = models.BigAutoField(primary_key=True)
    journal_id = models.ForeignKey(journal_table,default="1",on_delete=models.SET_DEFAULT)
    jvisit_date = models.DateField(default='')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=25)


    class Meta:
        db_table="journal_visit"


#article_download
class art_dld(models.Model):
    dld_id = models.BigAutoField(primary_key=True)
    article_id = models.ForeignKey(article_table,default="1",on_delete=models.SET_DEFAULT)
    dld_date = models.DateField(default='')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=25)

    class Meta:
        db_table="art_dld"


#user access article(uaa)
class uaa(models.Model):
    access_id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(user_table,default="1",on_delete=models.SET_DEFAULT)
    article_id = models.ForeignKey(article_table,default="1",on_delete=models.SET_DEFAULT)
    access_date = models.DateField(default='')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=25)

    class Meta:
        db_table="uaa"


 