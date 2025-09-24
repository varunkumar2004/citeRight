from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Paper, Author, Comment, Tag
from .forms import PaperUploadForm, CommentForm
from ai_processing.tasks import generate_article_task
from django.db.models import Q
import fitz
from django.core.files.base import ContentFile


@login_required
def paper_list_view(request, username=None):
    """
    Handles displaying papers for the homepage (with tabs), profiles, and search/filter results.
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
        context['papers'] = papers.order_by("-uploaded_at")
    elif tag_filter:
        papers = papers_base_qs.filter(tags__name=tag_filter)
        view_title = f"Papers tagged with '{tag_filter}'"
        context['papers'] = papers.order_by("-uploaded_at")
    elif username:
        profile_user = get_object_or_404(User, username=username)
        papers = papers_base_qs.filter(uploader=profile_user)
        view_title = f"Papers by {profile_user.username}"
        context.update({
            'papers': papers.order_by("-uploaded_at"),
            'profile_user': profile_user
        })
    else:
        # This is the default homepage view, now with data for two tabs
        view_title = 'CiteRight'
        all_papers = papers_base_qs.order_by("-uploaded_at")
        followed_users = request.user.profile.following.all()
        feed_papers = papers_base_qs.filter(uploader__in=followed_users).order_by('-uploaded_at')
        context.update({
            'all_papers': all_papers,
            'feed_papers': feed_papers,
            'is_home_view': True
        })

    context.update({
        'view_title': view_title,
        'all_tags': all_tags,
        'selected_tag': tag_filter,
        'search_query': query
    })
    
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
    """
    Handles paper uploads, now delegating all AI processing to the background task.
    """
    if request.method == 'POST':
        form = PaperUploadForm(request.POST, request.FILES)
        if form.is_valid():
            paper = form.save(commit=False)
            paper.uploader = request.user
            
            choice = form.cleaned_data.get('article_choice')
            if choice == 'ai':
                paper.article_content = "Generating AI article & tags, please check back..."
            else:
                paper.article_content = form.cleaned_data.get('user_article')
            
            paper.save()
            
            if choice == 'ai':
                generate_article_task.delay(paper.id)

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
            
            # Thumbnail generation logic remains
            uploaded_file = form.cleaned_data.get('pdf_file')
            if uploaded_file and uploaded_file.name.lower().endswith('.pdf'):
                try:
                    uploaded_file.seek(0)
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    page = doc.load_page(0)
                    pix = page.get_pixmap()
                    img_bytes = pix.tobytes("png")
                    thumbnail_file = ContentFile(img_bytes)
                    paper.thumbnail.save(f'{paper.pk}_thumbnail.png', thumbnail_file, save=True)
                    doc.close()
                except Exception as e:
                    print(f"Error generating thumbnail: {e}")

            return redirect('papers:paper_list')
    else:
        form = PaperUploadForm()
    return render(request, 'papers/paper_upload.html', {'form': form})


@login_required
def edit_abstract_view(request, pk):
    """Allows the uploader to edit the paper's article content."""
    paper = get_object_or_404(Paper, pk=pk)
    if paper.uploader != request.user:
        return HttpResponseForbidden("You are not allowed to edit this article.")
    if request.method == 'POST':
        paper.article_content = request.POST.get('abstract')
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

