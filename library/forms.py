from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Paper, Note

class PaperUploadForm(forms.ModelForm):
    class Meta: 
        model = Paper
        fields = ['title', 'pdf_file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter paper title'}),
            'pdf_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'class': 'form-control', 
                    'rows': 4, 
                    'placeholder': 'Add your notes here...'
                }
            ),
        }
        
class SignUpForm(UserCreationForm):
    """
    This form correctly inherits from UserCreationForm to handle passwords
    and adds a required email field.
    """
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text='Required. Please enter a valid email address.'
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # This line inherits the fields from the parent form (which includes 'username')
        # and adds our new 'email' field to it. This ensures the password fields
        # are not accidentally removed.
        fields = UserCreationForm.Meta.fields + ('email',)
