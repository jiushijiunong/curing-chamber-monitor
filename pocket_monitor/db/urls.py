# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import routers
from pocket_monitor.db import views

# router = routers.DefaultRouter(trailing_slash=False)
router = routers.SimpleRouter(trailing_slash=False)
router.register(r'api/projects', views.ProjectViewSet, base_name='project')
router.register(r'api/contracts', views.ContractViewSet, base_name='contract')
router.register(r'api/samples', views.SampleViewSet, base_name='sample')

urlpatterns = router.urls
