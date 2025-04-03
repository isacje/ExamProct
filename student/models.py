from django.db import models
from django.contrib.auth.models import User
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/Student/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=False)
    class_name = models.CharField(max_length=50, null=True, blank=True)  # e.g., "Class 10A"
    roll_number = models.CharField(max_length=20, null=True, blank=True)  # e.g., "A123"

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_instance(self):
        return self

    def __str__(self):
        return self.user.first_name