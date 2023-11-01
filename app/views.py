from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.db import connection
from django.utils import timezone
from .unit import DataSet
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.conf import settings

class Client():
    def index(request: HttpRequest):
        # --檢查是否已登入
        user = DataSet.check_user_login(request)
        if user is None:
            return render(request, 'client_base.html', {'user_logout': user})
        else:
            return redirect('/clt/basic/')

    def basic(request: HttpRequest):
        errmesg = None
        succmesg = None
        warnmesg = None
        # --檢查是否已登入
        user = DataSet.check_user_login(request)
        #無登入轉跳至登入頁面
        if user is None:
            return redirect('/clt/')
        #登入狀態進行鋪陳資料
        else:
            if request.method == "GET":
                user = request.session.get('uniform_numbers')
                decide = DataSet.check_info(user)

                warnmesg = decide.get('mesg')
                user_info = decide.get('user_info')
                print(user_info)
                return render(request, 'client_basic_info.html', {'warnmesg': warnmesg , 'user_info': user_info , 'user_logout': user})

            else:#method == "POST"
                user = request.session.get('uniform_numbers')
                rest_name = request.POST.get('rest_name')
                rest_address = request.POST.get('rest_address')
                rest_manager = request.POST.get('rest_manager')
                rest_phone = request.POST.get('rest_phone')
                co_name = request.POST.get('co_name')
                co_address = request.POST.get('co_address')
                co_owner = request.POST.get('co_owner')
                owner_phone = request.POST.get('owner_phone')

                #處理文件上傳
                co_image = request.FILES.get('co_image')
                if co_image :
                    # 獲取檔案類型
                    file_extension = co_image.name.split('.')[-1]
                    # 定義檔案名稱
                    file_name = f"{user}.{file_extension}"
                    #文件路徑
                    destination_path = os.path.join(settings.MEDIA_ROOT, "co_headshot/" + file_name)
                    #文件上傳
                    DataSet.handle_uploaded_file(co_image , destination_path)
                else:
                    file_name = None

                cursor = connection.cursor()

                #判斷是否有該使用者的資料
                #無資料，以新增方式執行
                if not DataSet.user_has_details(user):
                    try:
                        cursor.execute("INSERT INTO client_detail (uniform_numbers, co_image, rest_name, rest_address, rest_manager, rest_phone, co_name, co_address, co_owner, owner_phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(user, file_name, rest_name, rest_address, rest_manager, rest_phone, co_name, co_address, co_owner, owner_phone))
                        #檢查資料是否完整
                        decide = DataSet.check_info(user)
                        warnmesg = decide.get('mesg')
                        user_info = decide.get('user_info')
                        succmesg = "资料新增成功"

                        #若有錯誤警報，進行警報顯示
                        if warnmesg is not None:
                            return render(request, 'client_basic_info.html', {'warnmesg': warnmesg , 'user_info': user_info , 'user_logout': user})
                        else:
                            return render(request, 'client_basic_info.html', {'succmesg': succmesg , 'user_info': user_info , 'user_logout': user})
                    except Exception as err:
                        errmesg = err
                        return render(request, 'client_basic_info.html', {'errmesg': errmesg , 'user_logout': user , 'user_info': user_info})

                #有資料，以更新方式執行
                else:
                    try:
                        if co_image:
                            cursor.execute("UPDATE client_detail SET co_image = %s, rest_name = %s, rest_address = %s, rest_manager = %s, rest_phone = %s, co_name = %s, co_address = %s, co_owner = %s, owner_phone = %s WHERE uniform_numbers = %s",(file_name, rest_name, rest_address, rest_manager, rest_phone, co_name, co_address, co_owner, owner_phone, user))
                        else:
                            cursor.execute("UPDATE client_detail SET rest_name = %s, rest_address = %s, rest_manager = %s, rest_phone = %s, co_name = %s, co_address = %s, co_owner = %s, owner_phone = %s WHERE uniform_numbers = %s",(rest_name, rest_address, rest_manager, rest_phone, co_name, co_address, co_owner, owner_phone, user))

                        decide = DataSet.check_info(user)
                        warnmesg = decide.get('mesg')
                        user_info = decide.get('user_info')
                        succmesg = "资料更新成功"

                        #若有錯誤警報，進行警報顯示
                        if warnmesg is not None:
                            return render(request, 'client_basic_info.html', {'warnmesg': warnmesg , 'user_info': user_info , 'user_logout': user})
                        else:
                            return render(request, 'client_basic_info.html', {'succmesg': succmesg , 'user_info': user_info , 'user_logout': user})
                    except Exception as err:
                        errmesg = err
                        return render(request, 'client_basic_info.html', {'errmesg': errmesg , 'user_logout': user})



    def menu(request: HttpRequest):
        # --檢查是否已登入
        user = DataSet.check_user_login(request)
        if user is None:
            return redirect('/clt/')
        else:
            return render(request, 'client_menu.html', {'user_logout': user})

    def signup(request: HttpRequest):
        errmesg = None
        succmesg = None
        warnmesg = None

        if request.method == "POST":
            uniform_numbers = request.POST.get('uniform_numbers')
            client_password = request.POST.get('psw')
            password_confirm = request.POST.get('password_confirm')
            creattime = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            # print(uniform_numbers, client_password,password_confirm, creattime)

            validator = DataSet(uniform_numbers, client_password, password_confirm)
            errmesg = validator.check_signup()
            if errmesg is not None:
                return render(request, "client_base.html", {'errmesg': errmesg})
            else:
                try:
                    cursor = connection.cursor()
                    cursor.execute("INSERT INTO client (uniform_numbers , client_password , creattime) VALUES (%s , %s , %s)", (
                        uniform_numbers, client_password, creattime))
                    succmesg = '註冊成功，請重新登入'
                    return render(request, 'client_base.html', {'succmesg': succmesg})
                except Exception as err:
                    return render(request, 'client_base.html', {'errmesg': err})

        return render(request, 'client_base.html')

    def login(request: HttpRequest):
        errmesg = None
        succmesg = None
        warnmesg = None
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
