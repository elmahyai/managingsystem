from django.shortcuts import render,redirect
from django.views.generic import TemplateView ,CreateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from administration.decorators import manager_required
from administration.models import User
from django.contrib.auth import login
from administration.forms import ManagerSignUpForm
from django.http import HttpResponse , JsonResponse
import calendar ,random
from datetime import date
from administration.models import Employee,EmployeeStatus,workHours ,SwapRequest ,Group,GroupStatus\
    ,Log,Certification,Employee_Certification,Brief
from django.contrib import messages
from django.core.paginator import Paginator
from administration.utils import set_group_status
import datetime



# @method_decorator([login_required,manager_required] , name='dispatch')
class SignUpView(TemplateView):
    template_name = 'registration/signup.html'


@login_required
@manager_required
def Pre_Manager_Home(request):
    groups = Group.objects.all()
    # done swap
    doneSwaps =  SwapRequest.objects.filter(answer=True,admin_answer=True).count()
    # groups numbers
    groupsNumber = groups.count()
    # employee number
    employeeNumber = Employee.objects.all().count()
    # each group hours
    group_hours =[]
    for group in groups:
        group_hours.append(group.all * 8)
    # recent done swaps
    recent_swaps=SwapRequest.objects.filter(answer=True,admin_answer=True).order_by('-pk')[:5]
    # know in each shift
    hour = datetime.datetime.now().hour
    shift=0
    day=date.today()
    if hour  in range(6,14):
        shift = 1
    elif hour in range(14,22):
        shift = 2
    elif hour in [22,23]:
        shift = 3
    elif hour  in range(0,6):
        shift = 3
        day = day - datetime.timedelta(days=1)
    # current shift
    current_shift = GroupStatus.objects.filter(day= day , type=int(shift))
    #  get next shift
    if shift == 3 :
        next_shift = GroupStatus.objects.filter(day= day + datetime.timedelta(days=1)  , type=1)
    else:
        next_shift = GroupStatus.objects.filter(day= day , type=int(shift+1))

    # recent logs
    recent_logs=Log.objects.all().order_by('-pk')[:6]
    # number of employee in each role
    employees_num=[
        Employee.objects.filter(level=1).count(),
        Employee.objects.filter(level=2).count(),
        Employee.objects.filter(level=3).count(),
        Employee.objects.filter(level=4).count(),
        Employee.objects.filter(level=5).count(),
    ]
    print("=====================done===========")
    print(employees_num)
    swaps = SwapRequest.objects.filter(admin_request=False, answer=True)
    print('====================')
    print(swaps)
    # get certifctions need to teel admin
    certifications = Employee_Certification.objects.all()
    certifications_after = []
    # for certification in certifications:
    for cert in certifications:
        end_date = cert.start_date + datetime.timedelta(days=365 * cert.years)
        print()
        day_remind = end_date - date.today()
        if day_remind.days in range(-30, 31):
            certifications_after.append({
                'employee': cert.employee,
                'days': day_remind.days,
                'certification': cert.certification
            })

    # get certification_request
    certification_request1 = Employee_Certification.objects.filter(admin_accept = False)
    certification_request2 = Employee_Certification.objects.filter(admin_accept = True,update=True)

    # get top 5 empployees
    Top_employee = Employee.objects.order_by('morring' and 'afternoon' and 'evening')[:5]

    # get lower 5 employeees
    lower_employee = Employee.objects.order_by('-morring' and '-afternoon' and '-evening')[:5]



    return render(request, 'work/manager/pre_home.html',{
        'doneSwaps':doneSwaps,
        'groupsNumber':groupsNumber,
        'employeeNumber':employeeNumber,
        'recent_swaps':recent_swaps,
        'current_shift':current_shift,
        'recent_logs':recent_logs,
        'employees_num':employees_num,
        'group_hours':group_hours,
        'swaps':swaps,
        'certification':certifications_after,
        'certification_request1':certification_request1,
        'certification_request2':certification_request2,
        'next_shift':next_shift,
        'Top_employee':Top_employee,
        'lower_employee':lower_employee
    })







