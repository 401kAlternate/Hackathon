from django.utils import timezone

def timer_context(request):
    if not request.user.is_authenticated:
        return {}
    
    from projects.models import Project
    
    # Find active bidding timer
    bidding_projects = Project.objects.filter(status__in=['open', 'bidding'], deadline__gte=timezone.now()).order_by('deadline')[:1]
    
    active_bidding_timer = None
    if bidding_projects:
        project = bidding_projects[0]
        remaining = project.time_remaining
        if remaining > 0:
            deadline_ts = int(project.deadline.timestamp() * 1000)
            from projects.views import format_time
            active_bidding_timer = (remaining, deadline_ts, format_time(remaining))
    
    # Find active writing timer
    active_writing_timer = None
    if hasattr(request.user, 'profile') and request.user.profile.role == 'writer':
        writing_projects = Project.objects.filter(winner=request.user, status='in_progress', writing_deadline__gte=timezone.now()).order_by('writing_deadline')[:1]
        
        if writing_projects:
            project = writing_projects[0]
            remaining = project.writing_time_remaining
            if remaining > 0:
                deadline_ts = int(project.writing_deadline.timestamp() * 1000)
                from projects.views import format_time
                active_writing_timer = (remaining, deadline_ts, format_time(remaining))
    
    return {'active_bidding_timer': active_bidding_timer, 'active_writing_timer': active_writing_timer}