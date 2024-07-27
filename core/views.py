from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import login,get_user_model,authenticate
from .models import CustomUser, ChatTable, ChatLink
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse as JR
from django.db.models.signals import post_save
from django.db.models import Q
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password, check_password
from hashlib import sha256
import time


@receiver(post_save, sender=ChatTable)
def trg(sender, instance, created, **kwargs):
    print("New Data")

def index(req):
    if req.user.id is not None:
        return redirect(dashboard)
    return render(req,"index.html")

def logout(req):
    req.session.flush()
    return redirect(index)

@login_required(login_url='signin')
def gchat(req,target=""):
    oldData = req.session.get("oldData")
    res = {}
    res["user"] = []
    res["mesg"] = []
    res["root"] = req.user.username
    viewer = req.path.split("/")[1:]
    if not CustomUser.objects.filter(username=target).exists() and target != "":
        return redirect(dashboard)
    while True:
        if target != "":
            targetUser = CustomUser.objects.get(username=target)
            if ChatLink.objects.filter(user1=req.user,user2=targetUser).exists():
                link = ChatLink.objects.get(user1=req.user,user2=targetUser)
            elif ChatLink.objects.filter(user2=req.user,user1=targetUser).exists():
                link = ChatLink.objects.get(user2=req.user,user1=targetUser)
            else:
                nlink = ChatLink.objects.create(user2=req.user,user1=targetUser)
                nlink.save()
                link = ChatLink.objects.get(user2=req.user,user1=targetUser)
            ctable = ChatTable.objects.filter(link=link)
        else:
            ctable = ChatTable.objects.filter(link__isnull=True)
        ltable = str([elem.id for elem in ctable])
        if ltable != oldData or (viewer[-2] != "pchat" and target == "") or (viewer[-3] != "pchat" and target != ""):
            break
        time.sleep(0.5)
    req.session["oldData"] = ltable
    for elem in ctable:
        res["user"].append(elem.user.username)
        res["mesg"].append(elem.msg)
    res["user"].reverse()
    res["mesg"].reverse()
    return JR(res)


@login_required(login_url='signin')
def chat(req,target=""):
    if req.method == "POST":
        msg = req.POST.get("msgtxt")
        print(msg)
        target = req.POST.get("target")
        if msg == None or target == None:
            return HttpResponse(status=204)
        if target != "":
            targetUser = CustomUser.objects.get(username=target)
            if ChatLink.objects.filter(user1=req.user,user2=targetUser).exists():
                link = ChatLink.objects.get(user1=req.user,user2=targetUser)
            elif ChatLink.objects.filter(user2=req.user,user1=targetUser).exists():
                link = ChatLink.objects.get(user2=req.user,user1=targetUser)
            else:
                nlink = ChatLink.objects.create(user2=req.user,user1=targetUser)
                nlink.save()
                link = ChatLink.objects.get(user2=req.user,user1=targetUser)

            utxt = msg
            ntext = ChatTable.objects.create(user=req.user,msg=utxt,link=link)
            ntext.save()
        else:
            utxt = msg
            ntext = ChatTable.objects.create(user=req.user,msg=utxt)
            ntext.save()
        return HttpResponse(status=204)
    return render(req,"chat.html",{"user":req.user,"target":target})

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
def target(req):
    if req.method == "POST":
        pdata = req.POST
        uname = pdata["username"]
        upass = pdata["password"]
        redata = {"username": uname}
        if CustomUser.objects.filter(username=uname).exists():
            target =  CustomUser.objects.get(username=uname)
            query = Q(user1=req.user,user2=target) | Q(user2=req.user,user1=target)
            if not ChatLink.objects.filter(query).exists():
                nlink = ChatLink.objects.create(user2=req.user,user1=targetUser)
                nlink.save()
            link = ChatLink.objects.get(query)
            if link.password is None:
                link.password = make_password(upass)
                link.save()
            else:
                if not check_password(upass,link.password):
                    redata['msgf'] = "Invalid credintials"
                    return render(req,"target.html",redata)
            req.session["ekey"] = sha256(upass.encode()).hexdigest()
            return redirect(chat,uname)
        redata['msgf'] = "User not found"
        return render(req,"target.html",redata)
    return render(req,"target.html")

@login_required(login_url='signin')
def dashboard(req):
    print(req.path)
    return render(req,"dashboard.html",{"userid":req.user})
