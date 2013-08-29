# -*- coding: utf-8 -*-
from iosbetadeploy.views import HttpBasicAuthenticationView, error_handler
from iosbetadeploy.decorators import error_handling
from localizable.models import LocalizableString, Project
from django.http import HttpResponse, Http404
import urllib2

class LocalizableStringView(HttpBasicAuthenticationView):
    http_method_authentication_needed = ['post']

    def check_permission(self, request):
        if not request.user or not request.user.is_staff:
            raise Http404

    @error_handling(error_handler)
    def get(self, request, token, locale):
        project = Project.objects.get(token=token)
        return HttpResponse(LocalizableString.objects.get(project=project, locale=locale).text)


    @error_handling(error_handler)
    def post(self, request, token, locale):
        project = Project.objects.get(token=token)
        localizableString, created_unused = LocalizableString.objects.get_or_create(project=project, locale=locale)
        localizableString.text = request.POST['text']
        localizableString.save()
        return HttpResponse("success")
