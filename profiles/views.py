from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from papers.models import Paper
from django.shortcuts import render, get_object_or_404, redirect


@login_required
def profile_view(request, username):
    """
    Handles displaying a user's profile page, including their stats and uploaded papers.
    """
    profile_user = get_object_or_404(User, username=username)
    papers = Paper.objects.filter(uploader=profile_user).order_by('-uploaded_at')
    
    following_count = profile_user.profile.following.count()
    paper_count = papers.count()
    
    context = {
        'papers': papers,
        'profile_user': profile_user,
        'following_count': following_count,
        'paper_count': paper_count,
    }
    
    return render(request, 'papers/paper_list.html', context)


@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    request.user.profile.following.add(user_to_follow)
    return redirect('papers:profile_view', username=username)


@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    request.user.profile.following.remove(user_to_unfollow)
    return redirect('papers:profile_view', username=username)
