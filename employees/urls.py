from django.urls import path
from .views import CreateEmployee, EmployeeDetail, ListEmployees, AvgSalary, SearchBySkill

urlpatterns = [
    path('employeeslist/', ListEmployees.as_view(), name='list_employees'),
    path('employees/', CreateEmployee.as_view(), name='create_employee'),
    path('employees/avg-salary/', AvgSalary.as_view(), name='avg_salary'),
    path('employees/search/', SearchBySkill.as_view(), name='search_skill'),
    path('employees/<str:employee_id>/', EmployeeDetail.as_view(), name='employee_detail'),
]
