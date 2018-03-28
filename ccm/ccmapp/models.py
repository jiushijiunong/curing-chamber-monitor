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
    building_report_num = models.CharField(max_length=100)
    status = models.IntegerField()
    create_time = models.DateTimeField()
    last_edit_time = models.DateTimeField()
    supervise_unit_id = models.CharField(max_length=100)
    user_instance_id = models.CharField(max_length=100)
    build_unit_id = models.CharField(max_length=100)
    log_created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-last_edit_time', '-log_created_time')


class Contract(models.Model):
    sign_number = models.CharField(max_length=100, unique=True)
    serial_num = models.CharField(max_length=100)
    project = models.ForeignKey(Project, related_name='contracts', db_column='project_id')
    build_unit_id = models.CharField(max_length=100)
    build_unit_name = models.CharField(max_length=100)
    building_report_num = models.CharField(max_length=100)
    manage_unit_id = models.CharField(max_length=100)
    manage_unit_name = models.CharField(max_length=100)
    supervise_unit_id = models.CharField(max_length=100)
    supervise_unit_name = models.CharField(max_length=100)
    construct_unit_name = models.CharField(max_length=100)
    entrust_unit_name = models.CharField(max_length=100)
    checked_date_time = models.DateTimeField()
    checked = models.BooleanField()
    detection_unit_member_code = models.CharField(max_length=20)
    detection_unit_member_name = models.CharField(max_length=100)
    log_created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-checked_date_time', '-log_created_time')


class Sample(models.Model):
    instance_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    num = models.CharField(max_length=100)
    item_id = models.CharField(max_length=100)
    item_name = models.CharField(max_length=100)
    # project = models.ForeignKey(Project, related_name='project_id')
    contract = models.ForeignKey(Contract, related_name='+')
    count = models.IntegerField()
    status = models.IntegerField()
    status_str = models.CharField(max_length=20)
    regular = models.BooleanField()
    kind_id = models.CharField(max_length=100)
    kind_name = models.CharField(max_length=100)
    detection_unit_member_name = models.CharField(max_length=100)
    report_num = models.CharField(max_length=100)
    core_code_id = models.CharField(max_length=100)
    core_code_id_end = models.CharField(max_length=100)
    project_part = models.CharField(max_length=100)
    spec = models.CharField(max_length=100)
    grade = models.CharField(max_length=20)
    exam_result = models.CharField(max_length=100)
    hnt_yhtj = models.CharField(max_length=100)
    age_time_str = models.CharField(max_length=20)
    # report_date = models.DateTimeField(blank=True)
    # detection_date = models.DateTimeField(blank=True)
    # molding_date = models.DateTimeField(blank=True)
    report_date_str = models.CharField(max_length=100)
    detection_date_str = models.CharField(max_length=100)
    molding_date_str = models.CharField(max_length=100)
    log_created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-log_created_time',)
