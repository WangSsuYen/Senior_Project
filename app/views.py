from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.db import connection
from django.utils import timezone
from .unit import DataSet
from django.template.loader import render_to_string
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
        # 無登入轉跳至登入頁面
        if user is None:
            return redirect('/clt/')
        # 登入狀態進行鋪陳資料
        else:
            if request.method == "GET":
                user = request.session.get('uniform_numbers')
                decide = DataSet.check_info(user)

                warnmesg = decide.get('mesg')
                user_info = decide.get('user_info')
                print(user_info)
                return render(request, 'client_basic_info.html', {'warnmesg': warnmesg, 'user_info': user_info, 'user_logout': user})

            else:  # method == "POST"
                user = request.session.get('uniform_numbers')
                rest_name = request.POST.get('rest_name')
                rest_address = request.POST.get('rest_address')
                rest_manager = request.POST.get('rest_manager')
                rest_phone = request.POST.get('rest_phone')
                co_name = request.POST.get('co_name')
                co_address = request.POST.get('co_address')
                co_owner = request.POST.get('co_owner')
                owner_phone = request.POST.get('owner_phone')

                # 處理文件上傳
                co_image = request.FILES.get('co_image')
                if co_image:
                    # 獲取檔案類型
                    file_extension = co_image.name.split('.')[-1]
                    # 定義檔案名稱
                    file_name = f"{user}.{file_extension}"
                    # 文件路徑
                    destination_path = os.path.join(
                        settings.MEDIA_ROOT, "co_headshot/" + file_name)
                    # 文件上傳
                    DataSet.handle_uploaded_file(co_image, destination_path)
                else:
                    file_name = None

                cursor = connection.cursor()

                # 判斷是否有該使用者的資料
                # 無資料，以新增方式執行
                if not DataSet.user_has_details(user):
                    try:
                        cursor.execute("INSERT INTO client_detail (uniform_numbers, co_image, rest_name, rest_address, rest_manager, rest_phone, co_name, co_address, co_owner, owner_phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (
                            user, file_name, rest_name, rest_address, rest_manager, rest_phone, co_name, co_address, co_owner, owner_phone))
                        # 檢查資料是否完整
                        decide = DataSet.check_info(user)
                        warnmesg = decide.get('mesg')
                        user_info = decide.get('user_info')
                        succmesg = "资料新增成功"

                        # 若有錯誤警報，進行警報顯示
                        if warnmesg is not None:
                            return render(request, 'client_basic_info.html', {'warnmesg': warnmesg, 'user_info': user_info, 'user_logout': user})
                        else:
                            return render(request, 'client_basic_info.html', {'succmesg': succmesg, 'user_info': user_info, 'user_logout': user})
                    except Exception as err:
                        errmesg = err
                        return render(request, 'client_basic_info.html', {'errmesg': errmesg, 'user_logout': user, 'user_info': user_info})

                # 有資料，以更新方式執行
                else:
                    try:
                        if co_image:
                            cursor.execute("UPDATE client_detail SET co_image = %s, rest_name = %s, rest_address = %s, rest_manager = %s, rest_phone = %s, co_name = %s, co_address = %s, co_owner = %s, owner_phone = %s WHERE uniform_numbers = %s", (
                                file_name, rest_name, rest_address, rest_manager, rest_phone, co_name, co_address, co_owner, owner_phone, user))
                        else:
                            cursor.execute("UPDATE client_detail SET rest_name = %s, rest_address = %s, rest_manager = %s, rest_phone = %s, co_name = %s, co_address = %s, co_owner = %s, owner_phone = %s WHERE uniform_numbers = %s", (
                                rest_name, rest_address, rest_manager, rest_phone, co_name, co_address, co_owner, owner_phone, user))

                        decide = DataSet.check_info(user)
                        warnmesg = decide.get('mesg')
                        user_info = decide.get('user_info')
                        succmesg = "资料更新成功"

                        # 若有錯誤警報，進行警報顯示
                        if warnmesg is not None:
                            return render(request, 'client_basic_info.html', {'warnmesg': warnmesg, 'user_info': user_info, 'user_logout': user})
                        else:
                            return render(request, 'client_basic_info.html', {'succmesg': succmesg, 'user_info': user_info, 'user_logout': user})
                    except Exception as err:
                        errmesg = err
                        return render(request, 'client_basic_info.html', {'errmesg': errmesg, 'user_logout': user})

    def menu(request: HttpRequest):
        # --檢查是否已登入
        user = DataSet.check_user_login(request)
        if user is None:
            return redirect('/clt/')
        else:
            if request.method == "GET":
                #檢查成功、失敗訊息(成功、失敗訊息會在頁面顯示一次後消失)
                succmesg = request.session.pop('succmesg' , None)
                errmesg = request.session.pop('errmesg' , None)

                # 抓取網址回傳的類別編號
                category_number = request.GET.get('cn')
                user = request.session.get('uniform_numbers')

                #將SQL語言參數化(有參數與無參數)
                noparameter_query = '''SELECT client_menu.* , meals_category.category_name FROM client_menu JOIN meals_category ON client_menu.meals_category = meals_category.category_number WHERE meals_owner = %s'''
                parameter_query = '''SELECT client_menu.* , meals_category.category_name FROM client_menu JOIN meals_category ON client_menu.meals_category = meals_category.category_number
                                    WHERE client_menu.meals_owner = %s AND client_menu.meals_category = %s'''

                cursor = connection.cursor()
                # 取得菜單資訊,並與菜單類別進行分類
                if category_number is None:
                    cursor.execute(noparameter_query, (user,))
                else:
                    cursor.execute(parameter_query, (user, category_number,))
                column_names = [desc[0] for desc in cursor.description]
                user_menu = [dict(zip(column_names, row)) for row in cursor.fetchall()]
                print(user_menu)


                #抓去餐點類別，並統計類別數量
                cursor.execute("SELECT meals_category.category_name, client_menu.meals_category, COUNT(client_menu.meals_number) AS total FROM client_menu JOIN meals_category  ON client_menu.meals_category = meals_category.category_number WHERE meals_owner = %s GROUP BY meals_category.category_name, client_menu.meals_category ORDER BY client_menu.meals_category  ;" , (user, ))
                count_names = [desc[0] for desc in cursor.description]
                count_list = [dict(zip(count_names, row)) for row in cursor.fetchall()]


                #抓取餐點類別
                cursor.execute("SELECT * FROM meals_category")
                category_names = [desc[0] for desc in cursor.description]
                category_list = [dict(zip(category_names, row)) for row in cursor.fetchall()]


                return render(request, 'client_menu.html',
                {"category_list" : category_list, 'count_list' : count_list, 'user_menu': user_menu, 'user_logout': user, 'succmesg': succmesg , 'errmesg': errmesg})


    def menu_add(request: HttpRequest):
        if request.method == "POST":
            user = request.session.get('uniform_numbers')
            menu_name = request.POST.get('meals_name')
            menu_price = request.POST.get('meals_price')
            menu_type = request.POST.get('meals_status')
            menu_category = request.POST.get('meals_category')
            menu_description = request.POST.get('meals_description')
            menu_discount = request.POST.get('meals_discount')
            menu_discount_values = request.POST.get('meals_discount_values')
            creatime = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            menu_image = request.FILES.get('meals_image')

            #找出最大的菜單編號
            cursor = connection.cursor()
            cursor.execute("SELECT MAX(meals_number) FROM client_menu")
            max_number = cursor.fetchone()[0]
            if max_number is None:
                max_number = 0
            else:
                max_number = int(max_number)
                print(max_number)
            # 處理文件上傳
            if menu_image:
                # 獲取檔案類型
                file_extension = menu_image.name.split('.')[-1]
                # 定義檔案名稱
                file_name = f"{max_number + 1}.{file_extension}"
                # 文件路徑
                destination_path = os.path.join(
                    settings.MEDIA_ROOT, f"menu/{user}/" + file_name)
                # 文件上傳
                DataSet.handle_uploaded_file(menu_image, destination_path)
            else:
                file_name = None

            if menu_discount_values == "":
                menu_discount_values = None


            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO client_menu (meals_number, meals_image, meals_name, meals_price, meals_category, meals_status, meals_description, meals_creattime, meals_owner , meals_discount , meals_discount_values) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s , %s , %s )", (max_number+1, file_name, menu_name, menu_price, menu_category, menu_type,
                                    menu_description, creatime, user , menu_discount , menu_discount_values))
                succmesg = f"{menu_name}新增成功"
                request.session['succmesg'] = succmesg
                return redirect('/clt/menu/')
            except Exception as err:
                errmesg = err
                request.session['errmesg'] = errmesg
                return redirect('/clt/menu/')

    def menu_update(request: HttpRequest):
        if request.method == "POST":
            user = request.session.get('uniform_numbers')
            menu_number = request.POST.get('meals_number')
            menu_name = request.POST.get('meals_name')
            menu_price = request.POST.get('meals_price')
            menu_type = request.POST.get('meals_status')
            menu_category = request.POST.get('meals_category')
            menu_description = request.POST.get('meals_description')
            menu_discount = request.POST.get('meals_discount')
            menu_discount_values = request.POST.get('meals_discount_values')
            updatetime = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            menu_image = request.FILES.get('meals_image')
            # 處理文件上傳
            # 若有資料上傳，則執行更新
            if menu_image:
                # 獲取檔案類型
                file_extension = menu_image.name.split('.')[-1]
                # 定義檔案名稱
                file_name = f"{menu_number}.{file_extension}"
                # 文件路徑
                destination_path = os.path.join(
                    settings.MEDIA_ROOT, f"menu/{user}/" + file_name)
                # 文件上傳
                DataSet.handle_uploaded_file(menu_image, destination_path)
            # 若無資料上傳，則執行原檔案名稱
            else:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT meals_image FROM client_menu WHERE meals_owner = %s AND meals_number = %s", (user, menu_number))
                original_menu = cursor.fetchone()
                # 獲取原圖檔名稱
                if original_menu:
                    file_name = original_menu[0]
                else:
                    file_name = None

            cursor = connection.cursor()
            try:
                cursor.execute("UPDATE client_menu SET meals_image = %s, meals_name = %s, meals_price = %s, meals_category = %s, meals_status = %s, meals_description = %s, meals_creattime = %s , meals_discount = %s , meals_discount_values = %s WHERE meals_owner = %s AND meals_number = %s", (
                    file_name, menu_name, menu_price, menu_category, menu_type, menu_description, updatetime, menu_discount, menu_discount_values, user, menu_number))
                succmesg = f"{menu_name}已更新"
                request.session['succmesg'] = succmesg
                return redirect('/clt/menu/')
            except Exception as err:
                errmesg = err
                request.session['errmesg'] = errmesg
                return redirect('/clt/menu/')

    def menu_delete(request: HttpRequest):
        if request.method == "POST":
            user = request.session.get('uniform_numbers')
            menu_number = request.POST.get('meals_number')
            menu_name = request.POST.get('meals_name')
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "DELETE FROM client_menu WHERE meals_owner = %s AND meals_number = %s AND meals_name = %s",
                    (user, menu_number, menu_name,))
                succmesg = f"{menu_name}已被刪除"
                request.session['succmesg'] = succmesg
                return redirect('/clt/menu/')
            except Exception as err:
                errmesg = err
                request.session['errmesg'] = errmesg
                return redirect('/clt/menu/')

    def category_add(request: HttpRequest):
        if request.method == "POST":
            user = request.session.get('uniform_numbers')
            category_name = request.POST.get('category_name')

            cursor = connection.cursor()
            cursor.execute("SELECT MAX(category_number) FROM meals_category")
            max_number = cursor.fetchone()[0]
            if max_number is None:
                category_number = 0
            else:
                category_number = int(max_number)
            cursor.execute("INSERT INTO meals_category (category_number, category_name, category_creator) VALUES (%s, %s, %s)",
            (category_number + 1, category_name, user))
            succmesg = "類別新增成功"
            request.session['succmesg'] = succmesg
            return redirect('/clt/menu/')


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

            validator = DataSet(
                uniform_numbers, client_password, password_confirm)
            errmesg = validator.check_signup()
            if errmesg is not None:
                return render(request, "client_base.html", {'errmesg': errmesg})
            else:
                try:
                    cursor = connection.cursor()
                    cursor.execute("INSERT INTO client (uniform_numbers , client_password , creattime) VALUES (%s , %s , %s)", (
                        uniform_numbers, client_password, creattime))
                    creatfolder = DataSet.create_user_folder(uniform_numbers)
                    if creatfolder:
                        succmesg = '註冊成功，請重新登入'
                        return render(request, 'client_base.html', {'succmesg': succmesg})
                    else:
                        errmesg = '註冊失敗，請重新註冊'
                        return render(request, 'client_base.html', {'errmesg': errmesg})
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
        # request.session.clear()  # 清出所有session資料
        del request.session['uniform_numbers']  # 清除session特定指定資料
        return redirect("/clt/")


class Customer():
    def index(request: HttpRequest):

        # 左側統計餐點總類參數
        categroys = "SELECT meals_category.category_name, client_menu.meals_category, COUNT(client_menu.meals_number) AS total FROM client_menu JOIN meals_category ON client_menu.meals_category = meals_category.category_number GROUP BY meals_category,category_name, client_menu.meals_category ORDER BY client_menu.meals_category ;"

        # 所有餐點參數
        Total_meals = "SELECT * FROM client_menu WHERE meals_status = %s ORDER BY meals_category;"

        cursor = connection.cursor()
        cursor.execute(categroys)
        count_names = [desc[0] for desc in cursor.description]
        count_list = [dict(zip(count_names, row)) for row in cursor.fetchall()]
        print(count_list)

        cursor.execute(Total_meals , ("1",))
        dict_name = [desc[0] for desc in cursor.description]
        total_meals = [dict(zip(dict_name, row)) for row in cursor.fetchall()]
        print(total_meals)

        return render(request, "customer_meal.html" , {"count_list" : count_list , "total_meals" : total_meals})

    def map(request:HttpRequest):
        return render(request , "customer_map.html")

    def login(request: HttpRequest):
        return render(request, "customer_login.html")
