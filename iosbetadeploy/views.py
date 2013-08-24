# -*- coding: utf-8 -*-
# Create your views here.
from django.views.generic import View
from django.http import Http404
from django.db import transaction
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate
from django.core.files import temp

import plistlib
import base64
import biplist
import time

from zipfile import ZipFile

from .models import Device, Project, Instance, InstanceAllowedDevice
from .decorators import error_handling
from .utils import generate_random_from_vschar_set, HttpResponseJson, encrypt, decrypt

def error_handler(e):
    raise Http404

class HttpBasicAuthenticationView(View):
    """
    class-based view with http basic authentication.
    usage:

    class SomeView(HttpBasicAuthenticationView):
        http_method_authentication_needed = ['post']

        def check_permission(self, request):
            if not request.user.is_staff:
                raise Http404
    """

    http_method_authentication_needed = []

    def check_permission(self, request):
        pass

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        """
        override dispatch for handling http basic authorization
        """
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2:
                if auth[0].lower() == "basic":
                    username, password = base64.b64decode(auth[1]).split(':')
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        if user.is_active:
                            #login(request, user)
                            request.user = user
                            self.check_permission(request)
                            return super(HttpBasicAuthenticationView, self).dispatch(request, *args, **kwargs)
        if request.method.lower() in self.http_method_authentication_needed:
            raise Http404
        return super(HttpBasicAuthenticationView, self).dispatch(request, *args, **kwargs)


class ProjectInstanceView(HttpBasicAuthenticationView):
    """
    get:
        if token is for project, return project's instances view.
        elif token is for instance return manifest for instance with file access key.
        else raise http404
    post:
        need http basic authentication.
        param:
            instance, iOS application package, normally *.ipa
        register application.
    """
    http_method_authentication_needed = ['post']

    def check_permission(self, request):
        if not request.user.is_staff:
            raise Http404

    @error_handling(error_handler)
    def get(self, request, token):
        postfix = token[-4:]
        if postfix == "proj":
            project = Project.objects.get(token=token)
            instances = Instance.objects.filter(project=project).filter(is_showing=True).order_by('-create_date')
            return render_to_response('Project.html', {"project": project,'instances':instances})

        elif postfix == 'inst':
            instance = Instance.objects.select_related('project__bundle_identifier','project__name').get(token=token)
            file_key = encrypt(str(int(time.time()))+':'+generate_random_from_vschar_set(3), token.encode('utf8'))
            #TODO: find clear way to get domain
            return render_to_response('manifest.xml', {"instance": instance, 'file_key':file_key,
                                                       'domain': request.META['HTTP_HOST']})



        raise Http404

    @error_handling(error_handler)
    def post(self, request, token):
        uploaded_file = request.FILES['instance']
        appname = uploaded_file._name[:-4]
        zipped_file = ZipFile(uploaded_file)
        tempdir = temp.gettempdir()

        infoPlist_path = zipped_file.extract('Payload/'+appname+'.app/Info.plist',tempdir)
        provision_path = zipped_file.extract('Payload/'+appname+'.app/embedded.mobileprovision',tempdir)
        info = biplist.readPlist(infoPlist_path)
        bundle_name =  info['CFBundleName']
        bundle_version = info['CFBundleVersion']
        version_string = info['CFBundleShortVersionString']

        if token != info['CFBundleIdentifier']:
            raise Http404
        bundle_identifier = info['CFBundleIdentifier']
        provision_file = file(provision_path,'r')
        provision_content = provision_file.read()
        provision_file.close()
        start_index = provision_content.find('<?xml version="1.0" encoding="UTF-8"?>')
        end_index = provision_content.find('</plist>')
        provision_info = plistlib.readPlistFromString(provision_content[start_index:end_index+8])
        allowed_devices = provision_info['ProvisionedDevices']
        try:
            project = Project.objects.get(bundle_identifier=bundle_identifier)
        except ObjectDoesNotExist:
            project = Project(name=bundle_name, desc=bundle_name,
                              bundle_identifier=bundle_identifier,
                              token=generate_random_from_vschar_set(20)+".proj")
            project.save()

        with transaction.commit_on_success():
            try:
                instance = Instance(project=project, version=version_string, build_version=bundle_version,
                                    description="", token=generate_random_from_vschar_set(20)+".inst")
                instance.save()
                for udid in allowed_devices:
                    device, dummy_unused = Device.objects.get_or_create(udid=udid)
                    InstanceAllowedDevice.objects.create(instance=instance, device=device)

                transaction.commit()
            except Exception:
                transaction.rollback()
                raise
        try:
            instance.ipa_path.save(generate_random_from_vschar_set(20), request.FILES['instance'], True)
        except Exception:
            InstanceAllowedDevice.objects.filter(instance=instance).delete()
            instance.delete()
            raise
        return HttpResponseJson({'project_token:': project.token, 'instance_token': instance.token})


class FileRedirectView(View):
    """
    get:
        param:
            token: instance token
            file_access_key: file_access_key
        if file_access_key is vaild, return file real url.
        else raise Http404
    """
    @error_handling(error_handler)
    def get(self, request, token, key):
        reversed_key = decrypt(key.encode('utf-8'), token.encode('utf-8'))
        if abs(time.time() - int(reversed_key.split(':')[0])) > 60:
            raise Http404
        return HttpResponseRedirect(Instance.objects.get(token=token).ipa_path.url)


class IndexView(View):

    def get(self, request):
        projects = Project.objects.all()
        return render_to_response('Index.html', {"projects": projects})