
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from core.models import UserProfile, Story, Chapter, LoginEvent

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'created_at', 'is_public']
    list_filter = ['is_public', 'created_at']
    search_fields = ['title', 'user__username']

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'story', 'order', 'created_at']
    list_filter = ['story__user', 'created_at']
    search_fields = ['title', 'content']


@admin.register(LoginEvent)
class LoginEventAdmin(admin.ModelAdmin):
    list_display = ['user', 'timestamp', 'ip_address']
    list_filter = ['timestamp']
    search_fields = ['user__username', 'user__email', 'ip_address']
    readonly_fields = ['user', 'timestamp', 'ip_address']
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False