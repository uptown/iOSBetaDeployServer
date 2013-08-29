from django.db import models
from django.contrib import admin
from iosbetadeploy.models import Project



class LocalizableString(models.Model):
    project = models.ForeignKey(Project)
    locale = models.CharField(max_length=2, unique=True)
    text = models.TextField(default="")

    class Meta:
        unique_together = ("project", "locale")

    def __unicode__(self):
        return self.project.name + '(' + self.locale + ')'

admin.site.register(LocalizableString)
