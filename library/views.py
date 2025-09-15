from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Paper
from .forms import PaperUploadForm, NoteForm
import PyPDF2

@login_required
def paper_list_view(request, username=None):
    """
    This single view handles both the universal paper list and user-specific profile pages.
    - If a username is provided, it filters for that user's papers.
    - Otherwise, it displays all papers.
    """
    if username:
        # This is a user's profile view
        user = get_object_or_404(User, username=username)
        papers = Paper.objects.filter(uploader=user).order_by('-uploaded_at')
        view_title = f"{user.username}'s Papers"
    else:
        # This is the universal, all-papers view
        papers = Paper.objects.all().order_by('-uploaded_at')
        view_title = 'All Papers'

    context = {'papers': papers, 'view_title': view_title}
    return render(request, 'library/paper_list.html', context)

@login_required
def paper_detail(request, pk):
    """
    Displays the details for a single paper.
    Only the user who uploaded the paper can add notes.
    """
    paper = get_object_or_404(Paper, pk=pk)
    noteform = NoteForm()
    
    # Check if the current user is the one who uploaded the paper before processing the form
    if request.method == "POST" and paper.uploader == request.user:
        noteform = NoteForm(request.POST)
        if noteform.is_valid():
            note = noteform.save(commit=False)
            note.paper = paper
            note.save()
            return redirect('paper_detail', pk=paper.pk)
    
    context = {
        'paper': paper,
        'noteform': noteform
    }
    
    return render(request, 'library/paper_detail.html', context)

@login_required
def upload_paper(request):
    """Handle the paper upload process."""
    if request.method == 'POST':
        form = PaperUploadForm(request.POST, request.FILES)
        if form.is_valid():
            paper = form.save(commit=False)
            # Set the uploader to the currently logged-in user
            paper.uploader = request.user
            
            try:
                pdf_reader = PyPDF2.PdfReader(request.FILES['pdf_file'])
                metadata = pdf_reader.metadata
                if not paper.title and metadata and metadata.title:
                    paper.title = metadata.title
            except Exception as e:
                print(f"Could not extract metadata: {e}")
                if not paper.title:
                    paper.title = "Untitled Paper"

            paper.save()
            # Redirect to the main paper list after a successful upload
            return redirect('paper_list')
    else:
        form = PaperUploadForm()
    return render(request, 'library/paper_upload.html', {'form': form})