# @method_decorator([login_required,manager_required] , name='dispatch')
class ManagerSignUpView(CreateView):
    model = User
    form_class = ManagerSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Signup as a Manager'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('signup')


def home(request):
    if request.user.is_authenticated:
        if request.user.is_empolyee:
            return redirect('employee:home_to')#employee home page
        else:
            return redirect('manager:home')#manager home page
    return  render(request,'work/home.html')#home pag


@login_required
@manager_required
def Manager_Home(request, num):
    # delete logs 30 days before
    Log.objects.filter(day=datetime.datetime.today() + datetime.timedelta(days=30)).delete()

    if num == 1:
        if request.method == 'POST':
            month = (date.today().month) + 1
            month_type = 1
        else:
            month_type = 0
            month = date.today().month
        year=date.today().year
        days=[]
        data=[]
        day_types = [
            None,
            None,
            None,
            None,
            None,
        ]

    #     collecting data for months
    # first get all groups
        groups=Group.objects.all()
        month_range = calendar.monthrange(year, month)
        print(month_range)
        for i in range(month_range[1]):
            print("********")
        for i in range(month_range[1]):
            print("-------------")
            day = date(year, month, i + 1)
            # add this day to those month days
            days.append(day)
            for group in groups:
                if GroupStatus.objects.filter(group=group,day=day).count()==0:
                    # create new shift to this group
                    group_type = GroupStatus.objects.create(group=group,day=day)
                    set_group_status(group_type,6)

                else:
                    group_type = GroupStatus.objects.get(group=group,day=day)
                    #add this shift successfully in this day
                    if group_type.type == 1:
                        day_types[0] = group_type
                    elif group_type.type == 2:
                        day_types[1] = group_type
                    elif group_type.type == 3:
                        day_types[2] = group_type
                    elif group_type.type == 4:
                        day_types[3] = group_type
                    elif group_type.type == 5:
                        day_types[4] = group_type
                    # elif group_type.type == 6:
                    #     day_types[5] = group_type
            print("000000000000")
            data.append({
                            'day': day,
                            'day_types': day_types
                        })
            # reset this day_types
            day_types = [
                None,
                None,
                None,
                None,
                None,
            ]
        print(data)
        # paginator = Paginator(data, 7)  # Show 10 Question per page
        # page = request.GET.get('page')
        # data = paginator.get_page(page)

        print("=========================")
        return render(request, 'work/manager/manager_home.html', {
                'days': days,
                'data': data,
                'groups': groups,
                'month_type': month_type
            })
    elif num == 2:
        return render(request, 'work/manager/workhours_manage.html')





@login_required
@manager_required
def Manager_Home1(request,num):
    if num == 1:
        if request.method == 'POST':
            month = (date.today().month) +1
            month_type=1
        else:
            month_type=0
            month=date.today().month
        year = date.today().year
        days=[]
        data=[]
        day_types=[]
        # collecting data with the month in work
        employees=Employee.objects.all()
        month_range=calendar.monthrange(year,month)
        for i in range(month_range[1]):
            day=date(year,month,i+1)
            # add this day to those month days
            days.append(day)
            for emp in employees:
                if EmployeeStatus.objects.filter(employee=emp,day=day).count() == 0 :
                    #     create defualt object to this employee in this day
                    emp_type=EmployeeStatus.objects.create(employee=emp,day=day)
                else:
                    # get the object belong to this employee
                    emp_type=EmployeeStatus.objects.get(employee=emp,day=day)
                # add the object to this day types
                day_types.append(emp_type)
            data.append({
                'day':day,
                'day_types':day_types
                })
            day_types=[]
            # add those day types to all type
        swaps=SwapRequest.objects.filter(admin_request=False,answer=True)
        paginator = Paginator(data, 5)  # Show 10 Question per page
        page = request.GET.get('page')
        data = paginator.get_page(page)
        return render(request,'work/manager/manager_home.html',{
            'days' : days,
            'data':data,
            'employees':employees,
            'month_type':month_type,
            'swaps' : swaps
        })
    elif num == 2 :
        return render(request,'work/manager/workhours_manage.html')





