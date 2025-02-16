from django.db import models
from datetime import datetime

#author_table
class author_table(models.Model):
    author_id = models.BigAutoField(primary_key=True)
    author_type = models.CharField(max_length=50)
    author_name = models.CharField(max_length=50)
    author_email = models.CharField(max_length=90)
    author_mobile = models.CharField(max_length=20)
    author_dob = models.DateField()
    author_address = models.CharField(max_length=250)
    author_institute = models.CharField(max_length=100)
    author_password = models.CharField(max_length=90)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    #created_by=models.CharField(max_length=50)
    status=models.CharField(max_length=25)
    verify = models.BooleanField(default=False)
    token = models.CharField(max_length=100, null=True, blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table="author_table"

    def save(self, *args, **kwargs):
        # Update the updated_at attribute before saving
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)     


#dept_table
class dept_table(models.Model):
    dept_id = models.BigAutoField(primary_key=True)
    dept_name = models.CharField(max_length=50)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        db_table="dept_table"

    def save(self, *args, **kwargs):
        # Update the updated_at attribute before saving
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)        

#editoradmin_table
class ea_table(models.Model):   
    ea_id = models.BigAutoField(primary_key=True)
    employee_id = models.CharField(max_length=50)
    ea_name = models.CharField(max_length=50)
    ea_email = models.CharField(max_length=90)
    password = models.CharField(max_length=90)
    dept_id = models.ForeignKey(dept_table,default="1",on_delete=models.SET_DEFAULT)   
    ea_type = models.CharField(max_length=70)
    status = models.CharField(max_length=50, default="active")
    ea_mobile = models.CharField(max_length=20, default='')
    ea_address = models.CharField(max_length=200, default='')
    token = models.CharField(max_length=100, null=True, blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.now)  # Provide a default value
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table="ea_table"

    def save(self, *args, **kwargs):
        # Update the updated_at attribute before saving
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)        


#role_table
class role_table(models.Model):
    role_id = models.BigAutoField(primary_key=True)
    role_name = models.CharField(max_length=30)
    
    class Meta:
        db_table="role_table"

#seat_table
class seat_table(models.Model):
    seat_id = models.BigAutoField(primary_key=True)
    seat_name = models.CharField(max_length=30)
    role_id = models.ForeignKey(role_table,default="1",on_delete=models.SET_DEFAULT)    


    class Meta:
        db_table="seat_table"        


#designation_table
class designation_table(models.Model):
    designation_id = models.BigAutoField(primary_key=True)
    designation = models.CharField(max_length=30)
    role_id = models.ForeignKey(role_table,default="1",on_delete=models.SET_DEFAULT)    

    class Meta:
        db_table="designation_table"        


#usertable
class usertable(models.Model):
    usertable_id = models.BigAutoField(primary_key=True)
    ea_id = models.ForeignKey(ea_table,default="1",on_delete=models.SET_DEFAULT)
    seat_id = models.ForeignKey(seat_table,default="1",on_delete=models.SET_DEFAULT) 
    status = models.CharField(max_length=50, default="active")   

    class Meta:
        db_table="usertable"                


#journal_table
class journal_table(models.Model):
    journal_id = models.BigAutoField(primary_key=True)
    dept_id = models.ForeignKey(dept_table,default="1",on_delete=models.SET_DEFAULT)
    editor = models.ForeignKey(ea_table, null=True, blank=True, default="1",on_delete=models.SET_DEFAULT)
    journal_name = models.CharField(max_length=50)
    journal_aim = models.TextField()
    journal_ethics = models.TextField()
    banner = models.CharField(max_length=100,default="")
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    created_by=models.CharField(max_length=50)
    status=models.CharField(max_length=25)
    email = models.CharField(max_length=90, default='')
    phone = models.CharField(max_length=20, default = '')
    visit_count = models.IntegerField(default=0)
    issn_number = models.CharField(max_length=20, default='')
    ugc_care_list_number = models.CharField(max_length=50, default='')
    national_registration_number = models.CharField(max_length=50, default='')

    class Meta:
        db_table="journal_table"

    def save(self, *args, **kwargs):
        # Update the updated_at attribute before saving
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)    
    
#volume_table
class volume_table(models.Model):
    volume_id = models.BigAutoField(primary_key=True)
    journal_id = models.ForeignKey(journal_table,default="1",on_delete=models.SET_DEFAULT)
    volume = models.CharField(max_length=50, default='')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    created_by=models.CharField(max_length=50)
    status=models.CharField(max_length=25)

    class Meta:
        db_table="volume_table"


