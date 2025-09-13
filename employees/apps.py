from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'employees'

    def ready(self):
        try:
            from .db import get_employees_collection
            coll = get_employees_collection()
            coll.create_index('employee_id', unique=True)
        except Exception as e:
            print("Index creation skipped (Mongo may be offline):", e)