@login_required
@manager_required
def Change_Status(request,type_num,status_pk,shift_type,day):
    tr_number=None
    group_name = None
    day_pattren = day.split()
    temp_day = date(int(day_pattren[2]),int(day_pattren[1]),int(day_pattren[0]))
    # prepare the shift
    temp_shift = None
    if(status_pk == "n"):
        temp_shift =None
    else:
        temp_shift = GroupStatus.objects.get(pk=status_pk)
    # prepare the group
    temp_group=None
    if type_num == 1 :
        temp_group=Group.objects.get(name="A")
    elif type_num == 2 :
        temp_group=Group.objects.get(name="B")
    elif type_num == 3 :
        temp_group=Group.objects.get(name="C")
    elif type_num == 4 :
        temp_group=Group.objects.get(name="D")
    elif type_num == 5 :
        temp_group=Group.objects.get(name="E")

    # check if the request is not valid the same thing inthe datebase
    if not temp_group and not temp_shift:
        print("333333333333")
        return JsonResponse({
            "success":True,
            "tr_number" : tr_number,
            "group" : group_name
        },status=200)
    elif temp_shift and temp_shift.group == temp_group:
        print("herrrrrrrrr")
        return JsonResponse({
            "success": True,
            "tr_number" : tr_number,
            "group" : group_name
        }, status=200)
    else:
        #there is change
        if not temp_group:
            #just set this shift off day
            set_group_status(temp_shift,6)
        elif not temp_shift:
            temp_shift=GroupStatus.objects.get(day=temp_day,group=temp_group)
            tr_number=temp_shift.type
            print(temp_shift ,temp_group , temp_shift.group)
            temp_shift.type = shift_type
            temp_shift.save()
            print("h888888888")
            print("=====================")
            print(temp_day)
            set_group_status(temp_shift,shift_type)
        else:
            # two way shift
            if GroupStatus.objects.filter(group=temp_group,day=temp_day).count() == 0:
                temp_shift.group = temp_group
                temp_shift.save()
                set_group_status(temp_shift,temp_shift.type)
                print("666666666666666666")
            else:
                anther_shift = GroupStatus.objects.get(group=temp_group,day=temp_day)
                tr_number=anther_shift.type
                group_name=temp_shift.group.name
                anther_shift.group = temp_shift.group
                temp_shift.group = temp_group
                set_group_status(anther_shift,anther_shift.type)
                set_group_status(temp_shift,temp_shift.type)
                anther_shift.save()
                temp_shift.save()
                print("4444444444444444")

    return JsonResponse({
        "success": True,
        "tr_number": tr_number,
        "group": group_name
    }, status=200)




@login_required
@manager_required
def Work_Hours_show(request):
    if request.method == 'POST':
        print('====================')
        print(request.POST)
        if not request.POST['date']:
            messages.error(request,"must select date")
            return redirect('manager:home_to',2)
        day_pattern=request.POST['date'].split('-')
        if int(day_pattern[0]) != date.today().year or int(day_pattern[1])-date.today().month > 1 or int(day_pattern[1])<date.today().month  :
            messages.warning(request, "please , select valid date")
            return redirect('manager:home_to',2 )
        if int(day_pattern[0]) == date.today().year and int(day_pattern[1])==date.today().month and  int(day_pattern[2])< date.today().day:
            messages.warning(request, "please select valid date")
            return redirect('manager:home_to', 2)


        data=[]
        day=date(int(day_pattern[0]),int(day_pattern[1]),int(day_pattern[2]))
        shift=int(request.POST['shift'])
        Shift_hours = EmployeeStatus.objects.filter(day=day,type=shift)
        group_shift =  GroupStatus.objects.get(day=day,type=shift)
        # collect the Work hours from database for each empolyee
        for ele in Shift_hours:
            if workHours.objects.filter(status=ele).count() == 0:
                #     create default object
                work_object = workHours.objects.create(status=ele)
            else:
                #        get the object existed in database
                work_object = workHours.objects.get(status=ele)
            data.append({
                'shift':ele,
                'workhour':work_object
            })

        return render(request,'work/manager/shiftworks.html',{
            'type':shift,
            'data':data,
            'group_shift':group_shift
        })
    else:
        return redirect('manager:home')


