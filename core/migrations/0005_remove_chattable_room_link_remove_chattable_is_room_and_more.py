# Generated by Django 5.0.6 on 2024-07-28 06:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_chatroom_chattable_is_room_chattable_room_link"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="chattable",
            name="room_link",
        ),
        migrations.RemoveField(
            model_name="chattable",
            name="is_room",
        ),
        migrations.DeleteModel(
            name="ChatRoom",
        ),
    ]