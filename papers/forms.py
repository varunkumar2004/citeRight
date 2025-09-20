from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Paper, Comment

class PaperUploadForm(forms.ModelForm):
    """
    Form for uploading a new paper. Includes fields to tag existing users
    as authors and to create new authors who are not users.
    """
    author_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by('username'),
        widget=forms.SelectMultiple(attrs={'class': 'author-select-input'}),
        required=False,
        label="Select Authors (from platform users)"
    )
    
    new_authors = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'e.g., John Doe'}),
        required=False,
        label="Add Authors (Non-Users)",
        help_text="Separate multiple author names with a comma."
    )
    
    class Meta: 
        model = Paper
        fields = ['title', 'pdf_file', 'publication_year']
        # widgets = {
        #     'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter paper title'}),
        #     'pdf_file': forms.FileInput(attrs={'class': 'form-control'}),
        # }
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'class': 'form-control', 
                    'rows': 3, 
                    'placeholder': 'Join the discussion...'
                }
            ),
        }