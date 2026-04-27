from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    ROLE_CHOICES = [('client', 'Client'), ('writer', 'Writer')]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='writer')
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Project(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open for Bidding'),
        ('bidding', 'Bidding in Progress'),
        ('awarded', 'Awarded to Writer'),
        ('in_progress', 'Work in Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_projects')
    title = models.CharField(max_length=200)
    requirements = models.TextField()
    description = models.TextField()
    deadline = models.DateTimeField()
    offer_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_projects')
    writing_deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_bidding_open(self):
        return timezone.now() < self.deadline and self.status in ['open', 'bidding']
    
    @property
    def time_remaining(self):
        if self.is_bidding_open:
            delta = self.deadline - timezone.now()
            return delta.total_seconds()
        return 0
    
    @property
    def writing_time_remaining(self):
        if self.status == 'in_progress' and self.writing_deadline:
            delta = self.writing_deadline - timezone.now()
            return max(0, delta.total_seconds())
        return 0


class Bid(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bids')
    writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    proposal = models.TextField()
    timeline = models.IntegerField(default=7)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['project', 'writer']
    
    def __str__(self):
        return f"{self.writer.username} - {self.project.title} - ${self.bid_amount}"


class WorkSubmission(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='submissions')
    writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    content = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_final = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.writer.username} - {self.project.title}"