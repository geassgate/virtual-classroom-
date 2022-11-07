
from pydoc import describe
from django.db import models
from django.contrib.auth.models import User


class Lecturer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Corse(models.Model):
    lecturer_id = models.ForeignKey(Lecturer,related_name='corses', on_delete=models.CASCADE, default=None)
    name = models.CharField(max_length=50)

class Lecture(models.Model):
    corse = models.ForeignKey(Corse,related_name='lecture', on_delete=models.CASCADE)
    lecture_number = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50,default="ahmad")
    lec_date = models.DateField(auto_now=False, auto_now_add=False)
    time = models.TimeField(auto_now=False, auto_now_add=False)
    duration = models.CharField(max_length=5)
    describtion = models.CharField(max_length=10000,null=True)
    file = models.FileField(max_length=10000,upload_to=None,null=True)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    corses = models.ManyToManyField(Corse,blank=True,related_name="student")
