from .models import GroupStatus,Group,Employee,EmployeeStatus

def set_group_status(group_status,status):
    employees = Employee.objects.filter(group=group_status.group)
    for ele in employees:
        if EmployeeStatus.objects.filter(employee=ele,day=group_status.day).count() == 0:
            temp = EmployeeStatus.objects.create(employee=ele,day=group_status.day,type=status)
        else:
            temp = EmployeeStatus.objects.get(employee=ele,day=group_status.day)
            temp.type=status
            if status == 1 :
                ele.morring += 1
            elif status == 2:
                ele.afternoon +=1
            elif status == 3:
                ele.evening += 1
            ele.save()
            temp.save()
    group_status.type=status
    group_status.save()