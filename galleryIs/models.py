from django.db import models
import os
from django.db.models.signals import pre_save
# Create your models here.

class Genre(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Author(models.Model):
    id = models.AutoField(primary_key=True)
    fullName = models.CharField(max_length=100)
    birthday = models.DateTimeField()

    def __str__(self):
        return self.fullName



class Painting(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    createDT = models.DateTimeField()
    authors = models.ManyToManyField(Author)
    genres= models.ManyToManyField(Genre)

    def __str__(self):
        return self.title

class Refurbishment(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.CharField(max_length=100)
    startDT = models.DateTimeField()
    endDT = models.DateTimeField()
    painting = models.ForeignKey(Painting, 
    on_delete=models.CASCADE)

    def __str__(self):
        return '%s %s' % (self.painting.title, self.state)

class Exhibition(models.Model):
    id = models.AutoField(primary_key=True)
    theme = models.CharField(max_length=100)
    startDT = models.DateTimeField()
    endDT = models.DateTimeField()
    paintings = models.ManyToManyField(Painting)
   
    
    def __str__(self):
        return self.theme

def file_folder(instance, filename):
    return "{0}/{1}/{2}".format("template",'report', filename)
   
class Template(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    template = models.FileField(upload_to=file_folder)

    def __str__(self):
        return self.title

class Report(models.Model):
    exhibition = models.OneToOneField(Exhibition, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    visitorsQTY = models.IntegerField()
    descriprion = models.TextField(max_length=2500)
    createDT = models.DateTimeField()
    template = models.OneToOneField(Template, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.exhibition.theme

def validate_file_extension(sender, instance, *args, **kwargs):
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(instance.template.path)[1]  # [0] returns path+filename
    valid_extensions = ['.html']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')

pre_save.connect(validate_file_extension, sender=Template)