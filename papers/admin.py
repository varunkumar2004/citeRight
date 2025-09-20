from django.contrib import admin
from .models import Author, Tag, Paper, Comment

# Register your models here.
admin.site.register(Author)
admin.site.register(Tag)
admin.site.register(Paper)
admin.site.register(Comment)
