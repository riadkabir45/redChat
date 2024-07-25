# chat/consumers.py
import json

from channels.generic.websocket import WebsocketConsumer
from .models import CustomUser, ChatTable, ChatLink
from django.db.models.signals import post_save
from django.dispatch import receiver


class ChatConsumer(WebsocketConsumer):
    ins = []
    def connect(self):
        ChatConsumer.ins.append(self)
        self.accept()

    def disconnect(self, close_code):
        ChatConsumer.ins.remove(self)
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        userid = text_data_json["user"]
        tarid = text_data_json["target"]
        if text_data_json["type"] == "msg" and text_data_json["message"] != "":
            message = text_data_json["message"]
            user = CustomUser.objects.get(username=userid)
            if tarid == "":
                ntext = ChatTable.objects.create(user=user,msg=message)
                ntext.save()
            else:
                targ = CustomUser.objects.get(username=tarid)
                srcUser,tarUser = user,targ
                if ChatLink.objects.filter(user1=srcUser,user2=tarUser).exists():
                    link = ChatLink.objects.get(user1=srcUser,user2=tarUser)
                elif ChatLink.objects.filter(user2=srcUser,user1=tarUser).exists():
                    link = ChatLink.objects.get(user2=srcUser,user1=tarUser)
                else:
                    nlink = ChatLink.objects.create(user2=srcUser,user1=tarUser)
                    nlink.save()
                    link = ChatLink.objects.get(user2=srcUser,user1=tarUser)
                ntext = ChatTable.objects.create(user=user,msg=message,link=link)
                ntext.save()
        self.userid = userid
        self.tarid = tarid
        if text_data_json["type"] == "refresh":
            self.refresh()

    @receiver(post_save, sender=ChatTable)
    def trg(sender, instance, created, **kwargs):
        for ins in ChatConsumer.ins:
            ins.refresh()

    def refresh(self):
        src = self.userid
        tar = self.tarid
        srcUser = CustomUser.objects.get(username=src)
        if tar != "":
            tarUser = CustomUser.objects.get(username=tar)
            if ChatLink.objects.filter(user1=srcUser,user2=tarUser).exists():
                link = ChatLink.objects.get(user1=srcUser,user2=tarUser)
            elif ChatLink.objects.filter(user2=srcUser,user1=tarUser).exists():
                link = ChatLink.objects.get(user2=srcUser,user1=tarUser)
            else:
                nlink = ChatLink.objects.create(user2=srcUser,user1=tarUser)
                nlink.save()
                link = ChatLink.objects.get(user2=srcUser,user1=tarUser)
            ctable = ChatTable.objects.filter(link=link)
        else:
            ctable = ChatTable.objects.filter(link__isnull=True)
        res = {}
        res["user"] = []
        res["mesg"] = []
        res["root"] = srcUser.username
        if not ctable.exists():
            res["size"] = len(res["user"])
            self.send(text_data=json.dumps(res))
            return
        for elem in ctable:
            res["user"].append(elem.user.username)
            res["mesg"].append(elem.msg)
        res["user"].reverse()
        res["mesg"].reverse()
        res["size"] = len(res["user"])
        self.send(text_data=json.dumps(res))
