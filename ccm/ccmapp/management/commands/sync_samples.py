# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from ccm.mo import sample


class Command(BaseCommand):
    help = 'Sync samples into DB'

    def __init__(self):
        self.sample_sync = sample.Sync()

    def handle(self, *args, **options):
        self.sample_sync.sync()
