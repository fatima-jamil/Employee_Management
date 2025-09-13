from rest_framework import serializers

class EmployeeSerializer(serializers.Serializer):
    employee_id = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=200)
    department = serializers.CharField(max_length=100)
    salary = serializers.IntegerField(min_value=0)
    joining_date = serializers.DateField(required=False)  # YYYY-MM-DD
    skills = serializers.ListField(child=serializers.CharField(), required=False)
