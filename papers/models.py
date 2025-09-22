from django.db import models
from django.contrib.auth.models import User
import os
from ai_processing.utils import markdown_to_html
from django.db.models.signals import post_save
from django.dispatch import receiver

class Author(models.Model):
    """
    Represents an author. An author can be a registered user of the system,
    or an external author who is not a user (e.g., for citing existing papers).
    """
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="author_profile")
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
    # foreign key -> create many-to-one relationship. for eg. many paper objects can have the same user
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="uploaded_papers")
    title = models.CharField(max_length=300)
    article_content = models.TextField(blank=True, null=True)
    authors = models.ManyToManyField(Author, blank=True)
    publication_year = models.IntegerField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    pdf_file = models.FileField(upload_to='papers/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    
    @property
    def article_content_html(self):
        return markdown_to_html(self.article_content)

    def __str__(self): return self.title
    
    def filename(self):
        return os.path.basename(self.pdf_file.name)
    
    def delete(self, *args, **kwargs):
        self.pdf_file.delete(save=False)
        if self.thumbnail: self.thumbnail.delete(save=False)
        super().delete(*args, **kwargs)

    
class Comment(models.Model):
    """Represents a public comment on a specific paper."""
    paper = models.ForeignKey(Paper, related_name='comments', on_delete=models.CASCADE)
    # NEW: Link to the user who wrote the comment
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # Show newest comments first

    def __str__(self): return f'Comment by {self.user.username} on "{self.paper.title}"'

