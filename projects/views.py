from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from .models import UserProfile, Project, Bid, WorkSubmission


def format_time(seconds):
    if seconds <= 0:
        return '00:00:00'
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f'{hours:02d}:{minutes:02d}:{secs:02d}'


def home(request):
    open_projects = Project.objects.filter(status__in=['open', 'bidding']).order_by('-created_at')[:6]
    return render(request, 'home.html', {'open_projects': open_projects})


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role', 'writer')
        
        if password1 != password2:
            messages.error(request, "Passwords don't match")
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')
        
        user = User.objects.create_user(username=username, email=email, password=password1)
        UserProfile.objects.create(user=user, role=role)
        login(request, user)
        messages.success(request, f"Welcome! You are registered as a {role}.")
        return redirect('dashboard')
    
    return render(request, 'register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


@login_required
def dashboard(request):
    profile = request.user.profile
    
    if profile.role == 'client':
        my_projects = Project.objects.filter(client=request.user).order_by('-created_at')
        return render(request, 'dashboard.html', {'projects': my_projects, 'role': 'client'})
    else:
        my_bids = Bid.objects.filter(writer=request.user).order_by('-created_at')
        won_projects = Project.objects.filter(winner=request.user, status='in_progress')
        return render(request, 'dashboard.html', {'bids': my_bids, 'won_projects': won_projects, 'role': 'writer'})


@login_required
def create_project(request):
    profile = request.user.profile
    if profile.role != 'client':
        messages.error(request, "Only clients can create projects")
        return redirect('dashboard')
    
    if request.method == 'POST':
        from django.utils.dateparse import parse_datetime
        title = request.POST.get('title')
        requirements = request.POST.get('requirements')
        description = request.POST.get('description')
        deadline = request.POST.get('deadline')
        offer_price = request.POST.get('offer_price')
        
        deadline_dt = parse_datetime(deadline) if deadline else None
        
        Project.objects.create(
            client=request.user,
            title=title,
            requirements=requirements,
            description=description,
            deadline=deadline_dt,
            offer_price=offer_price,
        )
        
        messages.success(request, "Project posted successfully!")
        return redirect('dashboard')
    
    return render(request, 'create_project.html')


@login_required
def project_list(request):
    projects = Project.objects.filter(status__in=['open', 'bidding']).filter(deadline__gte=timezone.now()).order_by('-created_at')
    return render(request, 'project_list.html', {'projects': projects})


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    is_client = project.client == request.user
    user_bid = None
    
    if not is_client:
        user_bid = Bid.objects.filter(project=project, writer=request.user).first()
    
    return render(request, 'project_detail.html', {'project': project, 'is_client': is_client, 'user_bid': user_bid})


@login_required
def submit_bid(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if not project.is_bidding_open:
        messages.error(request, "Bidding is closed for this project")
        return redirect('project_detail', project_id=project_id)
    
    if request.method == 'POST':
        bid_amount = request.POST.get('bid_amount')
        proposal = request.POST.get('proposal')
        timeline = request.POST.get('timeline')
        
        bid, created = Bid.objects.update_or_create(
            project=project,
            writer=request.user,
            defaults={'bid_amount': bid_amount, 'proposal': proposal, 'timeline': timeline}
        )
        
        messages.success(request, "Bid submitted successfully!")
        return redirect('project_detail', project_id=project_id)
    
    return redirect('project_detail', project_id=project_id)


@login_required
def view_bids(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if project.client != request.user:
        messages.error(request, "You can only view bids for your own projects")
        return redirect('dashboard')
    
    bids = Bid.objects.filter(project=project).order_by('-created_at')
    return render(request, 'view_bids.html', {'project': project, 'bids': bids})


@login_required
def select_winner(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if project.client != request.user:
        messages.error(request, "You can only select winners for your own projects")
        return redirect('dashboard')
    
    if request.method == 'POST':
        bid_id = request.POST.get('bid_id')
        bid = get_object_or_404(Bid, id=bid_id, project=project)
        writing_days = int(request.POST.get('writing_days', 7))
        
        project.winner = bid.writer
        project.status = 'in_progress'
        project.writing_deadline = timezone.now() + timezone.timedelta(days=writing_days)
        project.save()
        
        bid.status = 'accepted'
        bid.save()
        
        Bid.objects.filter(project=project).exclude(id=bid.id).update(status='rejected')
        
        messages.success(request, f"Selected {bid.writer.username} as winner!")
        return redirect('dashboard')
    
    return redirect('view_bids', project_id=project_id)


@login_required
def submit_work(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if project.winner != request.user:
        messages.error(request, "Only the selected writer can submit work")
        return redirect('dashboard')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        WorkSubmission.objects.create(project=project, writer=request.user, content=content, is_final=True)
        
        project.status = 'completed'
        project.save()
        
        messages.success(request, "Work submitted successfully!")
        return redirect('dashboard')
    
    return render(request, 'submit_work.html', {'project': project})


@login_required
def my_bids(request):
    bids = Bid.objects.filter(writer=request.user).order_by('-created_at')
    return render(request, 'my_bids.html', {'bids': bids})