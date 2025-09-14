from django.db import models
from django.contrib.auth.models import User
import os

# Create your models here.

class Author(models.Model):
    """Represents a single author."""
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    """Represents a tag or keyword for organizing papers."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Paper(models.Model):
    """Represents a single research paper/document."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    authors = models.ManyToManyField(Author, blank=True)
    publication_year = models.IntegerField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    # The actual PDF file will be stored here
    pdf_file = models.FileField(upload_to='papers/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def filename(self):
        return os.path.basename(self.pdf_file.name)

class Note(models.Model):
    """Represents a user's note on a specific paper."""
    paper = models.ForeignKey(Paper, related_name='notes', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Note on "{self.paper.title}"'
