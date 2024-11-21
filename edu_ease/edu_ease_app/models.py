from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.
class Document(models.Model):
    user = models.ForeignKey(User,on_delete=models.RESTRICT)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    document = models.ForeignKey(Document, on_delete=models.RESTRICT)
    question_text = models.TextField()
    answer = models.TextField(null=True, blank=True)
    # page_number = models.IntegerField(null=True, blank=True)
    # line_number = models.IntegerField(null=True, blank=True)

