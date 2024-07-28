from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import login,get_user_model,authenticate
from .models import CustomUser, ChatTable, ChatLink, UpManager
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse as JR
from django.db.models import Q
from django.contrib.auth.hashers import make_password, check_password
from hashlib import sha256
import time

@login_required(login_url='signin')
def msg(req):
    if req.method == "POST":
        if req.POST.get("method") == "get":
            rtype = req.POST.get("type")
            if rtype == "chat":
                rtar = req.POST.get("target")
                if rtar != "":
                    rsrc = req.user
                    tars = CustomUser.objects.filter(username=rtar)
                    if tars.exists():
                        tar = tars[0]
                        query = Q(user1=rsrc,user2=tar)|Q(user1=tar,user2=rsrc)
                        links = ChatLink.objects.filter(query)
                        if links.exists():
                            res = {}
                            res["root"] = rsrc.username
                            res["user"] = []
                            res["mesg"] = []
                            link = links[0]
                            if req.resolver_match.view_name == "pmsg" and not ChatTable.objects.updated(rsrc.username,link):
                                return HttpResponse(status=204)
                            for msg in ChatTable.objects.filter(link=link):
                                res["user"].append(msg.user.username)
                                res["mesg"].append(msg.msg)
                            ChatTable.objects.setChecked(rsrc.username,link)
                            res["user"].reverse()
                            res["mesg"].reverse()
                            return JR(res)
                else:
                    rsrc = req.user
                    res = {}
                    res["root"] = rsrc.username
                    res["user"] = []
                    res["mesg"] = []
                    for msg in ChatTable.objects.filter(link__isnull=True):
                        res["user"].append(msg.user.username)
                        res["mesg"].append(msg.msg)
                    ChatTable.objects.setChecked(rsrc.username)
                    res["user"].reverse()
                    res["mesg"].reverse()
                    return JR(res)
        if req.POST.get("method") == "post":
            rtype = req.POST.get("type")
            rmsg = req.POST.get("msg")
            if rtype == "chat":
                rtar = req.POST.get("target")
                rsrc = req.user
                if rtar != "":
                    tars = CustomUser.objects.filter(username=rtar)
                    if tars.exists():
                        tar = tars[0]
                        query = Q(user1=rsrc,user2=tar)|Q(user1=tar,user2=rsrc)
                        links = ChatLink.objects.filter(query)
                        if links.exists():
                            nmsg = ChatTable.objects.create(user=rsrc,msg=rmsg,link=links[0])
                else:
                    nmsg = ChatTable.objects.create(user=rsrc,msg=rmsg)
    return HttpResponse(status=204)
    

def index(req):
    if req.user.id is not None:
        return redirect(dashboard)
    return render(req,"index.html")

def logout(req):
    req.session.flush()
    return redirect(index)

@login_required(login_url='signin')
def chat(req,target=""):
    if target != "":
        rsrc = req.user
        tars = CustomUser.objects.filter(username=target)
        if not tars.exists():
            return redirect('target')
        tar = tars[0]
        query = Q(user1=rsrc,user2=tar)|Q(user1=tar,user2=rsrc)
        if not ChatLink.objects.filter(query).exists():
            return redirect('target')
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
