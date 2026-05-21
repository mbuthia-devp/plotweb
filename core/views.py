import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from core.models import UserProfile, Story, Chapter


def index(request):
    return render(request, 'index.html')


def explore(request):
    public_stories = Story.objects.filter(is_public=True).select_related('user').prefetch_related('chapters')
    return render(request, 'explore.html', {'stories': public_stories})


def signup(request):
    if request.method == 'POST':
        first_name = (request.POST.get('firstName') or '').strip()
        second_name = (request.POST.get('secondName') or '').strip()
        contact = (request.POST.get('contact') or '').strip()
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password') or ''

        errors = []
        if not first_name:
            errors.append('First name is required')
        if not second_name:
            errors.append('Second name is required')
        if not contact:
            errors.append('Contact is required')
        if not email:
            errors.append('Email is required')
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors.append('Enter a valid email address')
        if not password or len(password) < 8:
            errors.append('Password must be at least 8 characters')

        if email and User.objects.filter(email=email).exists():
            errors.append('Email already registered')

        # If there are validation errors, return JSON for AJAX or re-render form for normal POST
        is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
        if errors:
            if is_ajax:
                return JsonResponse({'success': False, 'error': errors[0], 'errors': errors})
            else:
                context = {
                    'errors': errors,
                    'first_name': first_name,
                    'second_name': second_name,
                    'contact': contact,
                    'email': email,
                }
                return render(request, 'signup.html', context)

        # Create user and profile
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=second_name
        )

        profile = UserProfile.objects.create(
            user=user,
            first_name=first_name,
            second_name=second_name,
            contact=contact
        )

        # Save uploaded profile image if provided
        if request.FILES.get('profile_image'):
            profile.profile_image = request.FILES.get('profile_image')
            profile.save()

        login(request, user)
        if is_ajax:
            return JsonResponse({'success': True})
        return redirect('profile')

    return render(request, 'signup.html')


def log_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'error': 'Invalid credentials'})

    return render(request, 'log_in.html')


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def profile(request):
    return render(request, 'profile.html')


@login_required
def write(request):
    return render(request, 'write.html')


def admin_dashboard(request):
    return render(request, 'admin.html')


# API Endpoints for AJAX calls


@login_required
@require_http_methods(['GET'])
def get_stories(request):
    stories = Story.objects.filter(user=request.user).prefetch_related('chapters')
    data = []
    for story in stories:
        chapters = []
        for chapter in story.chapters.all():
            chapters.append({
                'id': chapter.id,
                'title': chapter.title,
                'content': chapter.content,
                'order': chapter.order,
            })
        data.append({
            'id': story.id,
            'title': story.title,
            'chapters': chapters,
            'created_at': story.created_at.isoformat(),
        })
    return JsonResponse({'stories': data})


@login_required
@require_http_methods(['POST'])
def save_story(request):
    data = json.loads(request.body)
    story_id = data.get('id')
    title = data.get('title', '')
    chapters_data = data.get('chapters', [])

    if story_id:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        story.title = title
        story.save()
    else:
        story = Story.objects.create(user=request.user, title=title, is_public=True)

    existing_chapter_ids = set()
    for i, chapter_data in enumerate(chapters_data):
        chapter_id = chapter_data.get('id')
        if chapter_id:
            try:
                chapter = Chapter.objects.get(id=chapter_id, story=story)
                chapter.title = chapter_data.get('title', '')
                chapter.content = chapter_data.get('content', '')
                chapter.order = i
                chapter.save()
                existing_chapter_ids.add(chapter_id)
            except Chapter.DoesNotExist:
                chapter = Chapter.objects.create(
                    story=story,
                    title=chapter_data.get('title', ''),
                    content=chapter_data.get('content', ''),
                    order=i,
                )
                existing_chapter_ids.add(chapter.id)
        else:
            chapter = Chapter.objects.create(
                story=story,
                title=chapter_data.get('title', ''),
                content=chapter_data.get('content', ''),
                order=i,
            )
            existing_chapter_ids.add(chapter.id)

    chapter_ids_to_delete = []
    for chapter in story.chapters.all():
        if chapter.id not in existing_chapter_ids:
            chapter_ids_to_delete.append(chapter.id)
    Chapter.objects.filter(id__in=chapter_ids_to_delete).delete()

    return JsonResponse({'success': True, 'story_id': story.id})


@login_required
@require_http_methods(['POST'])
def rename_story(request, story_id):
    data = json.loads(request.body)
    title = data.get('title', '').strip()
    story = get_object_or_404(Story, id=story_id, user=request.user)
    story.title = title
    story.save()
    return JsonResponse({'success': True, 'title': story.title})


@login_required
@require_http_methods(['DELETE'])
def delete_story(request, story_id):
    story = get_object_or_404(Story, id=story_id, user=request.user)
    story.delete()
    return JsonResponse({'success': True})


@login_required
@require_http_methods(['DELETE'])
def delete_chapter(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id, story__user=request.user)
    chapter.delete()
    return JsonResponse({'success': True})


@login_required
@require_http_methods(['POST'])
def delete_account(request):
    user = request.user
    user.delete()
    logout(request)
    return JsonResponse({'success': True})


@login_required
@require_http_methods(['GET'])
def get_stats(request):
    stories = Story.objects.filter(user=request.user)
    chapter_count = Chapter.objects.filter(story__user=request.user).count()
    word_count = 0
    for chapter in Chapter.objects.filter(story__user=request.user):
        word_count += len(chapter.content.split())

    return JsonResponse({
        'stories': stories.count(),
        'chapters': chapter_count,
        'words': word_count,
    })