@login_required
@manager_required
def Work_Hours_manage(request,hour_num,hour_type,work_pk):
    work = workHours.objects.get(pk=work_pk)
    breakNum=work.breakNum
    if breakNum == 2 and hour_type == 0:
    #     not valid
        return JsonResponse({'success':False},status=200)
    elif breakNum == 0 and hour_type ==1 :
        print("noooooooooooooooooo")
        return JsonResponse({'success':True},status=200)
    if hour_type == 0:
        if hour_num == 1:
             if work.one:
                 work.one = False
                 work.breakNum = breakNum + 1
        elif hour_num == 2:
            if work.two:
                work.two = False
                work.breakNum = breakNum + 1
        elif hour_num == 3:
            if work.three:
                work.three = False
                work.breakNum = breakNum + 1

        elif hour_num == 4:
            if work.four:
                work.four = False
                work.breakNum = breakNum + 1
        elif hour_num == 5:
            if work.five:
                work.five = False
                work.breakNum = breakNum + 1
        elif hour_num == 6:
            if work.six:
                work.six = False
                work.breakNum = breakNum + 1
        elif hour_num == 7:
            if work.seven:
                work.seven = False
                work.breakNum = breakNum + 1
        elif hour_num == 8:
            if work.eight:
                work.eight = False
                work.breakNum = breakNum + 1
    #     ============================================

    else:
        if hour_num == 1:
             if not work.one:
                 work.one = True
                 work.breakNum = breakNum - 1
        elif hour_num == 2:
            if not work.two:
                work.two = True
                work.breakNum = breakNum -1
        elif hour_num == 3:
            if not work.three:
                work.three = True
                work.breakNum = breakNum - 1

        elif hour_num == 4:
            if not work.four:
                work.four = True
                work.breakNum = breakNum - 1
        elif hour_num == 5:
            if not work.five:
                work.five = True
                work.breakNum = breakNum - 1
        elif hour_num == 6:
            if not work.six:
                work.six = True
                work.breakNum = breakNum - 1
        elif hour_num == 7:
            if not work.seven:
                work.seven = True
                work.breakNum = breakNum - 1
        elif hour_num == 8:
            if not work.eight:
                work.eight = True
                work.breakNum = breakNum - 1
    work.save()
    return JsonResponse({"success": True}, status=200)



@login_required
@manager_required
def reports_show(request):
    year=date.today().year
    month = date.today().month
    employees_names=[]
    hours=[]
    employees = Employee.objects.all()
    for emp in employees:
        employees_names.append(emp.user.username)
        hours.append(emp.group.all * 8)
        # hours.append(get_work_hour(emp,year= year, month= month )[0])
    return render(request,'work/manager/reports.html',{
        'employees_names':employees_names,
        'employees':employees,
        'hours':hours,
        'year':year
    })


@login_required
@manager_required
def report_show(request):
    month=date.today().month
    year=date.today().year
    if request.method == 'POST' :
        if not (request.POST['year'] and request.POST['month']):
            messages.error(request,"must select date")
            return redirect('manager:reports')


        day_pattern=[request.POST['year'],request.POST['month']]
        if int(day_pattern[0]) != year or abs(int(day_pattern[1])-month) > 2 :
            messages.warning(request, "please select valid date")
            return redirect('manager:reports')

        emp=Employee.objects.get(pk=request.POST['employee'])
        report=get_work_hour(emp,int(day_pattern[0]),int(day_pattern[1]))
        return render(request,'work/manager/report_show.html',{
            'hour_num':report[0],
            'break_num': report[1],
            'work_day':report[2],
            'swap_day':report[3],
            'employee':emp,
            'date':f"{day_pattern[1]} / {day_pattern[0]}"
        })


    else:
        return redirect('home')

