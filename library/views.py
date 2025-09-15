from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Paper, Tag # Import the Tag model
from .forms import PaperUploadForm, NoteForm
from django.http import HttpResponseForbidden
import PyPDF2

# --- New Imports for Tag Extraction ---
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
import re

# Download stopwords data for NLTK (only needs to be done once)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords
# --- End of New Imports ---


@login_required
def paper_list_view(request, username=None):
    """
    This single view handles both the universal paper list and user-specific profile pages.
    - If a username is provided, it filters for that user's papers.
    - Otherwise, it displays all papers from every user.
    """
    if username:
        # This is a user's profile view
        user = get_object_or_404(User, username=username)
        papers = Paper.objects.filter(uploader=user).order_by('-uploaded_at')
        view_title = f"Papers Uploaded by {user.username}"
    else:
        # This is the universal, all-papers view
        papers = Paper.objects.all().order_by('-uploaded_at')
        view_title = 'All Papers in the Library'

    context = {'papers': papers, 'view_title': view_title}
    return render(request, 'library/paper_list.html', context)


@login_required
def paper_detail(request, pk):
    """Display details for a single paper and handle note creation."""
    paper = get_object_or_404(Paper, pk=pk)
    noteform = NoteForm()
    
    if request.method == "POST":
        noteform = NoteForm(request.POST)
        if noteform.is_valid():
            note = noteform.save(commit=False)
            note.paper = paper
            note.save()
            return redirect('library:paper_detail', pk=paper.pk)
    
    context = {
        'paper': paper,
        'noteform': noteform
    }
    
    return render(request, 'library/paper_detail.html', context)


@login_required
def upload_paper(request):
    """Handle the paper upload process and extract tags."""
    if request.method == 'POST':
        form = PaperUploadForm(request.POST, request.FILES)
        if form.is_valid():
            paper = form.save(commit=False)
            paper.uploader = request.user 
            
            pdf_file = request.FILES['pdf_file']
            
            try:
                # Ensure the file pointer is at the beginning
                pdf_file.seek(0)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                metadata = pdf_reader.metadata
                if not paper.title and metadata and metadata.title:
                    paper.title = metadata.title
            except Exception as e:
                print(f"Could not extract metadata: {e}")
            finally:
                if not paper.title:
                    paper.title = "Untitled Paper"

            paper.save()
            form.save_m2m() # Save authors first

            # --- New Logic for Tag Extraction ---
            try:
                # Reset file pointer again to read content
                pdf_file.seek(0)
                pdf_reader_for_text = PyPDF2.PdfReader(pdf_file)
                full_text = ""
                for page in pdf_reader_for_text.pages:
                    full_text += page.extract_text() or ""
                
                # Clean the text: remove non-alphanumeric characters
                full_text = re.sub(r'[^a-zA-Z\s]', '', full_text).lower()

                if full_text.strip():
                    # Use TF-IDF to find the most important words
                    stop_words = list(stopwords.words('english'))
                    vectorizer = TfidfVectorizer(stop_words=stop_words, max_features=10) # Get top 10 keywords
                    tfidf_matrix = vectorizer.fit_transform([full_text])
                    feature_names = vectorizer.get_feature_names_out()

                    for term in feature_names:
                        # Get or create the tag and add it to the paper
                        tag, created = Tag.objects.get_or_create(name=term)
                        paper.tags.add(tag)
                
            except Exception as e:
                print(f"Could not extract tags: {e}")
            # --- End of New Logic ---

            return redirect('library:paper_list')
    else:
        form = PaperUploadForm()
    return render(request, 'library/paper_upload.html', {'form': form})

@login_required
def delete_paper(request, pk):
    """Handles the deletion of a paper with a confirmation step."""
    paper = get_object_or_404(Paper, pk=pk)
    
    # Security check: only the uploader can delete their own paper
    if paper.uploader != request.user:
        return HttpResponseForbidden("You are not allowed to delete this paper.")
    
    if request.method == 'POST':
        paper.delete()
        # Redirect to the user's profile page after deletion
        return redirect('library:profile_view', username=request.user.username)
    
    # For a GET request, show the confirmation page
    return render(request, 'library/paper_confirm_delete.html', {'paper': paper})