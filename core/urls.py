from django.urls import path
from core import views

urlpatterns = [
    path('', views.index, name='index'),
    path('explore/', views.explore, name='explore'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.log_in, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('write/', views.write, name='write'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('api/stories/', views.get_stories, name='get_stories'),
    path('api/stories/save/', views.save_story, name='save_story'),
    path('api/stories/<int:story_id>/rename/', views.rename_story, name='rename_story'),
    path('api/stories/<int:story_id>/delete/', views.delete_story, name='delete_story'),
    path('api/chapters/<int:chapter_id>/delete/', views.delete_chapter, name='delete_chapter'),
    path('api/account/delete/', views.delete_account, name='delete_account'),
    path('api/stats/', views.get_stats, name='get_stats'),
]