def get_work_hour(emp:Employee,year:int,month:int):
    month_range = calendar.monthrange(year,month)
    days=[]
    data=[]
    for i in range(month_range[1]):
        day= date(year,month,i+1)
        if EmployeeStatus.objects.filter(employee=emp,day=day).count() == 0 :
            temp=EmployeeStatus.objects.create(employee=emp,day=day)
        else:
            temp = EmployeeStatus.objects.get(employee=emp,day=day)
        days.append(day)
        data.append({
            'shift' : temp,
            'employee':emp
        })

    num = 0
    breaks = 0
    work_days = 0
    swap_num = 0
    for ele in data :
        print("++++++++++++++++++++++++++m",ele)
        temp=ele['shift']
        if not hasattr(temp, 'workhours'):
            workHours.objects.create(status=temp)
        if temp.type < 4:
            work_days = work_days + 1
            if temp.workhours.breakNum == 0 :
                num = num + 8
            elif temp.workhours.breakNum == 1:
                num =num +7
                breaks =breaks+1
            else:
                num = num + 6
                breaks =breaks + 2

        if SwapRequest.objects.filter(owner=emp , shift=temp , admin_answer = True).count() != 0:
                print("::::::::::::::::::::::::::::::::::")
                swap_num=swap_num+1


    print(":::::::::::::::::::::::::",swap_num)
    return [num,breaks,work_days,swap_num]


@login_required
@manager_required
def Swap_Accept(request,pk):
    swap = SwapRequest.objects.get(pk=pk)
    swap.admin_request=True
    swap.admin_answer=True
    user_shift=EmployeeStatus.objects.get(employee=swap.users.all()[0],day=swap.shift.day)
    user_shift.type=swap.shift.type
    user_shift.save()
    swap.shift.type = 6
    swap.shift.called = False
    swap.shift.save()
    swap.save()
    messages.success(request,"the swaping Done Successfully ")
    return redirect('manager:home')





@login_required
@manager_required
def Swap_Refuse(request, pk):
    swap = SwapRequest.objects.get(pk=pk)
    swap.admin_request=True
    swap.admin_answer=False
    swap.save()
    messages.info(request,"the swaping  refused !")
    return redirect('manager:home')

@login_required
@manager_required
def delete_show(request):
    employees=Employee.objects.all()
    groups=Group.objects.all()
    print(groups)
    return render(request,'work/manager/employee_delete.html',{
        'employees':employees,
        'groups':groups
    })

@login_required
@manager_required
def addgroup(request):
    if request.method == 'POST':
        print(request.POST)
        if Group.objects.filter(name=request.POST['name']).count() != 0:
            messages.error(request,"please enter anther name !!")
        else:
            Group.objects.create(name=request.POST['name'])
            messages.success(request,"group add successfully")
        return redirect('manager:group_signup')
    else:
        return render(request,'work/manager/addgroup.html')

@login_required
@manager_required
def add_Certification(request):
    if request.method == 'POST':
        print(request.POST)
        if Certification.objects.filter(name=request.POST['name']).count() != 0:
            messages.error(request,"sorry , there ia anther certification with the same name")
        else:
            Certification.objects.create(name=request.POST['name'])
            messages.success(request,"group add successfully")
        return redirect('manager:add_Certification')
    else:
        return render(request,'work/manager/add_Certification.html')

