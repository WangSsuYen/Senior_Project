from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


class Client():
    def index(request: HttpRequest):
        return render(request, 'client_base.html')


class Customer():
    def index(request: HttpRequest):
        return render(request, "customer_index.html")

    def login(request: HttpRequest):
        return render(request, "customer_login.html")
