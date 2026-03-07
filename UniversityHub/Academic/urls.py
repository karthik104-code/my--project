from django.urls import path
from Academic import views
urlpatterns =[
    path('students/',views.student_list),
    path('courses/',views.course_list),
    path('departments/',views.department_list),
    path('register-student/',views.student_create, name='register_student')
]