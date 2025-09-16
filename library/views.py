from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Paper, Tag, Author
from .forms import PaperUploadForm, NoteForm
from django.http import HttpResponseForbidden
import PyPDF2
from django.db.models import Q
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
import re
import fitz # PyMuPDF
from django.core.files.base import ContentFile
from nltk.corpus import stopwords


try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


@login_required
def paper_list_view(request, username=None):
    """
    Handles displaying papers. Now includes search functionality.
    """
    context = {}
    query = request.GET.get('q') # Get the search query from the URL's GET parameters

    if query:
        # If a search query is provided, filter the papers across multiple fields
        papers = Paper.objects.filter(
            Q(title__icontains=query) |
            Q(uploader__username__icontains=query) |
            Q(authors__name__icontains=query)
        ).distinct().order_by("-uploaded_at") # Use distinct() to avoid duplicate results from the author search
        
        view_title = f"Search Results for '{query}'"
        context = {
            'papers': papers,
            'view_title': view_title,
            'search_query': query
        }
    elif username:
        # If viewing a specific user's profile
        user = get_object_or_404(User, username=username)
        papers = Paper.objects.filter(uploader=user).order_by("-uploaded_at")
        view_title = f"Papers Uploaded by {user.username}"
        context = {
            'papers': papers,
            'view_title': view_title,
            'search_query': query
        }
    else:
        # The default view showing all papers
        all_papers = Paper.objects.all().order_by("-uploaded_at")
        followed_users = request.user.profile.following.all()
        feed_papers = Paper.objects.filter(uploader__in=followed_users).order_by('-uploaded_at')
        view_title = 'Home'
        context = {
            'all_papers': all_papers,
            'feed_papers': feed_papers,
            'view_title': view_title,
            'is_home_view': True  # A flag for the template to render tabs
        }
    
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
    """
    Handle the paper upload process, including author tagging, thumbnail generation,
    and keyword extraction.
    """
    if request.method == 'POST':
        form = PaperUploadForm(request.POST, request.FILES)
        if form.is_valid():
            paper = form.save(commit=False)
            paper.uploader = request.user 
            paper.save()
            form.save_m2m() 

            # Handle author tagging
            tagged_users = form.cleaned_data.get('author_users', [])
            for user in tagged_users:
                author_profile, created = Author.objects.get_or_create(user=user, defaults={'name': user.username})
                paper.authors.add(author_profile)

            new_author_names = form.cleaned_data.get('new_authors')
            if new_author_names:
                author_names = [name.strip() for name in new_author_names.split(',') if name.strip()]
                for name in author_names:
                    author, created = Author.objects.get_or_create(name=name, user=None)
                    paper.authors.add(author)
            
            uploaded_file = request.FILES['pdf_file']
            
            # Conditionally process the file if it's a PDF
            if uploaded_file.name.lower().endswith('.pdf'):
                try:
                    # Generate thumbnail
                    uploaded_file.seek(0)
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    page = doc.load_page(0) 
                    pix = page.get_pixmap()
                    img_bytes = pix.tobytes("png")
                    thumbnail_file = ContentFile(img_bytes)
                    paper.thumbnail.save(f'{paper.pk}_thumbnail.png', thumbnail_file, save=True)
                    doc.close()

                    # Extract keyword tags
                    uploaded_file.seek(0)
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    full_text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
                    full_text = re.sub(r'[^a-zA-Z\s]', '', full_text).lower()
                    if full_text.strip():
                        stop_words = list(stopwords.words('english'))
                        vectorizer = TfidfVectorizer(stop_words=stop_words, max_features=10)
                        vectorizer.fit_transform([full_text])
                        feature_names = vectorizer.get_feature_names_out()
                        for term in feature_names:
                            tag, created = Tag.objects.get_or_create(name=term)
                            paper.tags.add(tag)

                except Exception as e:
                    print(f"Error processing PDF file: {e}")
            else:
                print(f"Skipping thumbnail and tag generation for non-PDF file: {uploaded_file.name}")

            return redirect('library:paper_list')
    else:
        form = PaperUploadForm()
    return render(request, 'library/paper_upload.html', {'form': form})


@login_required
def follow_user(request, username):
    """Handles following of users."""
    user_to_follow = get_object_or_404(User, username=username)
    request.user.profile.following.add(user_to_follow)
    return redirect('library:profile_view', username=username)

@login_required
def unfollow_user(request, username):
    """Handles unfollowing of users."""
    user_to_unfollow = get_object_or_404(User, username=username)
    request.user.profile.following.remove(user_to_unfollow)
    return redirect('library:profile_view', username=username)


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