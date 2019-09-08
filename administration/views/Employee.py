from administration.decorators import manager_required ,employee_required
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from administration.models import User ,EmployeeStatus,Employee,SwapRequest\
    ,Log,Group,Certification,Employee_Certification,GroupStatus,Brief
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import redirect
from administration.forms import EmployeeSignupForm
from django.http import   JsonResponse
from django.shortcuts import render
from datetime import date
import calendar,datetime




@method_decorator([login_required,manager_required] , name='dispatch')
class EmployeeSignupView(CreateView):
    model = User
    form_class = EmployeeSignupForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'add new employee'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form.save()
        messages.success(self.request,'Done! , Add new Employee successfully .......')
        return redirect('employee_signup')


@login_required
@employee_required
def Pre_Employee_Home(request):
    groups= Group.objects.all()
    # hours
    hours=request.user.employee.group.all * 8
    # swaps request
    swap_reqest = SwapRequest.objects.filter(owner=request.user.employee).count()
    #  your done swaps
    swap_done = SwapRequest.objects.filter(owner=request.user.employee,answer=True,admin_answer=True).count()
    # recent done swaps
    recent_swaps = SwapRequest.objects.filter(answer=True, admin_answer=True).order_by('-pk')[:5]
    # each group hours
    group_hours = []
    for group in groups:
        group_hours.append(group.all * 8)
    employees_num = [
        Employee.objects.filter(level=1).count(),
        Employee.objects.filter(level=2).count(),
        Employee.objects.filter(level=3).count(),
        Employee.objects.filter(level=4).count(),
        Employee.objects.filter(level=5).count(),
    ]
    swapRequest= request.user.employee.SwapRequests.filter(answer=False,admin_request=False)
    live = False
    today = datetime.date.today()
    day = datetime.timedelta(days=1)
    yesterday = today - day
    day_shift = EmployeeStatus.objects.get(day=date.today(), employee=request.user.employee)
    day_before = EmployeeStatus.objects.get(day=yesterday, employee=request.user.employee)
    if day_shift.type <= 3 or day_before.type == 3:
        # you are live today
        if (day_shift.type == 1 and datetime.datetime.now().hour in range(6, 14)) or \
                (day_shift.type == 2 and datetime.datetime.now().hour in range(14, 22)) or \
                (day_before.type == 3 and (datetime.datetime.now().hour in [0, 1, 2, 3, 4, 5])) or \
                (day_shift.type == 3 and (datetime.datetime.now().hour in [22, 23])):
            live = True;
    # get group shift
    if datetime.datetime.now().hour < 6:
        group_shift=GroupStatus.objects.get(day=yesterday,type=3)
    elif datetime.datetime.now().hour in range(6,14):
        group_shift=GroupStatus.objects.get(day=today,type=1)
    elif datetime.datetime.now().hour in range(14,22):
        group_shift=GroupStatus.objects.get(day=today,type=2)
    elif datetime.datetime.now().hour in range(22,23):
        group_shift=GroupStatus.objects.get(day=today,type=3)


    if datetime.datetime.now().hour > 6:
        select_day = today
    else:
        select_day = today + day
    next_shift = EmployeeStatus.objects.get(day=select_day,employee=request.user.employee)
    while next_shift.type > 3:
        select_day += day
        next_shift = EmployeeStatus.objects.get(day=select_day, employee=request.user.employee)
    # get Certifications
    tempCertifications=Employee_Certification.objects.filter(employee=request.user.employee , admin_accept=True ,update=False)
    Certifications=[]
    for cer in tempCertifications:
        Certifications.append({
            'name':cer.certification.name,
            'day':cer.start_date + datetime.timedelta(days=365*cer.years)
        })
    hour = datetime.datetime.now().hour
    shift = 0
    day = date.today()
    if hour in range(6, 14):
        shift = 1
    elif hour in range(14, 22):
        shift = 2
    elif hour in [22, 23]:
        shift = 3
    elif hour in range(0, 6):
        shift = 3
        day = day - datetime.timedelta(days=1)
    # current shift
    current_shift = GroupStatus.objects.filter(day=day, type=int(shift))
    # get breifs
    breifs = Brief.objects.filter(employee=request.user.employee , shift=current_shift[0])
    print("================")
    print(breifs.count())
    print("================")
    return render(request,'work/employee/pre_home.html',{
       'employees_num': employees_num,
        'group_hours':group_hours,
        'recent_swaps':recent_swaps,
        'swap_done':swap_done,
        'hours':hours,
        'swap_reqest':swap_reqest,
        'swaps': swapRequest,
        'live': live,
        'next_shift':next_shift,
        'Certifications':Certifications,
        'group_shift':None,
        'current_shift':current_shift,
        'breifs':breifs
    })

@login_required
@employee_required
def Employee_Home(request):

    year = date.today().year
    month = date.today().month
    data=[]
    month_range=calendar.monthrange(year,month)
    for i in range(month_range[1]):
        day = date(year, month, i + 1)
        if EmployeeStatus.objects.filter(employee=request.user.employee, day=day).count() == 0:
            #     create defualt object to this employee in this day
            emp_type = EmployeeStatus.objects.create(employee=request.user.employee, day=day)
        else:
            # get the object belong to this employee
            print("pppppppppppppppppppp")
            emp_type = EmployeeStatus.objects.get(employee=request.user.employee, day=day)
            print(emp_type)
        data.append({
            'day': day,
            'day_types': emp_type
        })
    #     check if there any swap request
    # prepare log data


    return render(request,'work/employee/employee_home.html',{
            'data':data,
        })


