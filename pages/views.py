# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from .models import Student, Staff, Grade, Notification, Event, Activity
from datetime import datetime, date

def dashboard(request):
    # Calculate statistics
    total_students = Student.objects.count()
    total_staff = Staff.objects.count()
    total_grades = Grade.objects.count()
    
    # Calculate fees
    students_with_balance = Student.objects.all()
    outstanding_fees = sum(s.balance() for s in students_with_balance if s.balance() > 0)
    total_fees_due = sum(s.fees_due for s in students_with_balance)
    total_fees_paid = sum(s.fees_paid for s in students_with_balance)

    # Recent notifications and events
    recent_notifications = Notification.objects.order_by('-date')[:5]
    upcoming_events = Event.objects.all()[:5]  # You might want to add date filtering

    # Collection percentage
    collection_percentage = (total_fees_paid / total_fees_due * 100) if total_fees_due > 0 else 0
    
    
    # Get all grades for the form dropdown
    grades = Grade.objects.all()
    
    context = {
        'total_students': total_students,
        'total_staff': total_staff,
        'total_grades': total_grades,
        'outstanding_fees': outstanding_fees,
        'total_fees_due': total_fees_due,
        'total_fees_paid': total_fees_paid,
        'recent_notifications': recent_notifications,
        'upcoming_events': upcoming_events,
        'new_notifications': recent_notifications.count(),
        'collection_percentage': collection_percentage,
        
        # Add these for the forms and tables
        'students': Student.objects.select_related('grade').all()[:10],  # Show first 10
        'staff': Staff.objects.all()[:10],  # Show first 10
        'grades': grades,
        'grade_stats': [],  # You already have this logic
        'events': Event.objects.all()[:5],
        'activities': Activity.objects.all()[:5],
        'notifications': recent_notifications,
        
        # URL names for the template
        'add_student_url': '/add-student/',
        'add_staff_url': '/add-staff/',
        'add_grade_url': '/add-grade/',
        'add_event_url': '/add-event/',
        'add_activity_url': '/add-activity/',
        'add_notification_url': '/add-notification/',
        'students_url': '/students/',
        'staff_url': '/staff/',
        'search_students_url': '/search-students/',
        'search_staff_url': '/search-staff/',
        'filter_students_url': '/filter-students',
        'filter_staff_url': '/filter-staff',
        'edit_student_url': '/edit-student',
        'delete_student_url': '/delete-student',
        'edit_staff_url': '/edit-staff',
        'delete_staff_url': '/delete-staff',
        'edit_grade_url': '/edit-grade',
        'delete_grade_url': '/delete-grade',
        'grade_details_url': '/grade-details',
        'edit_event_url': '/edit-event',
        'delete_event_url': '/delete-event',
        'edit_activity_url': '/edit-activity',
        'delete_activity_url': '/delete-activity',
        'delete_notification_url': '/delete-notification',
    }
    return render(request, 'dashboard.html', context)
    

# ============= STUDENT VIEWS =============
def students_view(request):
    students = Student.objects.select_related('grade').all()
    grades = Grade.objects.all()
    
    context = {
        'students': students,
        'grades': grades,
    }
    return render(request, 'students.html', context)

def add_student(request):
    if request.method == 'POST':
        try:
            # Ensure grade exists before creating student
            grade = get_object_or_404(Grade, id=request.POST['grade'])
            student = Student.objects.create(
                name=request.POST['name'],
                grade=grade,
                date_of_birth=request.POST.get('date_of_birth') or None,
                fees_due=float(request.POST.get('fees_due', 0)),
                fees_paid=float(request.POST.get('fees_paid', 0))
            )
            print(f"DEBUG: Created student {student.id} - {student.name}")  # Debug line
            messages.success(request, 'Student added successfully!')
        except Exception as e:
            print(f"DEBUG: Error creating student: {str(e)}")  # Debug line
            messages.error(request, f'Error adding student: {str(e)}')
        
        return redirect('students')

def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        try:
            student.name = request.POST['name']
            student.grade = get_object_or_404(Grade, id=request.POST['grade'])
            student.date_of_birth = request.POST.get('date_of_birth') or None
            student.fees_due = float(request.POST.get('fees_due', 0))
            student.fees_paid = float(request.POST.get('fees_paid', 0))
            student.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('students')
        except Exception as e:
            messages.error(request, f'Error updating student: {str(e)}')
    
    grades = Grade.objects.all()
    context = {'student': student, 'grades': grades}
    return render(request, 'edit_student.html', context)

def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully!')
    return redirect('students')

def search_students(request):
    query = request.GET.get('q', '')
    students = Student.objects.select_related('grade')
    
    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(grade__name__icontains=query)
        )
    
    return render(request, 'students.html', {'students': students, 'search_query': query})

def filter_students(request, filter_type):
    students = Student.objects.select_related('grade')
    
    if filter_type == 'outstanding':
        students = [s for s in students if s.balance() > 0]
    elif filter_type == 'paid':
        students = [s for s in students if s.balance() <= 0]
    elif filter_type == 'recent':
        students = students.order_by('-enrolled_on')[:10]
    
    return render(request, 'students.html', {'students': students, 'filter_type': filter_type})

