# Generated by Django 5.0.6 on 2024-07-27 16:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_chatlink_password"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChatRoom",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("room_id", models.IntegerField()),
                ("password", models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.AddField(
            model_name="chattable",
            name="is_room",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="chattable",
            name="room_link",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="core.chatroom",
            ),
        ),
    ]