@login_required
@manager_required
def employee_certification(request,pk):
    if request.method == 'POST':
        print(request.POST)
        if int(request.POST['years']) not in [1,2,3,4,5]:
            messages.warning(request,"years must between 1, 5 !!")
        else:
            #start here
            day_pattern=request.POST['start_date'].split('-')

            employee = Employee.objects.get(id=request.POST['pk'])
            day=date(int(day_pattern[0]),int(day_pattern[1]),int(day_pattern[2]))
            print(day)
            certification = Certification.objects.get(pk=request.POST['certification'])
            if Employee_Certification.objects.filter(employee=employee,certification=certification)\
                    .count() == 0:
                Employee_Certification.objects.create(
                    employee=employee,
                    certification=certification,
                    years=request.POST['years'],
                    start_date=day
                )
                messages.success(request,"certification added successfully")
            else:
                temp=Employee_Certification.objects.get(employee=employee,certification=certification)
                temp.years=request.POST['years']
                temp.start_date=day
                temp.save()
                messages.success(request,"this certification updated successfully!!")
        return redirect('manager:employee_certification',pk)
    else:
        certifications = Certification.objects.all()
        return render(request,'work/manager/employee_certification.html',{
            "pk":pk,
            "certifications":certifications
        })


@login_required
@manager_required
def set_shifts(request):
    year=date.today().year
    month=date.today().month
    # get all group
    groups=Group.objects.all()
    for group in groups:
        group.all=0
        group.morring=0
        group.evening=0
        group.afternoon=0
        group.save()
    groups = Group.objects.all()

    # get month range
    month_range=calendar.monthrange(year,month)
    for i in range(month_range[1]):
        day = date(year, month, i + 1)

        temp_groups = list(groups).copy()
        # select first 3 shifts
        for i in [1,2,3,4]:
            done=None
            while not done :
                print(done)
                print("===helllo====")
                group = random.choice(temp_groups)
                if GroupStatus.objects.filter(group=group, day=day).count() == 0:
                    # create new shift to this group
                    group_type = GroupStatus.objects.create(group=group, day=day)
                else:
                    group_type = GroupStatus.objects.get(group=group, day=day)
                if i == 1:
                    if group.morring < 10 and  group.all < 24:
                        print("============1")
                        group.morring += 1
                        group.all += 1
                        group_type.type = i
                        set_group_status(group_type,i)
                        group.save()
                        group_type.save()
                        done = True
                    else:
                        done = None
                elif i == 2:
                    if group.afternoon < 10 and  group.all < 24:
                        print("======2")
                        group.afternoon += 1
                        group.all += 1
                        group_type.type = i
                        set_group_status(group_type,i)
                        group.save()
                        group_type.save()
                        done = True
                    else:
                        done = None
                elif i == 3 :
                    if group.evening < 10 and  group.all < 24:
                        print("=======3")
                        group.evening += 1
                        group.all += 1
                        group_type.type = i
                        set_group_status(group_type,i)
                        group.save()
                        group_type.save()
                        done = True
                    else:
                        done = None
                else:
                    group_type.type=i
                    set_group_status(group_type, i)
                    group.save()
                    group_type.save()
                    done=True
            temp_groups.remove(group)
        choices = [5,6]
        for temp in temp_groups:
            choice = random.choice(choices)
            if GroupStatus.objects.filter(group=temp, day=day).count() == 0:
                # create new shift to this group
                group_type = GroupStatus.objects.create(group=temp, day=day)
            else:
                group_type = GroupStatus.objects.get(group=temp, day=day)

            group_type.type =choice
            set_group_status(group_type, choice)
            group_type.save()
            choices.remove(choice)

    msg = ' done successfully , group A { morring : '+ str(groups[0].morring*8) + ' , afternoon : '+ str(groups[0].afternoon*8) + ' , evening : '+  str(groups[0].evening*8) +' , ALL : '+ str(groups[0].all*8) + '}'\
          +'group B { morring : '+ str(groups[1].morring*8) + ' , afternoon : '+ str(groups[1].afternoon*8) + ' , evening : '+ str(groups[1].evening*8) +' , ALL : '+ str(groups[1].all*8) + '}'\
          +'group C { morring : '+ str(groups[2].morring*8) + ' , afternoon : '+ str(groups[2].afternoon*8) + ' , evening : '+ str(groups[2].evening*8) +' , ALL : '+ str(groups[2].all*8) + '}'\
          +'group D { morring : '+ str(groups[3].morring*8) + ' , afternoon : '+ str(groups[3].afternoon*8) + ' , evening : '+ str(groups[3].evening*8) +' , ALL : '+ str(groups[3].all*8) + '}'\
          +'group F { morring : '+ str(groups[4].morring*8) + ' , afternoon : '+ str(groups[4].afternoon*8) + ' , evening : '+ str(groups[4].evening*8) +' , ALL : '+ str(groups[4].all*8) + '}'\

    print(msg)
    # done
    messages.success(request,msg)
    return redirect('manager:home_to' , 1)

    return HttpResponse("done")

