from django.shortcuts import HttpResponse
# Create your views here.
def student_list(request):
    return HttpResponse("List of Students")


from django.shortcuts import render
from .models import Course,Department,Student

def course_list(request):
    # 1. Fetch data from DB
    all_courses = Course.objects.all()

    # 2. Context: A dictionary mapping template variable names to Python objects
    context = {
        'courses': all_courses,
        'page_title': 'Available Courses'
    }
    return render(request, 'academic/course_list.html', context)

def department_list(request):
    # 1. Fetch data from DB
    all_departments = Department.objects.all()

    # 2. Context: A dictionary mapping template variable names to Python objects
    context = {
        'departments': all_departments,
        'page_title': 'Available Departments'
    }
    return render(request, 'academic/dept_list.html', context)


def student_list(request):
    all_students = Student.objects.all()

    context = {
        'students': all_students,
        'page_title': 'List of Students'
    }
    return render(request, 'academic/students_list.html', context)

from django.shortcuts import render, redirect
from.forms import Student, StudentForm

def student_create(request):
    
    if request.method == 'POST':
        #1. Bind data to the form
        form = StudentForm(request.POST)

        #2. Validation Check
        if form.is_valid():
            #3. Save to DB
            form.save()
            #4. Redirect (Post-Redirect-Get Pattern) return redirect('course_list')

    else:
        #GET request: Create empty form
        form = StudentForm()

    return render(request,
                'academic/student_form.html',
                {'form': form})