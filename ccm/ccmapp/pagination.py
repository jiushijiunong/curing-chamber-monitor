# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from django.utils.functional import cached_property


class FasterDjangoPaginator(Paginator):
    @cached_property
    def count(self):
        return self.object_list.values('id').count()


class CustomizedPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    django_paginator_class = FasterDjangoPaginator
