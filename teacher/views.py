from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from exam import models as QMODEL
from student import models as SMODEL
from exam import forms as QFORM


#for showing signup/login button for teacher
def teacherclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'teacher/teacherclick.html')

def logout(request):
    return render(request,'logout.html')
def teacher_signup_view(request):
    userForm=forms.TeacherUserForm()
    teacherForm=forms.TeacherForm()
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=forms.TeacherUserForm(request.POST)
        teacherForm=forms.TeacherForm(request.POST,request.FILES)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            teacher=teacherForm.save(commit=False)
            teacher.user=user
            teacher.save()
            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)
        return HttpResponseRedirect('teacherlogin')
    return render(request,'teacher/teachersignup.html',context=mydict)



def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    teacherdtls = models.Teacher.objects.get(user=request.user)
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    'total_student':SMODEL.Student.objects.all().count(),
    'teacherdtls':teacherdtls
    
    }
    return render(request,'teacher/teacher_dashboard.html',context=dict)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_exam_view(request):
    teacherdtls = models.Teacher.objects.get(user=request.user)
    return render(request,'teacher/teacher_exam.html',{'teacherdtls':teacherdtls})


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_exam_view(request):
    teacherdtls = models.Teacher.objects.get(user=request.user)
    courseForm=QFORM.CourseForm()
    if request.method=='POST':
        courseForm=QFORM.CourseForm(request.POST)
        if courseForm.is_valid():        
            courseForm.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-exam')
    return render(request,'teacher/teacher_add_exam.html',{'courseForm':courseForm,'teacherdtls':teacherdtls})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_exam_view(request):
    teacherdtls = models.Teacher.objects.get(user=request.user)
    courses = QMODEL.Course.objects.all()
    return render(request,'teacher/teacher_view_exam.html',{'courses':courses,'teacherdtls':teacherdtls})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def delete_exam_view(request,pk):
    teacherdtls = models.Teacher.objects.get(user=request.user)
    course=QMODEL.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/teacher/teacher-view-exam',{'teacherdtls':teacherdtls})

