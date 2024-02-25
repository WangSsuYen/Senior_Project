from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.db import connection
from django.utils import timezone
import re
import os
from django.conf import settings
import googlemaps
from datetime import datetime


class DataSet():
    def __init__(self, sign_status, **kwargs):
        self.sign_status = sign_status
        if self.sign_status == "client":
            self.uniform_numbers = kwargs.get("uniform_numbers")
            self.client_password = kwargs.get("client_password")
            self.password_confirm = kwargs.get("password_confirm")
        elif self.sign_status == "customer":
            self.student_id = kwargs.get("student_id")
            self.email = kwargs.get("customer_email")
            self.customer_password = kwargs.get("customer_password")


    def check_user_login(request):
        user = request.session.get('uniform_numbers')
        if user is None:
            return None  # 使用 None 表示未登入
        return user  # 返回已登入的使用者名稱

    def check_signup(self):
        if self.sign_status == "client":
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM client WHERE uniform_numbers = %s", (self.uniform_numbers, ))
            # 因%s為傳輸文字，因此uniform_numbers須轉為Str
            user = cursor.fetchone()
            if user is not None:
                return "帳號已存在，請重新輸入"

            if self.client_password != self.password_confirm:
                return "密碼不相符，請重新輸入。"

            if self.client_password is None or self.password_confirm is None or self.uniform_numbers is None:
                return "帳號或密碼不可為空，請重新輸入。"

            if len(self.client_password) < 6 or len(self.client_password) > 15:
                return "密碼格式錯誤，密碼長度請設定6到15位。"

            if not re.search(r'[a-zA-Z]', self.client_password):
                return "密碼必須包含至少一個英文字母。"

            if len(self.uniform_numbers) != 8:
                return "統一編號必須為8個數字"

        elif self.sign_status == "customer":
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM customer_detail WHERE student_id = %s OR email = %s", (self.student_id, self.email,))
            user = cursor.fetchone()
            print(user)

            if user is not None :
                return "帳號或信箱已存在，請重新輸入"

            if len(self.customer_password) < 8 or len(self.customer_password) > 20 :
                return "密碼格式錯誤，密碼長度請設定8到20位。"

            if not re.search(r'[a-zA-Z]', self.customer_password):
                return "密碼設定必須包含至少一個英文字母。"

            if not re.search(r'[@]', self.email):
                return "信箱格式錯誤。"


    def user_has_details(user):
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM client_detail WHERE uniform_numbers = %s", (user, ))
        user = cursor.fetchone()
        if user is None:
            return False
        else:
            return True

    def check_info(user):
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM client_detail WHERE uniform_numbers = %s", (user, ))
        user_info = cursor.fetchone()
        if user_info is None:
            mesg = "歡迎蒞臨，請先填寫完整資料再繼續唷!"
            return {"mesg": mesg, "user_info": user_info}
        elif None in user_info or "" in user_info:
            mesg = "請完整填寫基本資料"
            return {"mesg": mesg, "user_info": user_info}
        else:
            return {"user_info": user_info}

    def handle_uploaded_file(file, destination_path):
        with open(destination_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
    # wb+註解：以二進位格式打開一個文件，允許讀寫數據，如果文件存在則覆蓋，如果文件不存在則創建

    def create_user_folder(uniform_numbers):
        # 指定用户文件夹的路径
        user_folder = os.path.join(settings.MEDIA_ROOT, f"menu/{uniform_numbers}/")
    # 检查文件夹是否已存在，如果不存在则创建它
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        return user_folder

    def change_address(rest_info):
        gmaps = googlemaps.Client(key='AIzaSyB1N_PssFMCULrrmOijg6edxKvINwXnyp8')

        for item in rest_info:
            # Geocoding an address
            geocode_result = gmaps.geocode(item['rest_address'])

            if geocode_result and 'geometry' in geocode_result[0]:
                location = geocode_result[0]['geometry']['location']
                item['lat'] =  location['lat']
                item['lng'] =  location['lng']
                # item['location'] = {'lat': location['lat'], 'lng': location['lng']}
            else:
                # Handle the case where geocoding fails
                item['location'] = None

        return rest_info

        # Look up an address with reverse geocoding
        # reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

    #

    # def check_menu(user):
    #     cursor = connection.cursor()
    #     cursor.execute(
    #         "SELECT * FROM menu WHERE uniform_numbers = %s", (user, ))
    #     user_menu = cursor.fetchall()
    #     if user_menu is None:
    #         return False
    #     else:
    #         return user_menu
