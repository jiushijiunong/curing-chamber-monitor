# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from pocket_monitor.mo import samples


class Command(BaseCommand):
    help = 'Check if is the samples count correct in DB'

    def __init__(self):
        self.samples_sync = samples.Sync()

    def add_arguments(self, parser):
        parser.add_argument('user_instance_id', type=str)
        parser.add_argument('build_unit_id', type=str)

    def handle(self, *args, **options):
        self.samples_sync.samples_count(options['user_instance_id'], options['build_unit_id'])