@login_required
@manager_required
def filter_employees(request):
    if request.method == 'POST':
        print('=============================')
        print(request.POST)
        employees = Group.objects.get(pk=request.POST['group']).employees.all()
        groups = Group.objects.all()
        print(groups)
        return render(request, 'work/manager/employee_delete.html', {
            'employees': employees,
            'groups': groups
        })
    else:
        return redirect('home')


@login_required
@manager_required
def accept_certification(request,pk):
    select_emp_cert = Employee_Certification.objects.get(pk=pk)
    if select_emp_cert.admin_accept:
        select_emp_cert.update = False
    else:
        select_emp_cert.admin_accept = True
    select_emp_cert.save()
    print('=======accept======')
    return redirect('home')


@login_required
@manager_required
def refuse_certification(request,pk):
    select_emp_cert = Employee_Certification.objects.get(pk=pk)
    if select_emp_cert.admin_accept:
        select_emp_cert.years=select_emp_cert.prev_years
        select_emp_cert.start_date = select_emp_cert.prev_start_date
        select_emp_cert.update =False
        select_emp_cert.save()
    else:
        select_emp_cert.delete()
    print('======refuse=======')
    return redirect('home')


@login_required
@manager_required
def addbrief(request):
    if request.method == 'POST':
        print(request.POST)
        all_Briefs = Brief.objects.filter(shift=int(request.POST['shift']),employee=int(request.POST['employee']))
        if all_Briefs.count() == 1 :
            all_Briefs = Brief.objects.get(shift=int(request.POST['shift']), employee=int(request.POST['employee']))
            all_Briefs.text += " , "
            all_Briefs.text += request.POST['Breif']
            all_Briefs.save()
        else:
            all_Briefs=Brief()
            all_Briefs.text = request.POST['Breif']
            all_Briefs.shift=GroupStatus.objects.get(pk=int(request.POST['shift']))
            all_Briefs.employee=Employee.objects.get(pk=int(request.POST['employee']))
            all_Briefs.save()
        return redirect('manager:work_hour_update',request.POST['shift'])
    else:
        return redirect('home')


@login_required
@manager_required
def work_hour_update(request,pk):
    group_shift = GroupStatus.objects.get(pk=pk)
    Shift_hours = EmployeeStatus.objects.filter(day=group_shift.day, type=group_shift.type)
    shift = group_shift.type
    data=[]
    for ele in Shift_hours:
        if workHours.objects.filter(status=ele).count() == 0:
            #     create default object
            work_object = workHours.objects.create(status=ele)
        else:
            #        get the object existed in database
            work_object = workHours.objects.get(status=ele)
        data.append({
            'shift': ele,
            'workhour': work_object
        })
    #get briefs
    briefs=Brief.objects.filter(shift=pk)
    return render(request, 'work/manager/shiftworks.html', {
        'type': shift,
        'data': data,
        'group_shift': group_shift,
        'briefs':briefs
    })


