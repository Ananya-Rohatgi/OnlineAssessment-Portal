from django.shortcuts import render, redirect
from .models import Student, Question, UserResponse
from django.http import HttpResponse
from django.contrib import messages

from .models import Student, Question, UserResponse

# Signup
def signup_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        roll_number = request.POST.get('roll_number')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        # Check if email already exists
        if Student.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered. Please use a different email.")
            return redirect('/')  # Or render again with form data

        Student.objects.create(
            name=name,
            roll_number=roll_number,
            email=email,
            phone=phone
        )
        return redirect('/rules/')  # Or wherever you want to go next

    return render(request, "signup.html")

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
