from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.db import connection
from django.utils import timezone
import re


class DataSet():
    def check_user_login(request):
        user = request.session.get('uniform_numbers')
        if user is None:
            return None  # 使用 None 表示未登入
        return user  # 返回已登入的使用者名稱
