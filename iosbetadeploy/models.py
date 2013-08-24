from django.db import models
from django.contrib import admin
# Create your models here.



class Project(models.Model):
    token = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=20)
    desc = models.TextField(default="")
    bundle_identifier = models.CharField(max_length=100, unique=True)
    pem = models.FileField(default=None, blank=True, null=True, upload_to="pem")

    def __unicode__(self):
        return self.name

class Instance(models.Model):
    token = models.CharField(max_length=30, unique=True)
    project = models.ForeignKey(Project)
    version = models.CharField(max_length=30)
    build_version = models.CharField(max_length=30)
    description = models.TextField()
    create_date = models.DateTimeField(auto_now=True)
    is_showing = models.BooleanField(default=True, db_index=True)
    ipa_path = models.FileField(default=None, blank=True, null=True, upload_to="instances")

    class Meta:
        unique_together = ("project", "build_version")

    def __unicode__(self):
        return self.project.name + " " + self.version + "(" + self.build_version + ")"

class Device(models.Model):
    udid = models.CharField(max_length=50)
    name = models.CharField(max_length=50,default="Unknown Device")
    email = models.EmailField(default=None, blank=True, null=True)
    push_token = models.CharField(max_length=255, default="", blank=True)

    def __unicode__(self):
        return self.name + " " + self.udid

class InstanceAllowedDevice(models.Model):
    device = models.ForeignKey(Device)
    instance = models.ForeignKey(Instance)

    class Meta:
        unique_together = ("device", "instance")


admin.site.register(Project)
admin.site.register(Instance)
admin.site.register(Device)
admin.site.register(InstanceAllowedDevice)

