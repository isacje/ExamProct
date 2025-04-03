from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from exam import models as QMODEL
from teacher import models as TMODEL


#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')


def student_signup_view(request):
    userForm = forms.StudentUserForm()
    studentForm = forms.StudentForm()
    mydict = {'userForm': userForm, 'studentForm': studentForm}
    if request.method == 'POST':
        userForm = forms.StudentUserForm(request.POST)
        studentForm = forms.StudentForm(request.POST, request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            student = studentForm.save(commit=False)
            student.user = user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request, 'student/studentsignup.html', context=mydict)

def logout(request):
    return render(request,'logout.html')
def is_student(user):
    return user.groups.filter(name='STUDENT').exists()


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    student = Student.objects.get(user=request.user)
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    'studentdtls':student
    }
    return render(request,'student/student_dashboard.html',context=dict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    student = Student.objects.get(user=request.user)
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_exam.html',{'courses':courses,'studentdtls':student})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    student = Student.objects.get(user=request.user)
    print('student',student)
    print('studentdtls',course)
    
    # Check if the student has already taken this exam
    if QMODEL.Result.objects.filter(student=student, exam=course).exists():
        return render(request, 'student/exam_already_taken.html', {'course': course})

    total_questions = QMODEL.Question.objects.filter(course=course).count()
    questions = QMODEL.Question.objects.filter(course=course)
    total_marks = sum(q.marks for q in questions)
    
    return render(request, 'student/take_exam.html', {
        'course': course,
        'total_questions': total_questions,
        'total_marks': total_marks,
        'studentdtls':student
    })

# @login_required(login_url='studentlogin')
# @user_passes_test(is_student)
# def start_exam_view(request,pk):
#     course=QMODEL.Course.objects.get(id=pk)
#     questions=QMODEL.Question.objects.all().filter(course=course)
#     if request.method=='POST':
#         pass
#     response= render(request,'student/start_exam.html',{'course':course,'questions':questions})
#     response.set_cookie('course_id',course.id)
#     return response
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required, user_passes_test
# from exam import models as QMODEL
# from student.models import Student
# import cv2
# import numpy as np
# from datetime import datetime
# from threading import Thread
# from django.http import HttpResponse
# from django.utils import timezone

# # Global flag to control monitoring
# monitoring_active = {}  # Dictionary to track monitoring status by student-exam pair

# # Function to handle camera monitoring in a separate thread
# def monitor_exam(student, course):
#     student_exam_key = f"{student.id}-{course.id}"
    
#     # Get or create a single monitoring record for this session
#     monitoring_record, created = QMODEL.ExamMonitoring.objects.get_or_create(
#         student=student,
#         exam=course,
#         defaults={
#             'timestamp': timezone.now(),
#             'looking_at_screen': True,
#             'using_mobile': False,
#             'multiple_students': False
#         }
#     )
    
#     cap = cv2.VideoCapture(0)  # Default webcam
#     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
#     # Only run monitoring while active for this specific student-exam pair
#     while cap.isOpened() and monitoring_active.get(student_exam_key, False):
#         ret, frame = cap.read()
#         if not ret:
#             break

#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = face_cascade.detectMultiScale(gray, 1.1, 4)

#         # Monitoring logic
#         looking_at_screen = len(faces) > 0  # Face detected means looking at screen
#         multiple_students = len(faces) > 1  # More than one face detected
#         using_mobile = False

#         # Lightweight mobile detection using edge detection
#         edges = cv2.Canny(gray, 100, 200)
#         contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#         for contour in contours:
#             if cv2.contourArea(contour) > 500:  # Adjust threshold for mobile size
#                 using_mobile = True
#                 break

#         # Update existing record instead of creating new ones
#         monitoring_record.timestamp = timezone.now()
#         monitoring_record.looking_at_screen = looking_at_screen
#         monitoring_record.using_mobile = using_mobile
#         monitoring_record.multiple_students = multiple_students
#         monitoring_record.save()

#         # No display window in production
#         # cv2.imshow('Exam Monitoring', frame)
#         cv2.waitKey(1)  # Small delay to allow processing

#     # Clean up when monitoring stops
#     cap.release()
#     cv2.destroyAllWindows()

# @login_required(login_url='studentlogin')
# @user_passes_test(is_student)
# def start_exam_view(request, pk):
#     course = QMODEL.Course.objects.get(id=pk)
#     questions = QMODEL.Question.objects.all().filter(course=course)
#     student = Student.objects.get(user=request.user)
#     student_exam_key = f"{student.id}-{course.id}"

#     # Start monitoring only if it hasn't started yet for this student-exam pair
#     if request.method == 'GET' and not monitoring_active.get(student_exam_key, False):
#         monitoring_active[student_exam_key] = True
#         monitoring_thread = Thread(target=monitor_exam, args=(student, course))
#         monitoring_thread.daemon = True  # Thread stops when main process ends
#         monitoring_thread.start()

#     if request.method == 'POST':
#         print('Request','Trquire')
#         # Stop monitoring when exam is submitted
#         monitoring_active[student_exam_key] = False
        
#         # Use redirect to calculate marks
#         print('hello','dcsdc')
#         response = HttpResponseRedirect(reverse('calculate-marks'))
#         response.set_cookie('course_id', course.id)
#         return response

#     # Render the exam page for GET requests
#     response = render(request, 'student/start_exam.html', {'course': course, 'questions': questions})
#     response.set_cookie('course_id', course.id)
#     return response

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from exam import models as QMODEL
from student.models import Student
import cv2
import numpy as np
from datetime import datetime
from threading import Thread
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.utils import timezone
from ultralytics import YOLO

import dlib
from scipy.spatial import distance as dist
from imutils import face_utils
import os
from django.conf import settings

# Load face detector and shape predictor
detector = dlib.get_frontal_face_detector()
lnd = os.path.join(settings.BASE_DIR, 'shape_predictor_68_face_landmarks.dat')
predictor = dlib.shape_predictor(lnd)

def eye_aspect_ratio(eye):
    # Compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    # Compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])
    # Compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)
    return ear

# Global flag to control monitoring
monitoring_active = {}  # Dictionary to track monitoring status by student-exam pair

# Dictionary to store violation history
violation_history = {}  # Format: {student_exam_key: {'mobile': bool, 'multiple': bool}}
bst=os.path.join(settings.BASE_DIR,'best300.pt')
# Load YOLO model once at the module level
yolo_model = YOLO('yolov8n.pt')  # Load YOLOv8 model
# Function to handle camera monitoring in a separate thread
def monitor_exam(student, course):
    student_exam_key = f"{student.id}-{course.id}"
    
    # Initialize violation history for this session
    if student_exam_key not in violation_history:
        violation_history[student_exam_key] = {
            'mobile_detected': False,
            'multiple_students_detected': False,
            'multiple_students_count':0
        }
    
    # Get or create a monitoring record for this session
    monitoring_record, created = QMODEL.ExamMonitoring.objects.get_or_create(
        student=student,
        exam=course,
        defaults={
            'timestamp': timezone.now(),
            'looking_at_screen': True,
            'using_mobile': False,
            'multiple_students': False,
            'mobile_violation_occurred': False,
            'multiple_students_violation_occurred': False
        }
    )
    
    # Add the violation flags if they don't exist
    if not hasattr(monitoring_record, 'mobile_violation_occurred'):
        monitoring_record.mobile_violation_occurred = False
    
    if not hasattr(monitoring_record, 'multiple_students_violation_occurred'):
        monitoring_record.multiple_students_violation_occurred = False
    
    cap = cv2.VideoCapture(0)
    
    # Constants for eye aspect ratio
    EYE_AR_THRESH = 0.25
    EYE_AR_CONSEC_FRAMES = 3
    
    # Counter for frames with eyes closed
    eye_closed_counter = 0
    
    while cap.isOpened() and monitoring_active.get(student_exam_key, False):
        ret, frame = cap.read()
        if not ret:
            break

        # Process the frame with YOLOv8 for person/phone detection
        results = yolo_model(frame)
        boxes = results[0].boxes.xyxy.cpu().numpy()
        class_ids = results[0].boxes.cls.cpu().numpy()
        
        # Count people (class_id 0 is person in COCO dataset)
        num_people = sum(1 for cid in class_ids if int(cid) == 0)
        print('num_people',num_people)
        
        # Check for mobile phone (class_id 67 is cell phone in COCO dataset)
        mobile_detected = any(int(cid) == 67 for cid in class_ids)
        
        # Update violation history if violations are detected
        if mobile_detected:
            violation_history[student_exam_key]['mobile_detected'] = True
        
        if num_people > 1:
            violation_history[student_exam_key]['multiple_students_detected'] = True
            violation_history[student_exam_key]['multiple_students_count'] += 1
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = detector(gray, 0)
        
        # Flag for eye monitoring
        eyes_open = False
        face_present = False
        
        for face in faces:
            face_present = True
            
            # Determine facial landmarks
            shape = predictor(gray, face)
            shape = face_utils.shape_to_np(shape)
            
            # Extract the left and right eye coordinates
            left_eye = shape[36:42]
            right_eye = shape[42:48]
            
            # Calculate the eye aspect ratio
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)
            
            # Average the eye aspect ratio
            ear = (left_ear + right_ear) / 2.0
            
            # Check if eyes are open
            if ear > EYE_AR_THRESH:
                eyes_open = True
                eye_closed_counter = 0
            else:
                eye_closed_counter += 1
        
        # Determine if student is looking at screen
        # Consider them looking if face is detected, eyes are open, and not consistently closed
        looking_at_screen = face_present and (eyes_open or eye_closed_counter < EYE_AR_CONSEC_FRAMES)
        
        # Update monitoring record with current state and violation history
        monitoring_record.timestamp = timezone.now()
        monitoring_record.looking_at_screen = looking_at_screen
        monitoring_record.using_mobile = mobile_detected
        monitoring_record.multiple_students = num_people > 1
        
        # Set the persistent violation flags
        monitoring_record.mobile_violation_occurred = violation_history[student_exam_key]['mobile_detected']
        monitoring_record.multiple_students_violation_occurred = violation_history[student_exam_key]['multiple_students_count'] > 3
        
        monitoring_record.save()
        
        cv2.waitKey(1)

    # Clean up
    cap.release()
    cv2.destroyAllWindows()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    questions = QMODEL.Question.objects.all().filter(course=course)
    student = Student.objects.get(user=request.user)
    student_exam_key = f"{student.id}-{course.id}"

    # Start monitoring only if it hasn't started yet for this student-exam pair
    if request.method == 'GET' and not monitoring_active.get(student_exam_key, False):
        monitoring_active[student_exam_key] = True
        monitoring_thread = Thread(target=monitor_exam, args=(student, course))
        monitoring_thread.daemon = True  # Thread stops when main process ends
        monitoring_thread.start()

    if request.method == 'POST':
        # Stop monitoring when exam is submitted
        monitoring_active[student_exam_key] = False
        
        # Use redirect to calculate marks
        response = HttpResponseRedirect(reverse('calculate-marks'))
        response.set_cookie('course_id', course.id)
        return response

    # Render the exam page for GET requests
    response = render(request, 'student/start_exam.html', {'course': course, 'questions': questions,'studentdtls':student})
    response.set_cookie('course_id', course.id)
    return response
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def generate_pdf_report(request, pk):
    import re
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle

    course = QMODEL.Course.objects.get(id=pk)
    student = Student.objects.get(user=request.user)
    monitoring_records = QMODEL.ExamMonitoring.objects.filter(student=student, exam=course).order_by('timestamp')
    result = QMODEL.Result.objects.filter(student=student, exam=course).first()
    
    # Get the latest monitoring record which contains the violation history
    latest_record = monitoring_records.last()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="exam_report_{student.user.username}.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)

    # Title
    p.drawString(100, 750, f"Exam Report for {student.user.username}")
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, f"Course: {course.course_name}")
    p.drawString(100, 710, f"Marks: {result.marks if result else 'N/A'}")
    
    # Count monitoring checks and not looking at screen
    total_records = monitoring_records.count()
    not_looking_count = monitoring_records.filter(looking_at_screen=False).count()
    
    # Add violation summary
    if latest_record:
        # Display the persistent violation flags
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 610, "Violation Detection:")
        p.setFont("Helvetica", 12)
        
        if latest_record.mobile_violation_occurred:
            p.drawString(120, 590, "⚠️ Mobile phone was detected during this exam session")
        else:
            p.drawString(120, 590, "✓ No mobile phone usage detected")
            
        if latest_record.multiple_students_violation_occurred:
            p.drawString(120, 570, "⚠️ Multiple people were detected during this exam session")
        else:
            p.drawString(120, 570, "✓ No additional people detected")
        
        # Tab Switch Detection
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 540, "Tab Switch Violations:")
        p.setFont("Helvetica", 12)
        
        # More comprehensive regex to find all tab switch entries
        if latest_record.details:
            # Regex to find tab switch count from the new logging format
            tab_switch_pattern = r'\[.*?\] Tab switching detected (\d+) times'
            tab_switch_matches = re.findall(tab_switch_pattern, latest_record.details)
            
            if tab_switch_matches:
                total_switches = sum(int(count) for count in tab_switch_matches)
                
                if total_switches > 0:
                    p.drawString(120, 520, f"⚠️ Tab switched {total_switches} time(s) during the exam")
                    
                    # Optional: Add more detailed breakdown
                    if len(tab_switch_matches) > 1:
                        p.drawString(120, 500, f"Multiple tab switch events: {len(tab_switch_matches)} instances")
                else:
                    p.drawString(120, 520, "✓ No unauthorized tab switches detected")
            else:
                # Fallback to older logging format
                tab_switch_match = re.search(r'Tab switching detected (\d+)', latest_record.details)
                if tab_switch_match:
                    tab_switch_count = int(tab_switch_match.group(1))
                    if tab_switch_count > 0:
                        p.drawString(120, 520, f"⚠️ Tab switched {tab_switch_count} time(s) during the exam")
                    else:
                        p.drawString(120, 520, "✓ No unauthorized tab switches detected")
                else:
                    p.drawString(120, 520, "✓ No tab switch information available")
        else:
            p.drawString(120, 520, "✓ No additional details recorded")
        
    p.showPage()
    p.save()
    return response

