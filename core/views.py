from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import login,get_user_model,authenticate
from .models import CustomUser, ChatTable, ChatLink
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse as JR

def index(req):
    req.session['nav'] = {
                "Home": "/dashboard/",
                "Global Chat": "/chat/",
                "Local Chat": "/target/",
            }
    if req.user.id is not None:
        return redirect(dashboard)
    return render(req,"index.html")

def logout(req):
    req.session.flush()
    return redirect(index)

@login_required(login_url='signin')
def gchatTarget(req,target):
    if not CustomUser.objects.filter(username=target).exists():
        return redirect(dashboard)
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
    if not ctable.exists():
        return JR({})
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
def gchat(req):
    ctable = ChatTable.objects.filter(link__isnull=True)
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
def chatTarget(req,target):
    if not CustomUser.objects.filter(username=target).exists():
        return redirect(dashboard)
    targetUser = CustomUser.objects.get(username=target)
    if ChatLink.objects.filter(user1=req.user,user2=targetUser).exists():
        link = ChatLink.objects.get(user1=req.user,user2=targetUser)
    elif ChatLink.objects.filter(user2=req.user,user1=targetUser).exists():
        link = ChatLink.objects.get(user2=req.user,user1=targetUser)
    else:
        nlink = ChatLink.objects.create(user2=req.user,user1=targetUser)
        nlink.save()
        link = ChatLink.objects.get(user2=req.user,user1=targetUser)

    print(link)
    if req.method == "POST":
        pdata = req.POST
        utxt = pdata["msgtxt"]
        ntext = ChatTable.objects.create(user=req.user,msg=utxt,link=link)
        ntext.save()
        
    return render(req,"chat.html",{"user":req.user,"target":target})

@login_required(login_url='signin')
def chat(req):
    if req.method == "POST":
        pdata = req.POST
        utxt = pdata["msgtxt"]
        ntext = ChatTable.objects.create(user=req.user,msg=utxt)
        ntext.save()
        
    return render(req,"chat.html",{"user":req.user})

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
            return redirect(chatTarget,uname)
        redata['msgf'] = "User not found"
        return render(req,"target.html",redata)
    return render(req,"target.html")

@login_required(login_url='signin')
def dashboard(req):
    print(req.path)
    return render(req,"dashboard.html",{"userid":req.user})
