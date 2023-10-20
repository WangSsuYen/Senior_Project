from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.db import connection
from django.utils import timezone
import re
from .unit import DataSet


class Client():
    def index(request: HttpRequest):
        # --檢查是否已登入
        user = DataSet.check_user_login(request)
        if user is None:
            return render(request, 'client_base.html', {'user_logout': user})
        else:
            return redirect('/clt/basic/')

    def basic(request: HttpRequest):
        # --檢查是否已登入
        user = DataSet.check_user_login(request)
        if user is None:
            return redirect('/clt/')
        else:
            return render(request, 'client_basic.html', {'user_logout': user})

    def menu(request: HttpRequest):
        # --檢查是否已登入
        user = DataSet.check_user_login(request)
        if user is None:
            return redirect('/clt/')
        else:
            return render(request, 'client_menu.html', {'user_logout': user})

    def signup(request: HttpRequest):
        errmesg = None

        if request.method == "POST":
            uniform_numbers = request.POST.get('uniform_numbers')
            client_password = request.POST.get('psw')
            password_confirm = request.POST.get('password_confirm')
            creattime = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            # print(uniform_numbers, client_password,password_confirm, creattime)

            if client_password != password_confirm:
                errmesg = "密碼不相符，請重新輸入。"
                return render(request, 'client_base.html', {'errmesg': errmesg})

            if client_password is None or password_confirm is None or uniform_numbers is None:
                errmesg = "帳號或密碼不可為空，請重新輸入。"
                return render(request, 'client_base.html', {'errmesg': errmesg})

            if len(client_password) < 6 or len(client_password) > 15:
                errmesg = "密碼格式錯誤，密碼長度請設定6到15位。"
                return render(request, 'client_base.html', {'errmesg': errmesg})

            if not re.search(r'[a-zA-Z]', client_password):
                errmesg = "密碼必須包含至少一個英文字母。"
                return render(request, 'client_base.html', {'errmesg': errmesg})

            if len(uniform_numbers) != 8:
                errmesg = "統一編號必須為8個數字"
                return render(request, 'client_base.html', {'errmesg': errmesg})

            try:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO client (uniform_numbers , client_password , creattime) VALUES (%s , %s , %s)", (
                    uniform_numbers, client_password, creattime))
                return render(request, 'client_base.html', {'succmesg': '註冊成功，請重新登入'})
            except Exception as err:
                return render(request, 'client_base.html', {'errmesg': err})

        return render(request, 'client_base.html')

    def login(request: HttpRequest):
        errmesg = None
        if request.method == "POST":
            uniform_numbers = request.POST.get("uniform_numbers")
            client_password = request.POST.get('psw')
            try:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT * FROM client WHERE uniform_numbers = %s AND client_password = %s", (uniform_numbers, client_password))
                user = cursor.fetchone()
                if user is not None:
                    request.session['uniform_numbers'] = uniform_numbers
                    return redirect('/clt/basic/')
                else:
                    errmesg = "帳號或密碼錯誤，請重新輸入。"
            except Exception as err:
                errmesg = err

        return render(request, 'client_base.html', {'errmesg': errmesg})

    def logout(request: HttpRequest):
        request.session.clear()  # 清出所有session資料
        # del request.session['uniform_numbers'] #清除session特定指定資料
        return redirect("/clt/")


class Customer():
    def index(request: HttpRequest):
        return render(request, "customer_index.html")

    def login(request: HttpRequest):
        return render(request, "customer_login.html")
