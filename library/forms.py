from django import forms
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