from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Student URLs
    path('students/', views.students_view, name='students'),
    path('add-student/', views.add_student, name='add_student'),
    path('edit-student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('search-students/', views.search_students, name='search_students'),
    path('filter-students/<str:filter_type>/', views.filter_students, name='filter_students'),
    
    # Staff URLs
    path('staff/', views.staff_view, name='staff'),
    path('add-staff/', views.add_staff, name='add_staff'),
    path('edit-staff/<int:staff_id>/', views.edit_staff, name='edit_staff'),
    path('delete-staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('search-staff/', views.search_staff, name='search_staff'),
    path('filter-staff/<str:filter_type>/', views.filter_staff, name='filter_staff'),
    
    # Grade URLs
    path('grades/', views.grades_view, name='grades'),
    path('add-grade/', views.add_grade, name='add_grade'),
    path('edit-grade/<int:grade_id>/', views.edit_grade, name='edit_grade'),
    path('delete-grade/<int:grade_id>/', views.delete_grade, name='delete_grade'),
    path('grade-details/<int:grade_id>/', views.grade_details, name='grade_details'),
    
    # Finance URLs
    path('finance/', views.finance_view, name='finance'),
    path('update-fees/<int:student_id>/', views.update_fees, name='update_fees'),
    
    # Event URLs
    path('events/', views.events_view, name='events'),
    path('add-event/', views.add_event, name='add_event'),
    path('edit-event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('add-activity/', views.add_activity, name='add_activity'),
    path('edit-activity/<int:activity_id>/', views.edit_activity, name='edit_activity'),
    path('delete-activity/<int:activity_id>/', views.delete_activity, name='delete_activity'),
    
    # Notification URLs
    path('notifications/', views.notifications_view, name='notifications'),
    path('add-notification/', views.add_notification, name='add_notification'),
    path('delete-notification/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    
    # API URLs
    path('api/dashboard-stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
    path('api/students/', views.students_filter_api, name='students_filter_api'),
    path('api/staff/', views.staff_filter_api, name='staff_filter_api'),
]
