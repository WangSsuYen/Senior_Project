from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.db import connection
from django.utils import timezone
import re
from django.core.files.storage import default_storage , Storage
from django.core.files.base import ContentFile

class DataSet():
    def __init__(self, uniform_numbers, client_password, password_confirm):
        self.uniform_numbers = uniform_numbers
        self.client_password = client_password
        self.password_confirm = password_confirm

    def check_user_login(request):
        user = request.session.get('uniform_numbers')
        if user is None:
            return None  # 使用 None 表示未登入
        return user  # 返回已登入的使用者名稱

    def check_signup(self):
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM client WHERE uniform_numbers = %s", (self.uniform_numbers, ))
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

    def user_has_details(user):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM client_detail WHERE uniform_numbers = %s", (user, ))
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
            return {"mesg" : mesg , "user_info" : user_info}
        elif None in user_info or "" in user_info :
            mesg = "請完整填寫基本資料"
            return {"mesg" : mesg , "user_info" : user_info}
        else:
            return {"user_info" : user_info}


    def handle_uploaded_file(file , destination_path):
        with open(destination_path , 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
    #wb+註解：以二進位格式打開一個文件，允許讀寫數據，如果文件存在則覆蓋，如果文件不存在則創建