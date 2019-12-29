from __future__ import unicode_literals

from django.db import models

# Create your models here.

class DialingIp(models.Model):
    ip = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'dialingip'
