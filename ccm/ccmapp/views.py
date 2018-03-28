# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django_filters.rest_framework
from rest_framework import viewsets,filters
from ccm.ccmapp import models, serializers

# Create your views here.


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter,)
    filter_fields = ('instance_id', 'name', 'user_instance_id', 'build_unit_id', 'status', 'nature', 'create_time',
                     'region')
    search_fields = ('name', )
    ordering_fields = ('instance_id', 'name', 'user_instance_id', 'build_unit_id', 'status', 'nature', 'create_time',
                       'region')


class ContractViewSet(viewsets.ModelViewSet):
    queryset = models.Contract.objects.all()
    serializer_class = serializers.ContractSerializer
    filter_fields = ('sign_number', 'serial_num', 'project', 'checked_date_time')
    ordering_fields = ('sign_number', 'serial_num', 'project', 'checked_date_time')


class SampleViewSet(viewsets.ModelViewSet):
    queryset = models.Sample.objects.all()
    serializer_class = serializers.SampleSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    filter_fields = ('instance_id', 'name', 'contract', 'item_id', 'item_name', 'kind_id',
                     'kind_name', 'core_code_id', 'core_code_id_end', 'status')
    search_fields = ('name',)
    ordering_fields = ('instance_id', 'name', 'contract', 'item_id', 'item_name', 'kind_id',
                       'kind_name', 'core_code_id', 'core_code_id_end', 'status')