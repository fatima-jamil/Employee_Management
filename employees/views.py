from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .db import get_employees_collection
from .serializers import EmployeeSerializer
import datetime
from bson.objectid import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError

def serialize_employee(doc):
    if not doc:
        return None
    out = dict(doc)
    out['_id'] = str(out.get('_id'))
    jd = out.get('joining_date')
    if isinstance(jd, (datetime.datetime, datetime.date)):
        out['joining_date'] = jd.strftime('%Y-%m-%d')
    return out

class CreateEmployee(APIView):
    def post(self, request):
        data = request.data
        serializer = EmployeeSerializer(data=data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        coll = get_employees_collection()
        doc = serializer.validated_data.copy()

        if 'joining_date' in doc and isinstance(doc['joining_date'], datetime.date):
            doc['joining_date'] = datetime.datetime.combine(doc['joining_date'], datetime.time())

        try:
            result = coll.insert_one(doc)
            new_doc = coll.find_one({'_id': result.inserted_id})
            return Response(serialize_employee(new_doc), status=status.HTTP_201_CREATED)
        except DuplicateKeyError:
            return Response({'error': 'employee_id must be unique'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmployeeDetail(APIView):
    def get(self, request, employee_id):
        coll = get_employees_collection()
        doc = coll.find_one({'employee_id': employee_id})
        if not doc:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serialize_employee(doc))

    def put(self, request, employee_id):
        data = request.data
        if not isinstance(data, dict):
            return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EmployeeSerializer(data=data, partial=True)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        update_data = serializer.validated_data.copy()
        if 'joining_date' in update_data and isinstance(update_data['joining_date'], datetime.date):
            update_data['joining_date'] = datetime.datetime.combine(update_data['joining_date'], datetime.time())

        coll = get_employees_collection()
        if 'employee_id' in update_data and update_data['employee_id'] != employee_id:
            if coll.find_one({'employee_id': update_data['employee_id']}):
                return Response({'error': 'employee_id already exists'}, status=status.HTTP_400_BAD_REQUEST)

        result = coll.update_one({'employee_id': employee_id}, {'$set': update_data})
        if result.matched_count == 0:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        doc = coll.find_one({'employee_id': update_data.get('employee_id', employee_id)})
        return Response(serialize_employee(doc))

    def delete(self, request, employee_id):
        coll = get_employees_collection()
        result = coll.delete_one({'employee_id': employee_id})
        if result.deleted_count == 0:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'detail': 'Employee deleted'}, status=status.HTTP_200_OK)

class ListEmployees(APIView):
    def get(self, request):
        coll = get_employees_collection()
        department = request.query_params.get('department')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        query = {}
        if department:
            query['department'] = department

        skip = (page - 1) * page_size
        cursor = coll.find(query).sort('joining_date', DESCENDING).skip(skip).limit(page_size)
        docs = [serialize_employee(d) for d in cursor]
        total = coll.count_documents(query)
        return Response({
            'page': page,
            'page_size': page_size,
            'total': total,
            'employees': docs
        })

class AvgSalary(APIView):
    def get(self, request):
        coll = get_employees_collection()
        pipeline = [
            {'$group': {'_id': '$department', 'avg_salary': {'$avg': '$salary'}}},
            {'$project': {'_id': 0, 'department': '$_id', 'avg_salary': 1}}
        ]
        res = list(coll.aggregate(pipeline))
        for r in res:
            if isinstance(r.get('avg_salary'), float):
                r['avg_salary'] = round(r['avg_salary'], 2)
        return Response(res)

class SearchBySkill(APIView):
    def get(self, request):
        skill = request.query_params.get('skill')
        if not skill:
            return Response({'error': 'skill query parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        coll = get_employees_collection()
        cursor = coll.find({'skills': skill}).sort('joining_date', DESCENDING)
        docs = [serialize_employee(d) for d in cursor]
        return Response(docs)