# ============= STAFF VIEWS =============
def staff_view(request):
    staff = Staff.objects.all()
    return render(request, 'staff.html', {'staff': staff})

def add_staff(request):
    if request.method == 'POST':
        try:
            Staff.objects.create(
                name=request.POST['name'],
                role=request.POST['role'],
                date_joined=request.POST.get('date_joined') or date.today()
            )
            messages.success(request, 'Staff member added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding staff: {str(e)}')
        
        return redirect('staff')
    
    return render(request, 'add_staff.html', {'role_choices': Staff.ROLE_CHOICES})

def edit_staff(request, staff_id):
    staff_member = get_object_or_404(Staff, id=staff_id)
    
    if request.method == 'POST':
        try:
            staff_member.name = request.POST['name']
            staff_member.role = request.POST['role']
            staff_member.date_joined = request.POST.get('date_joined') or staff_member.date_joined
            staff_member.save()
            messages.success(request, 'Staff member updated successfully!')
            return redirect('staff')
        except Exception as e:
            messages.error(request, f'Error updating staff: {str(e)}')
    
    context = {'staff_member': staff_member, 'role_choices': Staff.ROLE_CHOICES}
    return render(request, 'edit_staff.html', context)

def delete_staff(request, staff_id):
    staff_member = get_object_or_404(Staff, id=staff_id)
    if request.method == 'POST':
        staff_member.delete()
        messages.success(request, 'Staff member deleted successfully!')
    return redirect('staff')

def search_staff(request):
    query = request.GET.get('q', '')
    staff = Staff.objects.all()
    
    if query:
        staff = staff.filter(
            Q(name__icontains=query) |
            Q(role__icontains=query)
        )
    
    return render(request, 'staff.html', {'staff': staff, 'search_query': query})

def filter_staff(request, filter_type):
    staff = Staff.objects.all()
    
    if filter_type == 'teachers':
        staff = staff.filter(role='Teacher')
    elif filter_type == 'admin':
        staff = staff.filter(role='Admin')
    elif filter_type == 'support':
        staff = staff.filter(role='Support')
    
    return render(request, 'staff.html', {'staff': staff, 'filter_type': filter_type})

# ============= GRADE VIEWS =============
def grades_view(request):
    grades = Grade.objects.all()
    grade_stats = []
    
    for grade in grades:
        student_count = grade.student_set.count()
        grade_stats.append({
            'grade': grade,
            'student_count': student_count,
            'teacher_count': Staff.objects.filter(role='Teacher').count()  # You might want to add a grade-teacher relationship
        })
    
    return render(request, 'grades.html', {'grade_stats': grade_stats})

def add_grade(request):
    if request.method == 'POST':
        try:
            Grade.objects.create(name=request.POST['name'])
            messages.success(request, 'Grade added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding grade: {str(e)}')
        
        return redirect('grades')
    
    return render(request, 'add_grade.html')

def edit_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    
    if request.method == 'POST':
        try:
            grade.name = request.POST['name']
            grade.save()
            messages.success(request, 'Grade updated successfully!')
            return redirect('grades')
        except Exception as e:
            messages.error(request, f'Error updating grade: {str(e)}')
    
    return render(request, 'edit_grade.html', {'grade': grade})

def delete_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    if request.method == 'POST':
        grade.delete()
        messages.success(request, 'Grade deleted successfully!')
    return redirect('grades')

