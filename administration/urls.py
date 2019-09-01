from django.urls import path , include
from administration.views import Manager,Employee


urlpatterns=[
    path('', Manager.home, name='home'),
    path('manager/', include(([
                                  path('', Manager.Pre_Manager_Home, name='home'),
                                  path('<int:num>/', Manager.Manager_Home, name='home_to'),
                                  path('changestatus/<int:type_num>/<status_pk>/<int:shift_type>/<day>', Manager.Change_Status, name='change_status'),
                                  path('manageWork/', Manager.Work_Hours_show , name='work_hour'),
                                  path('WorkHourManage/<int:hour_num>/<int:hour_type>/<int:work_pk>', Manager.Work_Hours_manage , name='work_hour_manage'),
                                  path('reports/', Manager.reports_show , name='reports'),
                                  path('report/', Manager.report_show , name='show_report'),
                                  path('swapaccept/<int:pk>', Manager.Swap_Accept, name='swapaccept'),
                                  path('swaprefuse/<int:pk>', Manager.Swap_Refuse, name='swaprefuse'),
                                  path('employeedelete/', Manager.delete_show, name='employee_delete'),
                                  path('groupadd/', Manager.addgroup, name='group_signup'),
                                  path('add_Certification/', Manager.add_Certification, name='add_Certification'),
                                  path('employee_certification/<pk>', Manager.employee_certification, name='employee_certification'),
                                  path('set_shifts/', Manager.set_shifts, name='set_shifts'),
                                  path('filter_employees/', Manager.filter_employees, name='filter_employees'),
                                  path('accept_certification/<int:pk>', Manager.accept_certification, name='accept_certification'),
                                  path('refuse_certification/<int:pk>', Manager.refuse_certification, name='refuse_certification'),
                                  path('addbrief/', Manager.addbrief, name='addbrief'),
                                  path('work_hour_update/<int:pk>', Manager.work_hour_update, name='work_hour_update'),

                              ], 'administration'), namespace='manager')),
    path('employee/', include(([
                                   path('', Employee.Pre_Employee_Home, name='home_to'),
                                   path('home', Employee.Employee_Home, name='home'),
                                   path('swap/<int:pk>', Employee.Swap_Request, name='swap'),
                                   path('swapaccept/<int:pk>', Employee.Swap_Accept, name='swapaccept'),
                                   path('swaprefuse/<int:pk>', Employee.Swap_Refuse, name='swaprefuse'),
                                   path('delete/<int:pk>', Employee.delete, name='delete'),
                                   path('logs_add/', Employee.sendlog, name='sendLog'),
                                   path('logs_show/', Employee.showlog, name='showlog'),
                                   path('certification/', Employee.certification, name='certification'),
                               ], 'administration'), namespace='employee')),
]