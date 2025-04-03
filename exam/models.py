from django.db import models

from student.models import Student
class Course(models.Model):
   course_name = models.CharField(max_length=50)
   question_number = models.PositiveIntegerField()
   total_marks = models.PositiveIntegerField()
   time_limit = models.PositiveIntegerField(default=60, help_text="Time limit in minutes")
   def __str__(self):
        return self.course_name

class Question(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    marks=models.PositiveIntegerField()
    question=models.CharField(max_length=600)
    option1=models.CharField(max_length=200)
    option2=models.CharField(max_length=200)
    option3=models.CharField(max_length=200)
    option4=models.CharField(max_length=200)
    cat=(('Option1','Option1'),('Option2','Option2'),('Option3','Option3'),('Option4','Option4'))
    answer=models.CharField(max_length=200,choices=cat)

class Result(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.ForeignKey(Course,on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)
    
class ExamMonitoring(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Course, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    looking_at_screen = models.BooleanField(default=True)  # True if student is looking at screen
    using_mobile = models.BooleanField(default=False)      # True if mobile phone detected
    multiple_students = models.BooleanField(default=False) # True if multiple faces detected
    details = models.TextField(blank=True, null=True)      # Optional field for additional info
    mobile_violation_occurred = models.BooleanField(default=False)
    multiple_students_violation_occurred = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.user.username} - {self.exam.course_name} - {self.timestamp}"