def grade_details(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    students = grade.student_set.all()
    return render(request, 'grade_details.html', {'grade': grade, 'students': students})

# ============= FINANCE VIEWS =============
def finance_view(request):
    students = Student.objects.all()
    
    total_fees_due = sum(s.fees_due for s in students)
    total_fees_paid = sum(s.fees_paid for s in students)
    outstanding_fees = sum(s.balance() for s in students if s.balance() > 0)
    
    # Outstanding fees by grade
    grade_stats = {}
    for student in students:
        if student.balance() > 0:
            grade_name = student.grade.name
            if grade_name not in grade_stats:
                grade_stats[grade_name] = 0
            grade_stats[grade_name] += student.balance()
    
    context = {
        'total_fees_due': total_fees_due,
        'total_fees_paid': total_fees_paid,
        'outstanding_fees': outstanding_fees,
        'grade_stats': grade_stats,
        'collection_rate': (total_fees_paid / total_fees_due * 100) if total_fees_due > 0 else 0
    }
    return render(request, 'finance.html', context)

def update_fees(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        try:
            student.fees_due = float(request.POST.get('fees_due', student.fees_due))
            student.fees_paid = float(request.POST.get('fees_paid', student.fees_paid))
            student.save()
            messages.success(request, 'Fees updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating fees: {str(e)}')
        
        return redirect('finance')
    
    return render(request, 'update_fees.html', {'student': student})

# ============= EVENT VIEWS =============
def events_view(request):
    events = Event.objects.all()
    activities = Activity.objects.all()
    return render(request, 'events.html', {'events': events, 'activities': activities})

def add_event(request):
    if request.method == 'POST':
        try:
            Event.objects.create(title=request.POST['title'])
            messages.success(request, 'Event added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding event: {str(e)}')
        
        return redirect('events')
    
    return render(request, 'add_event.html')

def add_activity(request):
    if request.method == 'POST':
        try:
            Activity.objects.create(title=request.POST['title'])
            messages.success(request, 'Activity added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding activity: {str(e)}')
        
        return redirect('events')
    
    return render(request, 'add_activity.html')

# ============= NOTIFICATION VIEWS =============
def notifications_view(request):
    notifications = Notification.objects.order_by('-date')
    return render(request, 'notifications.html', {'notifications': notifications})

def add_notification(request):
    if request.method == 'POST':
        try:
            Notification.objects.create(
                message=request.POST['message'],
                date=date.today()
            )
            messages.success(request, 'Notification sent successfully!')
        except Exception as e:
            messages.error(request, f'Error sending notification: {str(e)}')
        
        return redirect('notifications')
    
    return render(request, 'add_notification.html')

def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    if request.method == 'POST':
        notification.delete()
        messages.success(request, 'Notification deleted successfully!')
    return redirect('notifications')

# ============= API ENDPOINTS (for AJAX) =============
def dashboard_stats_api(request):
    """API endpoint for real-time dashboard updates"""
    data = {
        'total_students': Student.objects.count(),
        'total_staff': Staff.objects.count(),
        'total_grades': Grade.objects.count(),
        'outstanding_fees': sum(s.balance() for s in Student.objects.all() if s.balance() > 0),
        'new_notifications': Notification.objects.count(),
    }
    return JsonResponse(data)

def students_filter_api(request):
    """API endpoint for filtering students"""
    filter_type = request.GET.get('filter', 'all')
    students = Student.objects.select_related('grade').all()
    
    if filter_type == 'outstanding':
        students = [s for s in students if s.balance() > 0]
    elif filter_type == 'paid':
        students = [s for s in students if s.balance() <= 0]
    
    data = [{
        'id': s.id,
        'name': s.name,
        'grade': s.grade.name,
        'balance': s.balance(),
        'status': 'outstanding' if s.balance() > 0 else 'paid'
    } for s in students]
    
    return JsonResponse({'students': data})
# Add these missing view functions to your views.py file

def payment_history(request, student_id):
    """View payment history for a specific student"""
    student = get_object_or_404(Student, id=student_id)
    
    # If you have the FeePayment model from the enhanced models
    try:
        from .models import FeePayment
        payments = FeePayment.objects.filter(student=student).order_by('-payment_date')
    except ImportError:
        # Fallback if FeePayment model doesn't exist yet
        payments = []
    
    context = {
        'student': student,
        'payments': payments,
        'total_paid': student.fees_paid,
        'balance': student.balance(),
    }
    return render(request, 'payment_history.html', context)

def edit_event(request, event_id):
    """Edit an existing event"""
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        try:
            event.title = request.POST['title']
            # Add more fields as needed based on your Event model
            event.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('events')
        except Exception as e:
            messages.error(request, f'Error updating event: {str(e)}')
    
    return render(request, 'edit_event.html', {'event': event})

def delete_event(request, event_id):
    """Delete an event"""
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
    return redirect('events')

def edit_activity(request, activity_id):
    """Edit an existing activity"""
    activity = get_object_or_404(Activity, id=activity_id)
    
    if request.method == 'POST':
        try:
            activity.title = request.POST['title']
            # Add more fields as needed based on your Activity model
            activity.save()
            messages.success(request, 'Activity updated successfully!')
            return redirect('events')  # or wherever you want to redirect
        except Exception as e:
            messages.error(request, f'Error updating activity: {str(e)}')
    
    return render(request, 'edit_activity.html', {'activity': activity})

def delete_activity(request, activity_id):
    """Delete an activity"""
    activity = get_object_or_404(Activity, id=activity_id)
    if request.method == 'POST':
        activity.delete()
        messages.success(request, 'Activity deleted successfully!')
    return redirect('events')

def activities_view(request):
    """View all activities"""
    activities = Activity.objects.all()
    return render(request, 'activities.html', {'activities': activities})

def staff_filter_api(request):
    """API endpoint for filtering staff"""
    filter_type = request.GET.get('filter', 'all')
    staff = Staff.objects.all()
    
    if filter_type == 'teachers':
        staff = staff.filter(role='Teacher')
    elif filter_type == 'admin':
        staff = staff.filter(role='Admin')
    elif filter_type == 'support':
        staff = staff.filter(role='Support')
    
    data = [{
        'id': s.id,
        'name': s.name,
        'role': s.role,
        'date_joined': s.date_joined.strftime('%Y-%m-%d'),
        'status': getattr(s, 'status', 'Active')  # Use getattr in case status field doesn't exist yet
    } for s in staff]
    
    return JsonResponse({'staff': data})