from django.db import transaction

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    if request.COOKIES.get('course_id') is not None:
        course_id = request.COOKIES.get('course_id')
        course = QMODEL.Course.objects.get(id=course_id)
    
        total_marks = 0
        questions = QMODEL.Question.objects.all().filter(course=course)
        for i in range(len(questions)):
            selected_ans = request.COOKIES.get(str(i + 1))
            actual_answer = questions[i].answer
            if selected_ans == actual_answer:
                total_marks = total_marks + questions[i].marks
        
        student = models.Student.objects.get(user_id=request.user.id)
        student_exam_key = f"{student.id}-{course.id}"
        monitoring_active[student_exam_key] = False
        
        try:
            with transaction.atomic():
                result, created = QMODEL.Result.objects.update_or_create(
                    student=student,
                    exam=course,
                    defaults={'marks': total_marks}
                )
        except Exception as e:
            # Handle the exception appropriately
            return HttpResponse("An error occurred: {}".format(str(e)), status=500)

        return HttpResponseRedirect('view-result')


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    student = Student.objects.get(user=request.user)
    courses=QMODEL.Course.objects.all()
    return render(request,'student/view_result.html',{'courses':courses,'studentdtls':student})
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.all().filter(exam=course).filter(student=student)    
    questions=QMODEL.Question.objects.all().filter(course=course)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks
    
    return render(request,'student/check_marks.html',{'results':results, 'total_marks':total_marks,'studentdtls':student})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses=QMODEL.Course.objects.all()
    student = Student.objects.get(user=request.user)
    return render(request,'student/student_marks.html',{'courses':courses,'studentdtls':student})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def log_tab_switch(request):
    if request.method == 'POST':
        try:
            exam_id = request.POST.get('exam_id')
            tab_switch_count = request.POST.get('tab_switch_count', '0')
            print('gg',tab_switch_count)
            
            # Validate inputs
            if not exam_id:
                return JsonResponse({'status': 'error', 'message': 'Exam ID is required'}, status=400)
            
            student = Student.objects.get(user=request.user)
            course = QMODEL.Course.objects.get(id=exam_id)
            
            # Timestamp for precise tracking
            current_time = timezone.now()
            
            # Get or create the monitoring record
            monitoring_record, created = QMODEL.ExamMonitoring.objects.get_or_create(
                student=student,
                exam=course
            )
            
            # If record already exists, update it
            if not created:
                print("Tab switching detected")
                monitoring_record.timestamp = current_time
                monitoring_record.looking_at_screen = False
                
                # Append new tab switch information, keeping a log of multiple instances
                if monitoring_record.details is not None:
                    print("Appending")
                    monitoring_record.details += f"\n[{current_time}] Tab switching detected {tab_switch_count} times"
                    print(monitoring_record.details,'hhyu')
                    monitoring_record.save()
                else:
                    print("name()")
                    monitoring_record.details = f"\n[{current_time}] Tab switching detected {tab_switch_count} times"
                    monitoring_record.save()
                monitoring_record.save()
            
            return JsonResponse({
                'status': 'success', 
                'message': f'Tab switch logged: {tab_switch_count} times'
            })
        
        except Student.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Student not found'}, status=404)
        
        except QMODEL.Course.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Course not found'}, status=404)
        
        except Exception as e:
            print('kkr',e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
  