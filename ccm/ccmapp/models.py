# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Project(models.Model):
    name = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()

    class Meta:
        ordering = ('-created', 'code')
