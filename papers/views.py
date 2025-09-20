from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from .models import Paper, Tag, Author, Comment
from .forms import PaperUploadForm, CommentForm
# from ai_processing.tasks import generate_article_task
from django.db.models import Q
import PyPDF2
import fitz
from django.core.files.base import ContentFile
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
import re
from nltk.corpus import stopwords

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


@login_required
def paper_list_view(request):
    """
    Handles displaying the main homepage, search results, and tag-filtered results.
    """
    papers = Paper.objects.select_related('uploader').prefetch_related('authors', 'tags')
    all_tags = Tag.objects.all().order_by('name')
    query = request.GET.get('q')
    tag_filter = request.GET.get('tag')
    
    if query:
        papers = papers.filter(
            Q(title__icontains=query) |
            Q(authors__name__icontains=query) |
            Q(uploader__username__icontains=query)
        ).distinct()
        view_title = f"Search Results for '{query}'"
    elif tag_filter:
        papers = papers.filter(tags__name=tag_filter)
        view_title = f"Papers tagged with '{tag_filter}'"
    else:
        view_title = 'CiteRight'

    context = {
        'papers': papers.order_by("-uploaded_at"),
        'view_title': view_title,
        'all_tags': all_tags,
        'selected_tag': tag_filter,
        'search_query': query,
    }
    return render(request, 'papers/paper_list.html', context)


@login_required
def paper_detail(request, pk):
    """Displays a single paper and handles its comment section."""
    paper = get_object_or_404(Paper, pk=pk)
    comment_form = CommentForm()
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.paper = paper
            comment.user = request.user
            comment.save()
            return redirect('papers:paper_detail', pk=paper.pk)
    context = {'paper': paper, 'comment_form': comment_form}
    return render(request, 'papers/paper_detail.html', context)


@login_required
def upload_paper(request):
    """Handles the form for uploading a new paper."""
    if request.method == 'POST':
        form = PaperUploadForm(request.POST, request.FILES)
        if form.is_valid():
            paper = form.save(commit=False)
            paper.uploader = request.user
            paper.abstract = "Generating AI article, please check back in a moment..."
            paper.save()

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
            
            # Trigger background task for AI processing
            # generate_article_task.delay(paper.id)

            return redirect('papers:paper_list')
    else:
        form = PaperUploadForm()
    return render(request, 'papers/paper_upload.html', {'form': form})


@login_required
def edit_abstract_view(request, pk):
    """Allows the uploader to edit the AI-generated abstract."""
    paper = get_object_or_404(Paper, pk=pk)
    if paper.uploader != request.user:
        return HttpResponseForbidden("You are not allowed to edit this abstract.")
    if request.method == 'POST':
        paper.abstract = request.POST.get('abstract')
        paper.save()
        return redirect('papers:paper_detail', pk=paper.pk)
    return render(request, 'papers/edit_abstract.html', {'paper': paper})


@login_required
def delete_paper(request, pk):
    """Handles the deletion of a paper."""
    paper = get_object_or_404(Paper, pk=pk)
    if paper.uploader != request.user:
        return HttpResponseForbidden("You are not allowed to delete this paper.")
    if request.method == 'POST':
        paper.delete()
        return redirect('profiles:profile_view', username=request.user.username)
    return render(request, 'papers/paper_confirm_delete.html', {'paper': paper})


@login_required
def bookmarked_papers_view(request):
    """Displays a list of papers the user has bookmarked."""
    bookmarked_papers = request.user.bookmarked_papers.all().order_by('-uploaded_at')
    context = {
        'papers': bookmarked_papers,
        'view_title': 'My Bookmarks',
        'all_tags': Tag.objects.all().order_by('name'), # For the sidebar
    }
    return render(request, 'papers/paper_list.html', context)


@login_required
def toggle_bookmark_view(request, pk):
    """Adds or removes a paper from the user's bookmarks."""
    paper = get_object_or_404(Paper, pk=pk)
    if paper in request.user.bookmarked_papers.all():
        request.user.bookmarked_papers.remove(paper)
    else:
        request.user.bookmarked_papers.add(paper)
    return redirect(request.META.get('HTTP_REFERER', 'papers:paper_list'))

