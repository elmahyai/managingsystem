from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class Group(models.Model):
    name=models.CharField(max_length=5)
    morring = models.IntegerField(default=0)
    afternoon = models.IntegerField(default=0)
    evening = models.IntegerField(default=0)
    all=models.IntegerField(default=0)

    def __str__(self):
        return self.name

class User(AbstractUser):
    is_manager = models.BooleanField(default=False)
    is_empolyee = models.BooleanField(default=False)


class Employee(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    level_tuple=(
        (1,'ِACC'),
        (2,'APP'),
        (3,'ACC supervisor'),
        (4,'APP supervisor'),
        (5,'Tower supervisor'),
    )
    level=models.IntegerField(
        default=1,
        choices=level_tuple
    )
    age=models.PositiveSmallIntegerField( default=20)
    fullName = models.CharField(max_length=150)
    phoneNumber = models.CharField(max_length=100)
    group=models.ForeignKey(Group,on_delete=models.CASCADE,related_name='employees',null=True )
    morring=models.IntegerField(default=0)
    afternoon=models.IntegerField(default=0)
    evening=models.IntegerField(default=0)

    def __str__(self):
        return self.user.username



class GroupStatus(models.Model):
    type_tuple = (
        (1, 'M'),
        (2, 'A'),
        (3, 'N'),
        (4, 'On Call'),
        (5, 'Sleap'),
        (6, 'OFF Day'),
    )
    day = models.DateField()
    type = models.IntegerField(
        choices=type_tuple,
        default=6
    )
    group=models.ForeignKey(Group,on_delete=models.CASCADE,related_name='shifts')
    brief=models.TextField(null=True)



class EmployeeStatus(models.Model):
    type_tuple = (
        (1, 'M'),
        (2, 'A'),
        (3, 'N'),
        (4, 'On Call'),
        (5, 'Sleap'),
        (6, 'OFF Day'),
    )
    day=models.DateField()
    type=models.IntegerField(
        choices=type_tuple,
        default=6
    )
    employee=models.ForeignKey(Employee,on_delete=models.CASCADE,related_name='cases')
    called=models.BooleanField(default=False)


class workHours(models.Model):
    status=models.OneToOneField(EmployeeStatus,on_delete=models.CASCADE , related_name='workhours')
    breakNum=models.IntegerField(default=0)
    one=models.BooleanField(default=True)
    two=models.BooleanField(default=True)
    three=models.BooleanField(default=True)
    four=models.BooleanField(default=True)
    five=models.BooleanField(default=True)
    six=models.BooleanField(default=True)
    seven=models.BooleanField(default=True)
    eight=models.BooleanField(default=True)


class SwapRequest(models.Model):
    owner=models.ForeignKey(Employee,on_delete=models.CASCADE,related_name='SwapRequestOwners')
    shift=models.OneToOneField(EmployeeStatus,on_delete=models.CASCADE)
    answer=models.BooleanField(default=False)
    admin_request=models.BooleanField(default=False)
    admin_answer=models.BooleanField(default=False)
    users=models.ManyToManyField(Employee,related_name='SwapRequests')






class Certification(models.Model):
    name=models.CharField(max_length=150)
    employees=models.ManyToManyField(
        Employee,
        through='Employee_Certification',
        through_fields=('certification','employee'), # The order is important
    )


class Employee_Certification(models.Model):
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE)
    employee=models.ForeignKey(Employee,on_delete=models.CASCADE)
    start_date=models.DateField()
    years=models.PositiveSmallIntegerField()
    admin_accept=models.BooleanField(default=False)
    update=models.BooleanField(default=False)
    prev_start_date = models.DateField(default=None ,null=True)
    prev_years = models.PositiveSmallIntegerField(default=0)



class Log(models.Model):
    level_tuple = (
        (1, 'ACC'),
        (2, 'APP'),
        (3, 'ACC supervisor'),
        (4, 'APP supervisor'),
        (5, 'Tower supervisor'),
    )
    type_tuple = (
        (1, 'M'),
        (2, 'A'),
        (3, 'N')
    )
    day = models.DateField()
    shift = models.IntegerField(choices=type_tuple)
    text = models.TextField()
    level = models.IntegerField(choices=level_tuple)
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE,related_name='logs')




class Brief(models.Model):
    text=models.TextField(null=True)
    employee=models.ForeignKey(Employee,on_delete=models.CASCADE,related_name='briefs')
    shift = models.ForeignKey(GroupStatus,on_delete=models.CASCADE,related_name='braifs')