@login_required(login_url='adminlogin')
def teacher_question_view(request):
    teacherdtls = models.Teacher.objects.get(user=request.user)
    return render(request,'teacher/teacher_question.html',{'teacherdtls':teacherdtls})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_question_view(request):
    questionForm=QFORM.QuestionForm()
    teacherdtls = models.Teacher.objects.get(user=request.user)
    if request.method=='POST':
        questionForm=QFORM.QuestionForm(request.POST)
        if questionForm.is_valid():
            question=questionForm.save(commit=False)
            course=QMODEL.Course.objects.get(id=request.POST.get('courseID'))
            question.course=course
            question.save()       
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-question')
    return render(request,'teacher/teacher_add_question.html',{'questionForm':questionForm,'teacherdtls':teacherdtls})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_question_view(request):
    teacherdtls = models.Teacher.objects.get(user=request.user)
    courses= QMODEL.Course.objects.all()
    return render(request,'teacher/teacher_view_question.html',{'courses':courses,'teacherdtls':teacherdtls})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def see_question_view(request,pk):
    teacherdtls = models.Teacher.objects.get(user=request.user)
    questions=QMODEL.Question.objects.all().filter(course_id=pk)
    return render(request,'teacher/see_question.html',{'questions':questions,'teacherdtls':teacherdtls})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def remove_question_view(request,pk):
    question=QMODEL.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/teacher/teacher-view-question')


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)  # You'll need to define this function similar to is_student
def teacher_generate_exam_monitoring_pdf(request, course_id, student_id=None):
    """
    Generate PDF report of ExamMonitoring records for a teacher.
    If student_id is provided, it will generate a report for that specific student.
    Otherwise, it will generate a summary report for all students in the course.
    """
    course = QMODEL.Course.objects.get(id=course_id)
    
    # Get monitoring records
    if student_id:
        # Report for a specific student
        student = SMODEL.Student.objects.get(id=student_id)
        monitoring_records = QMODEL.ExamMonitoring.objects.filter(
            student=student, 
            exam=course
        ).order_by('timestamp')
        result = QMODEL.Result.objects.filter(student=student, exam=course).first()
        print('mon',monitoring_records)
    else:
        # Summary report for all students in the course
        monitoring_records = QMODEL.ExamMonitoring.objects.filter(
            exam=course
        ).order_by('student', 'timestamp')
    import re
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    
    response = HttpResponse(content_type='application/pdf')
    
    if student_id:
        student = SMODEL.Student.objects.get(id=student_id)
        filename = f"exam_monitoring_{course.course_name}_{student.user.username}.pdf"
    else:
        filename = f"exam_monitoring_{course.course_name}_all_students.pdf"
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Title
    if student_id:
        elements.append(Paragraph(f"Exam Monitoring Report for {student.user.username}", title_style))
    else:
        elements.append(Paragraph(f"Exam Monitoring Summary - {course.course_name}", title_style))
    
    elements.append(Paragraph(f"Course: {course.course_name}", heading_style))
    
    if student_id:
        # Single student report
        student = SMODEL.Student.objects.get(id=student_id)
        result = QMODEL.Result.objects.filter(student=student, exam=course).first()
        
        # Add result information if available
        if result:
            elements.append(Paragraph(f"Marks: {result.marks}", normal_style))
            elements.append(Paragraph(f"Date: {result.date.strftime('%Y-%m-%d %H:%M')}", normal_style))
        
        # Count monitoring checks and violations
        total_records = monitoring_records.count()
        not_looking_count = monitoring_records.filter(looking_at_screen=False).count()
        mobile_detected_count = monitoring_records.filter(using_mobile=True).count()
        multiple_students_count = monitoring_records.filter(multiple_students_violation_occurred=True).count()
        print('h',multiple_students_count)
        
        # Get the latest record to check if violations occurred
        latest_record = monitoring_records.last()
        
        # Add monitoring summary
        elements.append(Paragraph("Monitoring Summary:", heading_style))
        elements.append(Paragraph(f"Total monitoring checks: {total_records}", normal_style))
        elements.append(Paragraph(f"Not looking at screen: {not_looking_count}", normal_style))
        elements.append(Paragraph(f"Mobile phone detected: {mobile_detected_count}", normal_style))
        elements.append(Paragraph(f"Multiple students detected: {multiple_students_count}", normal_style))
        
        # Add violation flags if latest record exists
        if latest_record and latest_record.details:
    # More comprehensive regex to find all tab switch entries
            tab_switch_pattern = r'\[.*?\] Tab switching detected (\d+) times'
            tab_switch_matches = re.findall(tab_switch_pattern, latest_record.details)
            
            elements.append(Paragraph("Tab Switch Violations:", heading_style))
            
            if tab_switch_matches:
                total_switches = sum(int(count) for count in tab_switch_matches)
                
                if total_switches > 0:
                    elements.append(Paragraph(f"⚠️ Tab switched {total_switches} time(s) during the exam", normal_style))
                    
                    # Detailed tab switch information
                    if len(tab_switch_matches) > 1:
                        elements.append(Paragraph(f"Multiple tab switch events: {len(tab_switch_matches)} instances", normal_style))
                else:
                    elements.append(Paragraph("✓ No unauthorized tab switches detected", normal_style))
            else:
                # Fallback to older logging format
                tab_switch_match = re.search(r'Tab Switches: (\d+)', latest_record.details)
                if tab_switch_match:
                    tab_switch_count = int(tab_switch_match.group(1))
                    if tab_switch_count > 0:
                        elements.append(Paragraph(f"⚠️ Tab switched {tab_switch_count} time(s) during the exam", normal_style))
                    else:
                        elements.append(Paragraph("✓ No unauthorized tab switches detected", normal_style))
                else:
                    elements.append(Paragraph("✓ No tab switch information available", normal_style))
        
        # Add detailed monitoring log
        elements.append(Paragraph("Detailed Monitoring Log:", heading_style))
        
        # Create table data
        data = [["Timestamp", "Looking at Screen", "Mobile Detected", "Multiple Students", "Details"]]
        
        for record in monitoring_records:
            data.append([
                record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "Yes" if record.looking_at_screen else "No",
                "Yes" if record.using_mobile else "No",
                "Yes" if record.multiple_students_violation_occurred else "No",
                record.details or ""
            ])
        
        # Create table
        table = Table(data, colWidths=[1.5*inch, 1*inch, 1*inch, 1.2*inch, 2.3*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        
    else:
        # Report for all students in the course
        
        # Get list of students who took this exam
        student_ids = monitoring_records.values_list('student', flat=True).distinct()
        students = SMODEL.Student.objects.filter(id__in=student_ids)
        
        # Summary table data
        summary_data = [["Student", "Total Checks", "Not Looking", "Mobile Detected", "Multiple People", "Tab Switches", "Result"]]
        
        for student in students:
            student_records = monitoring_records.filter(student=student)
            result = QMODEL.Result.objects.filter(student=student, exam=course).first()
            
            latest_record = student_records.last()
            mobile_violation = latest_record.mobile_violation_occurred if latest_record else False
            multi_student_violation = latest_record.multiple_students_violation_occurred if latest_record else False
            
            # Tab Switch Detection
            tab_switches = 0
            if latest_record and latest_record.details:
                # Try new format first
                tab_switch_matches = re.findall(r'\[.*?\] Tab switching detected (\d+) times', latest_record.details)
                print('tab', tab_switch_matches)
                if tab_switch_matches:
                    tab_switches = sum(int(count) for count in tab_switch_matches)
                    print('tabi', tab_switches)
                else:
                    # Fallback to old format
                    tab_switch_match = re.search(r'Tab switching detected (\d+)', latest_record.details)
                    print('tabu', tab_switch_match)
                    if tab_switch_match:
                        tab_switches = int(tab_switch_match.group(1))
            
            # Add violation indicators
            violations = ""
            if mobile_violation:
                violations += "📱 "
            if multi_student_violation:
                violations += "👥 "
            if tab_switches > 0:
                tab_switches = 1
                violations += "🔄 "
                
            summary_data.append([
                student.user.username,
                student_records.count(),
                student_records.filter(looking_at_screen=False).count(),
                student_records.filter(mobile_violation_occurred=True).count(),
                student_records.filter(multiple_students_violation_occurred=True).count(),
                tab_switches,
                f"{result.marks if result else 'N/A'} {violations}"
            ])

        # Update the summary_table column widths to accommodate the new column
        summary_table = Table(summary_data, colWidths=[1.2*inch, 1.1*inch, 1.1*inch, 1.1*inch, 1.1*inch, 1.1*inch, 1.1*inch])
        
        # Style the summary table
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(Paragraph("Student Summary", heading_style))
        elements.append(Paragraph("Legend: 📱 Mobile detected, 👥 Multiple people detected, 🔄 Tab switches", normal_style))
        elements.append(summary_table)
        
        # Add note about individual reports
    
    # Build the PDF
    doc.build(elements)
    return response


