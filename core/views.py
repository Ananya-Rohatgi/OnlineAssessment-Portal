from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Student, Question, UserResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache

# Sign Up View
def signup_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        roll_number = request.POST.get('roll_number')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        if Student.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect('/')
        if Student.objects.filter(roll_number=roll_number).exists():
            messages.error(request, "This roll number is already registered.")
            return redirect('/')

        student = Student.objects.create(
            name=name,
            roll_number=roll_number,
            email=email,
            phone=phone
        )
        request.session['user_id'] = student.id
        request.session['test_start_time'] = timezone.now().timestamp()  # Store test start time
        return redirect('/rules/')

    return render(request, "signup.html")

# Rules View
def rules_view(request):
    if request.method == 'POST' and request.POST.get('agree') == 'on':
        return redirect('/assessment/?q=1')
    return render(request, 'rules.html')

# Assessment View (One question at a time)
@never_cache
def assessment_view(request):
    student_id = request.session.get('user_id')
    if not student_id:
        messages.error(request, "Please sign up first.")
        return redirect('/')

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        messages.error(request, "Invalid session.")
        return redirect('/')

    questions = list(Question.objects.all()[:5])
    total_questions = len(questions)

    current_index = int(request.GET.get('q', '1'))
    if current_index < 1:
        current_index = 1
    if current_index > total_questions:
        return redirect('/review/')

    current_question = questions[current_index - 1]
    responses = UserResponse.objects.filter(user=student)
    answered_question_ids = responses.values_list('question_id', flat=True)

    # Calculate remaining time
    if 'test_start_time' in request.session:
        elapsed = timezone.now().timestamp() - request.session['test_start_time']
        remaining = max(0, 3600 - int(elapsed))  # 60 minutes test duration
        minutes = remaining // 60
        seconds = remaining % 60
        remaining_time = f"{minutes:02d}:{seconds:02d}"
    else:
        remaining_time = "60:00"

    context = {
        'student': student,
        'questions': questions,
        'current_question': current_question,
        'current_question_index': current_index,
        'answered_question_ids': list(answered_question_ids),
        'remaining_time': remaining_time,
    }
    return render(request, 'assessment.html', context)
@never_cache
def submit_view(request):
    student_id = request.session.get('user_id')
    if not student_id:
        messages.error(request, "Session expired.")
        return redirect('/')

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        messages.error(request, "Student not found.")
        return redirect('/')

    question_id = request.POST.get("question_id")
    if not question_id:
        messages.error(request, "Invalid submission.")
        return redirect('/assessment/?q=1')

    try:
        question_id = int(question_id)
        question = Question.objects.get(id=question_id)
        selected_option = request.POST.get(f"question_{question_id}")
    except (ValueError, Question.DoesNotExist):
        messages.error(request, "Invalid question.")
        return redirect(f'/assessment/?q={question_id}')

    if selected_option:
        UserResponse.objects.update_or_create(
            user=student,
            question=question,
            defaults={
                'selected_option': selected_option,
                'is_correct': selected_option == question.correct_option
            }
        )
    else:
        # Remove any existing response if no option selected
        UserResponse.objects.filter(user=student, question=question).delete()

    next_question_index = question_id + 1
    # total_questions = Question.objects.count()
    questions = list(Question.objects.all()[:5])  # Same as assessment_view
    total_questions = len(questions)
    
    # Modified this part to redirect to review on last question
    if next_question_index > total_questions:
        return redirect('/review/') 
    else:
        return redirect(f'/assessment/?q={next_question_index}')
@never_cache  
def review_view(request):
    student_id = request.session.get('user_id')
    if not student_id:
        messages.error(request, "Session expired.")
        return redirect('/')

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        messages.error(request, "Student not found.")
        return redirect('/')

    questions = list(Question.objects.all()[:5])
    responses = UserResponse.objects.filter(user=student)
    answered_count = responses.count()
    total_questions = len(questions)

    # Calculate remaining time
    if 'test_start_time' in request.session:
        elapsed = timezone.now().timestamp() - request.session['test_start_time']
        remaining = max(0, 3600 - int(elapsed))  # 60 minutes test duration
        minutes = remaining // 60
        seconds = remaining % 60
        remaining_time = f"{minutes:02d}:{seconds:02d}"
    else:
        remaining_time = "60:00"

    context = {
        'student': student,
        'answered_count': answered_count,
        'total_questions': total_questions,
        'remaining_time': remaining_time,
    }
    return render(request, 'review.html', context)

import csv
from django.conf import settings
import os
from datetime import datetime
@never_cache
def final_submit_view(request):
    student_id = request.session.get('user_id')
    if not student_id:
        messages.error(request, "Session expired.")
        return redirect('/')

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        messages.error(request, "Student not found.")
        return redirect('/')

    # Calculate score
    responses = UserResponse.objects.filter(user=student)
    total_questions = Question.objects.count()
    answered_count = responses.count()
    correct_answers = responses.filter(is_correct=True).count()
    score_percentage = round((correct_answers / total_questions) * 100, 2) if total_questions > 0 else 0
    
    # Mark test as completed
    student.test_completed = True
    student.save()
    
    # Save results to CSV
    csv_file_path = os.path.join(settings.BASE_DIR, 'student_results.csv')
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.isfile(csv_file_path)
    
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write headers if file doesn't exist
        if not file_exists:
            writer.writerow(['Timestamp', 'Full Name', 'Registration Number', 'Score', 'Disqualified'])
            
        # Write student data (not disqualified)
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            student.name,
            student.roll_number,
            f"{score_percentage}%",
            "No"  # Not disqualified
        ])
    
    # Clear session data
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'test_start_time' in request.session:
        del request.session['test_start_time']

    context = {
        'total_questions': total_questions,
        'answered_count': answered_count,
        'correct_answers': correct_answers,
        'score_percentage': f"{score_percentage}%",
    }
    return render(request, 'submission_confirmation.html', context)

def test_ended_view(request):
    student_id = request.session.get('user_id')
    
    # Only log if there was a student session
    if student_id:
        try:
            student = Student.objects.get(id=student_id)
            
            # Save disqualification to CSV
            csv_file_path = os.path.join(settings.BASE_DIR, 'student_results.csv')
            file_exists = os.path.isfile(csv_file_path)
            
            with open(csv_file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                
                if not file_exists:
                    writer.writerow(['Timestamp', 'Full Name', 'Registration Number', 'Score', 'Disqualified'])
                
                writer.writerow([
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    student.name,
                    student.roll_number,
                    "0%",  # Score is 0% for disqualified
                    "Yes"  # Disqualified
                ])
        
        except Student.DoesNotExist:
            pass
    
    # Clear session data
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'test_start_time' in request.session:
        del request.session['test_start_time']
        
    response = render(request, 'test_ended.html')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response