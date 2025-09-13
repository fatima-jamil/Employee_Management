from djongo import models

class Employee(models.Model):
    employee_id = models.CharField(max_length=50, unique=True)   
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    salary = models.FloatField()
    skills = models.JSONField()   

    def __str__(self):
        return f"{self.employee_id} - {self.name}"
