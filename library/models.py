from django.db import models
from django.contrib.auth.models import User
import os

# Create your models here.

class Author(models.Model):
    """
    Represents an author. An author can be a registered user of the system,
    or an external author who is not a user (e.g., for citing existing papers).
    """
    # This links the Author to a specific user account.
    # It's optional (null=True, blank=True) because an author might not have an account.
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # This field is required to store the name of authors who are not users.
    name = models.CharField(max_length=200)

    def __str__(self):
        # If the author is linked to a user, display their username. Otherwise, use the name field.
        if self.user:
            return self.user.get_full_name() or self.user.username
        return self.name

class Tag(models.Model):
    """Represents a tag or keyword for organizing papers."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Paper(models.Model):
    """Represents a single research paper/document."""
    # Renamed 'user' to 'uploader' for clarity. This is the person who added the paper.
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    # This links to the authors who WROTE the paper.
    authors = models.ManyToManyField(Author, blank=True)
    publication_year = models.IntegerField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
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