#issue_table
class issue_table(models.Model):
    issue_id = models.BigAutoField(primary_key=True)
    volume_id = models.ForeignKey(volume_table,default="1",on_delete=models.SET_DEFAULT)
    issue_no =  models.CharField(max_length=50)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    created_by=models.CharField(max_length=50)
    status=models.CharField(max_length=25)
    cover_image = models.ImageField(upload_to='issue_covers/', default='')
    current_page_number = models.IntegerField(default=1)

    class Meta:
        db_table="issue_table"


#article_table
class article_table(models.Model):
    article_id = models.BigAutoField(primary_key=True)
    issue_id = models.ForeignKey(issue_table,default="1",on_delete=models.SET_DEFAULT)
    author_id = models.ForeignKey(author_table,default="1",on_delete=models.SET_DEFAULT,blank=True)
    author1 = models.CharField(max_length=90, default='1')
    author2 = models.CharField(max_length=90, blank=True, null=True)
    author3 = models.CharField(max_length=90, blank=True, null=True)
    article_title = models.CharField(max_length=90)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    created_by=models.CharField(max_length=50)
    status=models.CharField(max_length=25)
    article_file = models.FileField(upload_to='articles/', default='')
    visit_count = models.IntegerField(default=0) 
    download_count = models.IntegerField(default=0)
    ea_id = models.ForeignKey(ea_table,default="1",on_delete=models.SET_DEFAULT)
    starting_page_number = models.IntegerField(default=1)  

    class Meta:
        db_table="article_table"


#eb_table
class eb_table(models.Model):
    board_id = models.BigAutoField(primary_key=True)
    journal_id = models.ForeignKey(journal_table,default="1",on_delete=models.SET_DEFAULT)
    editor_name = models.CharField(max_length=50)
    editor_address = models.CharField(max_length=100, default='')
    editor_email = models.CharField(max_length=100, default='')
    editor_mobile = models.CharField(max_length=20)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    created_by=models.CharField(max_length=50)
    status=models.CharField(max_length=25)
    photo=models.ImageField(upload_to='eb_photos/', default='')

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
    created_by=models.CharField(max_length=50)
    status=models.CharField(max_length=25)


    class Meta:
        db_table="gl_table"


#notification_table
class notification_table(models.Model):
    notification_id = models.BigAutoField(primary_key=True)
    journal_id = models.ForeignKey(journal_table,default="1",on_delete=models.SET_DEFAULT)
    notification = models.CharField(max_length=100)
    link = models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    created_by=models.CharField(max_length=50)
    status=models.CharField(max_length=25)

    class Meta:
        db_table="notification_table"        

class JournalPageVisit(models.Model):
    journal_visit_id = models.BigAutoField(primary_key=True)
    journal_id = models.ForeignKey(journal_table, default=1, on_delete=models.SET_DEFAULT)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "journalpage_visit"


class ArticleVisit(models.Model):
    art_visit_id = models.BigAutoField(primary_key=True)
    article_id = models.ForeignKey(article_table, default=1, on_delete=models.SET_DEFAULT)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "article_visit"


class ArticleDownload(models.Model):
    dld_id = models.BigAutoField(primary_key=True)
    article_id = models.ForeignKey(article_table, default=1, on_delete=models.SET_DEFAULT)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "article_download"


#message_table
class message_table(models.Model):
    msg_id = models.BigAutoField(primary_key=True)
    journal_id = models.ForeignKey(journal_table,default="1",on_delete=models.SET_DEFAULT)
    ea_id = models.ForeignKey(ea_table,default="1",on_delete=models.SET_DEFAULT)
    msg_name = models.CharField(max_length=50)
    msg_email = models.CharField(max_length=90)
    subject = models.CharField(max_length=200)
    message = models.CharField(max_length=50)    
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table="message_table"

class review_table(models.Model):
    review_id = models.BigAutoField(primary_key=True)
    article_id = models.ForeignKey(article_table, default=1, on_delete=models.SET_DEFAULT) 
    editor_id = models.ForeignKey(ea_table, default=1, on_delete=models.SET_DEFAULT)
    review = models.TextField()       
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=25)

    class Meta:
        db_table="review_table"
    


