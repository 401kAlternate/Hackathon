from django.contrib import admin
from .models import UserProfile, Project, Bid, WorkSubmission

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'created_at']
    list_filter = ['role']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'offer_price', 'status', 'deadline']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['project', 'writer', 'bid_amount', 'timeline', 'status']
    list_filter = ['status']

@admin.register(WorkSubmission)
class WorkSubmissionAdmin(admin.ModelAdmin):
    list_display = ['project', 'writer', 'submitted_at', 'is_final']