@login_required
@employee_required
def Swap_Request(request,pk):
    shift = EmployeeStatus.objects.get(pk=pk)
    if not SwapRequest.objects.filter(shift = shift).count() == 0 :
        messages.info(request,"your request in progress  , please wait others employee answer")
        return redirect('employee:home')
    else:
        # check if there is employee free


        if EmployeeStatus.objects.filter(day=shift.day, type=4).count() == 0:
            messages.warning(request,"sorry threre is no employee free to take your shift")
            return redirect('employee:home')
        else:
            num=0
            avalable_num = EmployeeStatus.objects.filter(day=shift.day, type=4)
            for ele in avalable_num:
                if ele.employee.level==request.user.employee.level:
                    num=num+1

            if num == 0:
                messages.warning(request, "sorry threre is no employee free to take your shift")
                return redirect('employee:home')


        # collocting avalable Employee
        users_ids=[]
        for ele in EmployeeStatus.objects.filter(day=shift.day,type=4):
            if ele.employee.level == request.user.employee.level:
                users_ids.append(ele.employee.pk)
        users=Employee.objects.filter(pk__in = users_ids)
        # create swap request
        swapRequest = SwapRequest(owner=request.user.employee)
        swapRequest.shift=shift
        swapRequest.save()
        for user in users:
            swapRequest.users.add(user)
        swapRequest.save()
        shift.called = True
        shift.save()
        messages.success(request,'you request sent successfuly , please wait the response !!! ')
        return redirect('employee:home')


@login_required
@employee_required
def Swap_Accept(request,pk):
    swap = SwapRequest.objects.get(pk=pk)
    if swap.answer :
        swap.users.remove(request.user.employee)
        swap.save()
        messages.info(request,"thank you , anther employee take this shift before you")
        return redirect("employee:home")
    else:
        mine_in_quearyset = Employee.objects.filter(pk=request.user.employee.pk)
        swap.answer=True
        swap.users.set(mine_in_quearyset)
        swap.save()
        messages.success(request,"thank you , you  request to take  this shift  , please waiting admin confirm")
        return redirect("employee:home")




@login_required
@employee_required
def Swap_Refuse(request,pk):
    swap = SwapRequest.objects.get(pk=pk)
    swap.users.remove(request.user.employee)
    swap.save()
    return redirect("employee:home")


@login_required
@manager_required
def delete(request, pk):
    User.objects.get(pk=pk).delete()
    return JsonResponse({"success": True}, status=200)

@login_required
@employee_required
def sendlog(request):
    print("===============log===============")
    if request.method == 'POST':
        print("===============log2===============")
        print(request.POST)
        if request.POST['log'] == "":
            messages.warning(request, "sorry , there is no message to send!!")
        else:
            today = datetime.date.today()
            day_step = datetime.timedelta(days=1)
            yesterday = today - day_step
            if datetime.datetime.now().hour in range(0,6):
                day=yesterday
                shift=3
            else:
                day=today
                if datetime.datetime.now().hour in [22,23]:
                    shift=3
                elif datetime.datetime.now().hour in range(6,14):
                    shift=1
                elif datetime.datetime.now().hour in range(14,22):
                    shift=2
            Log.objects.create(
                text=request.POST['log'],
                day=day,
                shift=shift,
                level=request.user.employee.level,
                employee=request.user.employee
            )
            messages.success(request,"your message sent successfully!!")
            return redirect('employee:home')
        return redirect('employee:home')
    else:
        return redirect('employee:home')


@login_required
@employee_required
def showlog(request):
    today = datetime.date.today()
    day = datetime.timedelta(days=1)
    yesterday = today - day
    current_hour = datetime.datetime.now().hour
    if current_hour in range(0,6):
        logs = Log.objects.filter(
            day=yesterday,
            level=request.user.employee.level,
            shift=2
        )
    elif current_hour in range(6,14) :
        logs = Log.objects.filter(
            day=yesterday,
            level=request.user.employee.level,
            shift=3
        )
    elif current_hour in range(14,22):
        logs = Log.objects.filter(
            day=today,
            level=request.user.employee.level,
            shift=1
        )
    elif current_hour in [22,23]:
        logs = Log.objects.filter(
            day=today,
            level=request.user.employee.level,
            shift=2
        )
    print(logs)
    return render(request,'work/employee/showlogs.html',{
        "logs":logs
    })


@login_required
@employee_required
def certification(request):
    if request.method == 'POST':
        print(request.POST)
        if int(request.POST['years']) not in [1, 2, 3, 4, 5]:
            messages.warning(request, "years must between 1, 5 !!")
        else:
            # start here
            day_pattern = request.POST['start_date'].split('-')
            day = date(int(day_pattern[0]), int(day_pattern[1]), int(day_pattern[2]))
            print(day)
            certification = Certification.objects.get(pk=request.POST['certification'])
            if Employee_Certification.objects.filter(employee=request.user.employee, certification=certification) \
                    .count() == 0:
                Employee_Certification.objects.create(
                    employee=request.user.employee,
                    certification=certification,
                    years=request.POST['years'],
                    start_date=day
                )
                messages.success(request, "certification added successfully waiting admin confirm !!")
            else:
                temp = Employee_Certification.objects.get(employee=request.user.employee, certification=certification)
                temp.prev_years=temp.years
                temp.years = request.POST['years']
                temp.prev_start_date = temp.start_date
                temp.start_date = day
                temp.update=True
                temp.save()
                messages.success(request, "this certification updated successfully!! waiting admin confirm ")
        return redirect('employee:certification',)
    else:
        certifications=Certification.objects.all()
        # get his certifications confirmed
        confirm_certifications = Employee_Certification.objects.filter(employee=request.user.employee , admin_accept=True ,update=False)
        return  render(request,'work/employee/certification.html',{
            'certifications':certifications,
            'confirm_certifications':confirm_certifications
        })

