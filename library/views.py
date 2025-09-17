from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Paper, Tag, Author, UserProfile, Comment
from .forms import PaperUploadForm, CommentForm
from django.http import HttpResponseForbidden
import PyPDF2
from django.db.models import Q, Count
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
    Handles displaying papers, including profile pages with user stats.
    """
    all_tags = Tag.objects.all().order_by('name')
    query = request.GET.get('q')
    tag_filter = request.GET.get('tag')
    context = {}

    # Base queryset is optimized to pre-fetch related data
    papers_base_qs = Paper.objects.select_related('uploader').prefetch_related('authors', 'tags')

    if query:
        papers = papers_base_qs.filter(
            Q(title__icontains=query) |
            Q(uploader__username__icontains=query) |
            Q(authors__name__icontains=query)
        ).distinct()
        view_title = f"Search Results for '{query}'"
    elif tag_filter:
        papers = papers_base_qs.filter(tags__name=tag_filter)
        view_title = f"Papers tagged with '{tag_filter}'"
    elif username:
        profile_user = get_object_or_404(User, username=username)
        papers = papers_base_qs.filter(uploader=profile_user)
        view_title = f"Papers by {profile_user.username}"
        
        # --- NEW: Calculate user stats for the profile page ---
        following_count = profile_user.profile.following.count()
        paper_count = papers.count()
        
        context.update({
            'profile_user': profile_user,
            'following_count': following_count,
            'paper_count': paper_count,
        })
    else:
        # Default view for the main homepage
        papers = papers_base_qs
        view_title = 'CiteRight'

    context.update({
        'papers': papers.order_by("-uploaded_at"),
        'view_title': view_title,
        'all_tags': all_tags,
        'selected_tag': tag_filter,
        'search_query': query
    })
    
    return render(request, 'library/paper_list.html', context)


@login_required
def paper_detail(request, pk):
    """Display details for a single paper and handle comment creation."""
    paper = get_object_or_404(Paper, pk=pk)
    comment_form = CommentForm()
    
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.paper = paper
            comment.user = request.user
            comment.save()
            return redirect('library:paper_detail', pk=paper.pk)
    
    context = {
        'paper': paper,
        'comment_form': comment_form
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
            
            if uploaded_file.name.lower().endswith('.pdf'):
                try:
                    uploaded_file.seek(0)
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    page = doc.load_page(0) 
                    pix = page.get_pixmap()
                    img_bytes = pix.tobytes("png")
                    thumbnail_file = ContentFile(img_bytes)
                    paper.thumbnail.save(f'{paper.pk}_thumbnail.png', thumbnail_file, save=True)
                    doc.close()

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
    user_to_follow = get_object_or_404(User, username=username)
    request.user.profile.following.add(user_to_follow)
    return redirect('library:profile_view', username=username)

@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    request.user.profile.following.remove(user_to_unfollow)
    return redirect('library:profile_view', username=username)


@login_required
def delete_paper(request, pk):
    paper = get_object_or_404(Paper, pk=pk)
    
    if paper.uploader != request.user:
        return HttpResponseForbidden("You are not allowed to delete this paper.")
    
    if request.method == 'POST':
        paper.delete()
        return redirect('library:profile_view', username=request.user.username)
    
    return render(request, 'library/paper_confirm_delete.html', {'paper': paper})

