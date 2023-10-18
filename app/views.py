from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.db import connection
from django.utils import timezone


class Client():
    def index(request: HttpRequest):
        return render(request, 'client_base.html')

    def basic(request: HttpRequest):

        if request.session.get('uniform_numbers') is None:
            print(request.session.get('uniform_numbers'))
            return redirect('/clt/')

        return render(request, 'client_basic.html')

    def menu(request: HttpRequest):

        if request.session.get('uniform_numbers') is None:
            print(request.session.get('uniform_numbers'))
            return redirect('/clt/')

        return render(request, 'client_menu.html')

    def signup(request: HttpRequest):
        errmesg = None

        if request.method == "POST":
            uniform_numbers = request.POST.get('uniform_numbers')
            client_password = request.POST.get('psw')
            password_confirm = request.POST.get('password_confirm')
            creattime = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            print(uniform_numbers, client_password,
                  password_confirm, creattime)

            if client_password != password_confirm:
                errmesg = "密碼不相符，請重新輸入。"
                return render(request, 'client_base.html', {'errmesg': errmesg})

            if client_password is None or password_confirm is None or uniform_numbers is None:
                errmesg = "帳號或密碼不可為空，請重新輸入。"
                return render(request, 'client_base.html', {'errmesg': errmesg})

            if len(client_password) < 6 or len(client_password) > 15:
                errmesg = "密碼格式錯誤，密碼長度請設定6到15位。"
                return render(request, 'client_base.html', {'errmesg': errmesg})

            try:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO client (uniform_numbers , password , creattime) VALUES (%s , %s , %s)",
                               (uniform_numbers, client_password, creattime))
                return render(request, 'client_base.html', {'succmesg': '註冊成功，請重新登入'})
            except Exception as err:
                return render(request, 'client_base.html', {'errmesg': err})

        return render(request, 'client_base.html')

    def login(request: HttpRequest):
        return redirect('/clt/menu/')


class Customer():
    def index(request: HttpRequest):
        return render(request, "customer_index.html")

    def login(request: HttpRequest):
        return render(request, "customer_login.html")
