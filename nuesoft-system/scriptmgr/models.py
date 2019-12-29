# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models

class TestFileParam(models.Model):
    file_name = models.CharField(max_length=64, blank=True, null=True)
    type = models.CharField(max_length=10, blank=True, null=True)
    ip_addr = models.CharField(max_length=1024, blank=True, null=True)
    param = models.CharField(max_length=1024, blank=True, null=True)
    ways_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'test_file_param'

