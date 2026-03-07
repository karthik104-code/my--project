from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100)
    head_of_department = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    SEMESTER_CHOICES = [
        (1, 'Semester 1'),
        (2, 'Semester 2'),
        (3, 'Semester 3'),
        (4, 'Semester 4'),
    ]

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    semester = models.PositiveSmallIntegerField(
        choices=SEMESTER_CHOICES,
        default=1
    )
    credits = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.code} - {self.name}"


class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    enrollment_date = models.DateField(auto_now_add=True)
    courses = models.ManyToManyField(Course, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"