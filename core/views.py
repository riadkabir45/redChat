from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import login,get_user_model,authenticate
from .models import CustomUser, ChatTable, ChatLink
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse as JR
from django.db.models.signals import post_save
from django.dispatch import receiver
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
    viewer = req.path.split("/")[-2]
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
        if not ctable.exists():
            return JR({})
        ltable = str([elem.id for elem in ctable])
        if ltable != oldData or viewer != "pchat":
            break
        time.sleep(0.5)
    req.session["oldData"] = ltable
    res = {}
    res["user"] = []
    res["mesg"] = []
    res["root"] = req.user.username
    for elem in ctable:
        res["user"].append(elem.user.username)
        res["mesg"].append(elem.msg)
    res["user"].reverse()
    res["mesg"].reverse()
    return JR(res)


@login_required(login_url='signin')
def chat(req,target=""):
    if req.method == "POST":
        print("new respone used")
        msg = req.POST.get("msgtxt")
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
        redata = {"username": uname}
        if CustomUser.objects.filter(username=uname).exists():
            return redirect(chat,uname)
        redata['msgf'] = "User not found"
        return render(req,"target.html",redata)
    return render(req,"target.html")

@login_required(login_url='signin')
def dashboard(req):
    print(req.path)
    return render(req,"dashboard.html",{"userid":req.user})
