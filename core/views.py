from django.shortcuts import render, redirect
from .models import Student, Question, UserResponse
from django.http import HttpResponse
from django.contrib import messages

from .models import Student, Question, UserResponse

# Signup
def signup_view(request):
    if request.method == 'POST':
        data = request.POST
        if Student.objects.filter(email=data['email']).exists() or Student.objects.filter(roll_number=data['roll_number']).exists():
            messages.error(request, "Email or Roll Number already exists.")
            return redirect('signup')
        student = Student.objects.create(
            name=data['name'],
            roll_number=data['roll_number'],
            email=data['email'],
            phone=data['phone'],
            password=data['password']
        )
        request.session['user_id'] = student.id
        return redirect('rules')
    return render(request, 'signup.html')

# Login
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            student = Student.objects.get(email=email, password=password)
            request.session['user_id'] = student.id
            return redirect('rules')
        except Student.DoesNotExist:
            messages.error(request, "Invalid credentials.")
    return render(request, 'login.html')

# Rules
def rules_view(request):
    if request.method == 'POST' and request.POST.get('agree') == 'on':
        return redirect('assessment')
    return render(request, 'rules.html')

# Assessment
def assessment_view(request):
    student_id = request.session.get('user_id')
    if not student_id:
        return redirect('login')
    student = Student.objects.get(id=student_id)
    questions = Question.objects.all()[:5]
    return render(request, 'assessment.html', {'student': student, 'questions': questions})

# Submit
def submit_view(request):
    student = Student.objects.get(id=request.session['user_id'])
    for key, value in request.POST.items():
        if key.startswith('question_'):
            qid = int(key.split('_')[1])
            question = Question.objects.get(id=qid)
            UserResponse.objects.create(
                user=student,
                question=question,
                selected_option=value,
                is_correct=(value == question.correct_option)
            )
    return HttpResponse("Assessment submitted. Thank you!")
