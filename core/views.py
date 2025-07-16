from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Student, Question, UserResponse

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
        return redirect('/rules/')

    return render(request, "signup.html")


# Rules View
def rules_view(request):
    if request.method == 'POST' and request.POST.get('agree') == 'on':
        return redirect('/assessment/?q=1')
    return render(request, 'rules.html')


# Assessment View (One question at a time)
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
        return redirect('/test-ended/')

    current_question = questions[current_index - 1]
    responses = UserResponse.objects.filter(user=student)
    answered_question_ids = responses.values_list('question_id', flat=True)

    context = {
        'student': student,
        'questions': questions,
        'current_question': current_question,
        'current_question_index': current_index,
        'answered_question_ids': list(answered_question_ids),
    }
    return render(request, 'assessment.html', context)

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

    next_question_index = question_id + 1
    total_questions = Question.objects.count()
    if next_question_index > total_questions:
        return redirect('/test-ended/')
    else:
        return redirect(f'/assessment/?q={next_question_index}')

def test_ended_view(request):
    return render(request, 'test_ended.html')
