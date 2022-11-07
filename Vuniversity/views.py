from ast import Expression
from datetime import date, datetime
from time import time
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from threading import Timer
from .lecture_vatifiy import main, student_conflect, time2mint
from .models import *
import requests
# Create your views here.


askarr = []

student_time = []

teachers_online = []


def lec_get_started(request):
    name = request.user.username
    user = request.user

    today_lectures = {}
    lecturer = Lecturer.objects.get(user=user)
    lecturer_course = Corse.objects.filter(lecturer_id=lecturer)
    for course in lecturer_course:
        lectures = Lecture.objects.filter(corse=course, lec_date=datetime.today())
        today_lectures[course.name] = lectures

    now = datetime.now()
    now = now.minute + now.hour * 60

    has_lect = False
    for k, c in today_lectures.items():
        for l in c:
            l.time = l.time.minute + l.time.hour * 60
            duration = time2mint(l.duration)
            if now < l.time + duration and now > l.time:
                print(l.time, ' ', duration)
                has_lect = True
    
    if has_lect :
        return render(request, 'lecturer/get_started.html', {
            'lecturer_name': name,
            'live': True,
            'corses': lecturer_course,
        })

    return render(request, 'lecturer/get_started.html', {
        'lecturer_name': name,
        'live': False,
        'corses': lecturer_course,
    })

def login_view(request):
    if request.method == 'POST':
        user_name = request.POST['id']
        password = request.POST['password']

        user = authenticate(request,username=user_name,password=password)
        if user == None:
            messages.success(request,'chick your user name or password')
            return redirect(reverse('vuniversity:Login'))

        owner = Student.objects.filter(user=user)
        if owner:
            login(request, user)
            return redirect(reverse('vuniversity:std_Get_started'))

        owner = Lecturer.objects.filter(user=user)
        if owner :
            login(request, user)
            return redirect(reverse('vuniversity:Get_started'))

    return render(request,'index.html')

def see_all_lecture(request):
    if request.method == "POST":
        row = request.POST.dict()
        list_row = list(row.values())
        # --------- if there is a conflect with another lecture-----#
        if main(request, list_row):
            # massage = "ther are a lecture in the same time "
            messages.success(request,'you have a lecture in the same time')
            return redirect(reverse('vuniversity:Get_started'))

        
        #---------- if student have another lecture in the same time------#
        if student_conflect(list_row):
            
            messages.success(request,'Student have a lecture in the same time')
            return redirect(reverse('vuniversity:Get_started'))
        # -------------------preparing data to store -------------------#
        corse_name = list_row[1]
        corse_info = Corse.objects.get(name=corse_name)
        lec_title = list_row[2]
        lec_date = str(list_row[3])
        lec_time = list_row[4]
        duration = list_row[5]
        #-----------------Store the Data---------------------------------#
        new_row = Lecture(corse=corse_info, name=lec_title,
                        lec_date=lec_date, time=lec_time, duration=duration)
        new_row.save()
    

    quire ={}
    name = request.user.username
    user = request.user
    lecturer = Lecturer.objects.get(user=user)
    lecturer_course = Corse.objects.filter(lecturer_id=lecturer)
    for corse in lecturer_course:
        lecturer_lecture = Lecture.objects.filter(corse=corse)
        quire[corse.name] = lecturer_lecture

    return render(request, 'lecturer/all lecture.html',{
        'lecturer_name': name,
        'quire':quire
    })

def logout_view(request):
    logout(request)
    return redirect(reverse('vuniversity:Login'))

def std_get_started(request):
    name = request.user.username

    std = Student.objects.get(user=request.user)
    corses = std.corses.all()
    print(corses)
    lctr = {}
    for corse in corses:
        student_lecture = Lecture.objects.filter(corse=corse, lec_date=datetime.today())
        lctr[corse.name] = {
            'lectures': student_lecture,
            'course': corse
            }
    print(lctr)

    now = datetime.now()
    # print(now)
    now = now.minute + now.hour * 60
    # print(now)
    has_lect = False
    teacher_name = False
    for k, c in lctr.items():
        for l in c['lectures']:
            l.time = l.time.minute + l.time.hour * 60
            duration = time2mint(l.duration)
            if now < l.time + duration and now > l.time:
                teacher_name = c['course'].lecturer_id.user.username
                print(teacher_name)
                print(l.time, ' ', duration)
                has_lect = True
                break

    t_online = False
    for t in teachers_online:
        if t['name'] == teacher_name:
            t_online = t['online']
            break

    if not t_online:
        return render(request, 'student/get_started.html', {
        'lecturer_name': name,
        'live': False
    })



    if has_lect and t_online:
        return render(request, 'student/get_started.html', {
            'lecturer_name': name,
            'live': True,
        })

    return render(request, 'student/get_started.html', {
        'lecturer_name': name,
        'live': False
    })

def std_all_lecture(request):
    name = request.user.username
    user = request.user
    student = Student.objects.get(user=user)
    student_corses = student.corses.all()
    quire = {}
    for corse in student_corses:
        student_lecture = Lecture.objects.filter(corse=corse)
        quire[corse.name] = student_lecture

    return render(request, 'student/see all lecture.html', {
        'lecturer_name': name,
        'quire':quire
    })

