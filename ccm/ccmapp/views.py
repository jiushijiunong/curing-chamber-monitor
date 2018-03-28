# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django_filters.rest_framework
from rest_framework import viewsets,filters
from ccm.ccmapp import models, serializers

# Create your views here.


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    filter_fields = ('name', 'code')
    search_fields = ('name', )
    ordering_fields = ('code',)
