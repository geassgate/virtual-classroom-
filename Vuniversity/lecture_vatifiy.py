from .models import *

def time2mint(x):
    lec_start = str(x).split(":")
    new_lec_hours = int(lec_start[0]) * 60
    new_lec_start = new_lec_hours + int(lec_start[1])
    return int(new_lec_start)

#----------------calculate the end of lecture ---------------#

def main(request, list_row):
    
    # -------------------preparing data to store -------------------#

    new_lec_time_start = list_row[4]
    new_lec_duration = list_row[5]
    new_lec_time_start_in_mint = time2mint(new_lec_time_start)
    new_lec_duration_in_min = time2mint(new_lec_duration)
    new_lec_end = new_lec_time_start_in_mint + new_lec_duration_in_min


    #-----------get element from another table----------------#
    new_lect_date = str(list_row[3])
    carrant_lecturer = Lecturer.objects.get(user=request.user.id)
    lecturer_corsee = carrant_lecturer.corses.all()

    #----------------check lecture conflect--------------------#
    for corse in lecturer_corsee:
        course_lectures = corse.lecture.filter(lec_date=new_lect_date).values()
        for lecture in course_lectures:
            lec_start = lecture['time']
            lec_start_in_min = time2mint(lec_start)
            lec_duration = lecture['duration']
            lec_duration_in_min = time2mint(lec_duration)
            curnt_lec_end = lec_duration_in_min + lec_start_in_min
            if new_lec_end > lec_start_in_min and new_lec_time_start_in_mint < curnt_lec_end:
                return True


def student_conflect(list_row):
    new_lec_time_start = list_row[4]
    new_lec_duration = list_row[5]
    new_lec_time_start_in_mint = time2mint(new_lec_time_start)
    new_lec_duration_in_min = time2mint(new_lec_duration)
    new_lec_end = new_lec_time_start_in_mint + new_lec_duration_in_min

    corse_name = list_row[1]
    lect_date = str(list_row[3])
    corse = Corse.objects.get(name = corse_name)
    students = corse.student.all()
    for student in students:
        student_corses = student.corses.all()
        for corse in student_corses:
            student_lectures = corse.lecture.filter(lec_date = lect_date).values()
            for lecture in student_lectures:
                lec_studint_start = lecture['time']
                lec_studint_start_in_min = time2mint(lec_studint_start)
                lec_studint_duration = lecture['duration']
                lec_studint_duration_in_min = time2mint(lec_studint_duration)
                lec_studint_end = lec_studint_start_in_min + lec_studint_duration_in_min

                if new_lec_end > lec_studint_start_in_min and new_lec_time_start_in_mint < lec_studint_end:
                    return True