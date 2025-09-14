from django.shortcuts import render, get_object_or_404, redirect
from .models import Paper
from .forms import NoteForm, PaperUploadForm
from django.contrib.auth.decorators import login_required

@login_required
def paper_list(request):
    papers = Paper.objects.filter(user=request.user).order_by('-uploaded_at')
    context = {'papers': papers}
    return render(request, 'library/paper_list.html', context)

@login_required
def paper_detail(request, pk):
    paper = get_object_or_404(Paper, pk=pk, user=request.user)
    noteform = NoteForm()
    
    if request.method == "POST":
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
    if request.method == "POST":
        form = PaperUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            paper = form.save(commit=False)    
            paper.user = request.user
            
            # try:
            #     pdf_reader = 
            
            paper.save()
            return redirect('paper_list')
    else:
        form = PaperUploadForm()
    context = {'form': form}
    return render(request, 'library/paper_upload.html', context)