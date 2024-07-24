from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import login,get_user_model,authenticate
from .models import CustomUser, ChatTable
from django.contrib.auth.decorators import login_required
import django.contrib.auth.decorators as decor
from django.http import JsonResponse as JR

def index(req):
    return render(req,"index.html")

def gchat(req):
    ctable = ChatTable.objects.all()
    res = {}
    res["user"] = []
    res["mesg"] = []
    res["root"] = req.user.username
    for elem in ctable:
        res["user"].append(elem.user.username)
        res["mesg"].append(elem.msg)
    return JR(res)

@login_required(login_url='signin')
def chat(req):
    if req.method == "POST":
        pdata = req.POST
        utxt = pdata["msgtxt"]
        ntext = ChatTable.objects.create(user=req.user,msg=utxt)
        ntext.save()

    ctable = ChatTable.objects.all()
        
    return render(req,"chat.html",{"ctable":ctable,"user":req.user})

def signup(req):
    if req.user.id is not None:
        return redirect(dashboard)
    if req.method == "POST":
        pdata = req.POST
        uname = pdata["username"]
        upass = pdata["password"]
        ucpass = pdata["cpassword"]
        redata = {"username": uname}
        if upass != ucpass:
            redata["msgf"] = "Both password mismatch!!!"
        if CustomUser.objects.filter(username="riada").exists():
            redata["msgf"] = "Username taken!!!"
        else:
            nuser = CustomUser.objects.create_user(username=uname,password=upass)
            nuser.save()
            redata["msgs"] = "Account created successfully!"
            return render(req,"signup.html",redata)
        return render(req,"signup.html",redata)
    return render(req,"signup.html")

def signin(req):
    if req.user.id is not None:
        return redirect(dashboard)
    if req.method == "POST":
        pdata = req.POST
        uname = pdata["username"]
        upass = pdata["password"]
        redata = {"username": uname}
        user = authenticate(username=uname,password=upass)
        if user is not None:
            login(req,user)
            return redirect(dashboard)
        else:
            redata['msgf'] = "Invalid credintials"
        return render(req,"signin.html",redata)
    return render(req,"signin.html")

@login_required(login_url='signin')
def dashboard(req):
    return render(req,"dashboard.html",{"userid":req.user})