def summary(request):
    global student_time
    students = student_time.copy()
    print(students)
    student_time = []
    print(students)

    # me = User.objects.get(id=request.user)
    for t in teachers_online:
        if t['name'] == request.user.username:
            print(t['name'], ' ', request.user.username)
            me = int(t['time'])
            break

    for s in students:
        hrs, mins = divmod(s['time'], 60)
        s['percent'] = s['time'] /  me * 100
        print(s['percent'])
        s['time'] = str(hrs) + ':' + str(mins)  
    return render(request, 'lecturer/summary.html', {
        'students': students
    })

def live_lecture(request):
    lecture_info = {}
    time = datetime.now()
    time = time.strftime('%H:%M')
    time_in_min = time2mint(time)
    user = request.user
    lecturer = Lecturer.objects.get(user=user)
    lecturer_course = Corse.objects.filter(lecturer_id=lecturer)
    for course in lecturer_course:
        lecturer_lectures = course.lecture.all()
        # print('----------')
        # print(lecturer_lectures)
        # print('----------')
        for lecture in lecturer_lectures:
            lecture_start_time = time2mint(lecture.time)
            # print(lecture_start_time)
            lecture_duration = time2mint(lecture.duration)
            lect_end = lecture_start_time + lecture_duration

            if lecture.lec_date == date.today() and time_in_min > lecture_start_time and time_in_min < lect_end:
                lecture_info[course] = lecture
                # print('----------')
                # print(lecture.lec_date == date.today())
                # print('----------')
    # print(lecturer_lectures)
    # print('----------')
    # print(lecture_info)
    # print('----------')
    lecture_name =""
    corse_name = ""
    for k, v in lecture_info.items():
        lecture_name = v.name
        corse_name = k.name
    name = request.user.username

    return render(request, 'lecturer/next_lecture.html',{
        'lecturer_name': name,
        'room': 1234,
        'lecture_name':lecture_name,
        'course_name' : corse_name
    })

def std_live(request):
    name = request.user.username
    return render(request,'student/show live lecture.html',{
        'lecturer_name' : name ,
        'room': 1234
    })


@csrf_exempt
def ask_api(request):
    m = json.loads(request.body)
    global askarr
    if m['sender'] == 'student':
        if m['type'] == 'ask':

            for s in askarr:
                if m['sname'] == s['name']:
                    if s['state'] == 'no':
                        s['state'] = ''

                return JsonResponse({'state': ''})

            ask = {
                'name': m['sname'],
                'state': ''
            }

            askarr.append(ask)
            return JsonResponse({'state': 'ok'})
        elif m['type'] == 'speak':
            for s in askarr:
                if s['name'] == m['sname']:
                    if s['state'] == 'ok':
                        askarr.remove(s)
                        return JsonResponse({'state': 'ok'})
                    elif s['state'] == 'no':
                        return JsonResponse({'state': 'no'})
                    elif s['state'] == '':
                        return JsonResponse({'state': 'retry'})
            
            return JsonResponse({'state': 'error'})
    elif m['sender'] == 'teacher':
        if m['type'] == 'checkask':
            askers = []

            print(askarr)
            for s in askarr:
                if s['state'] == '':
                    askers.append(s['name'])

            if len(askers) == 0:
                return JsonResponse({'students': 'empty'})
            return JsonResponse({'students': askers})
        elif m['type'] == 'reply':
            for s in askarr:
                if s['name'] == m['name']:
                    s['state'] = m['state']
                    print(askarr)
                    break
            return JsonResponse({'state': 'ok'})


@csrf_exempt
def time_api(request):
    m = json.loads(request.body)
    if m['sender'] == 'student':
        global student_time
        for s in student_time:
            if s['name'] == m['name']:
                s['time'] += 1
                return JsonResponse({'res': 'ok'})

        st = {
            'name': m['name'],
            'time': 1
        }
        student_time.append(st)
        return JsonResponse({'res': 'ok'})

    if m['sender'] == 'teacher':
        global teachers_online
        for t in teachers_online:
            if t['name'] == m['name']:
                t['online'] = True
                t['time'] += 1
                timer = Timer(59.0, offline, args=(t,))
                timer.start()
                return JsonResponse({'res': 'ok'})

        t = {
            'name': m['name'],
            'online': True,
            'time': 1
        }
        teachers_online.append(t)
        timer = Timer(59.0, offline, args=(t,))
        timer.start()
        return JsonResponse({'res': 'ok'})

def offline(t):
    print(teachers_online)
    t['online'] = False
    print(teachers_online)
    return

@csrf_exempt
def alter_api(request):
    
    m = json.loads(request.body)
    lecture = Lecture.objects.get(name=m['lecture'])
    lecture.file = m['file']
    print('---------m file --------')
    print( m['file'])
    print('-------end mfile----------')
    lecture.describtion = m['description']
    lecture.save()
    print('-----------------')
    print(lecture.file)
    print('-----------------')

    return JsonResponse({'res': 'ok'})