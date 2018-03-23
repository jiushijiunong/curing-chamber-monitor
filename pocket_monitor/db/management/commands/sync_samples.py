# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.core.management.base import BaseCommand, CommandError
from pocket_monitor.mo import samples

logger = logging.getLogger("mo.sync.samples")


class Command(BaseCommand):
    def __init__(self):
        self.samples_sync = samples.Sync()

    def handle(self, *args, **options):
        self.samples_sync.sync()
