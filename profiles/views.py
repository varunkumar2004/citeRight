from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from papers.models import Paper, Tag

@login_required
def profile_view(request, username):
    """
    Handles displaying a user's profile page, including their stats,
    uploaded papers, and (privately) their bookmarked papers in tabs.
    Only the selected tab's content is fetched and rendered.
    """
    profile_user = get_object_or_404(User, username=username)
    
    tab = request.GET.get("tab", "uploaded")
    uploaded_papers = None
    bookmarked_papers = None

    if tab == "uploaded":
        uploaded_papers = Paper.objects.filter(uploader=profile_user).order_by("-uploaded_at")

    elif tab == "bookmarked" and request.user == profile_user:
        bookmarked_papers = request.user.bookmarked_papers.all().order_by("-uploaded_at")

    following_count = profile_user.profile.following.count()
    paper_count = (
        Paper.objects.filter(uploader=profile_user).count()
    )

    context = {
        "tab": tab,
        "papers": uploaded_papers,
        "bookmarked_papers": bookmarked_papers,
        "profile_user": profile_user,
        "following_count": following_count,
        "paper_count": paper_count
    }

    return render(request, "papers/paper_list.html", context)


@login_required
def follow_user(request, username):
    """Handles the logic for following a user."""
    user_to_follow = get_object_or_404(User, username=username)
    request.user.profile.following.add(user_to_follow)
    return redirect("profiles:profile_view", username=username)


@login_required
def unfollow_user(request, username):
    """Handles the logic for unfollowing a user."""
    user_to_unfollow = get_object_or_404(User, username=username)
    request.user.profile.following.remove(user_to_unfollow)
    return redirect("profiles:profile_view", username=username)
