# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from ccm.ccmapp import models


class ProjectSerializer(serializers.ModelSerializer):
    contracts = serializers.PrimaryKeyRelatedField(many=True, queryset=models.Contract.objects.all())

    class Meta:
        model = models.Project
        fields = '__all__'
        depth = 1


class ContractSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(many=False, queryset=models.Project.objects.all())

    class Meta:
        model = models.Contract
        fields = '__all__'
        depth = 1


class SampleSerializer(serializers.ModelSerializer):
    contract = serializers.PrimaryKeyRelatedField(many=False, queryset=models.Contract.objects.all())

    class Meta:
        model = models.Sample
        fields = '__all__'
        depth = 1
