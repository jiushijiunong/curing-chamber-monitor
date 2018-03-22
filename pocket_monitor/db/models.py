# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Project(models.Model):
    instance_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    nature = models.CharField(max_length=20)
    num = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    address = models.CharField(max_length=256)
    build_report_num = models.CharField(max_length=100)
    status = models.IntegerField()
    create_time = models.DateTimeField()
    last_edit_time = models.DateTimeField()
    log_created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-last_edit_time', 'create_time')
