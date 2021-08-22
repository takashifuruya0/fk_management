"""fk_management URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.views.generic import TemplateView


class TopView(TemplateView):
    template_name="top.html"

    def get(self, request):
        if not request.user.is_authenticated:
            # return super().get(request)
            return redirect("/auth/login")
        elif request.user.is_superuser:
            return redirect("kakeibo:kakeibo_top")
        else:
            return redirect("kakeibo:shared_top")


urlpatterns = [
    path('admin/', admin.site.urls, name="admin"),
    path('auth/', include('allauth.urls')),
    path("kakeibo/", include("kakeibo.urls")),
    path("", TopView.as_view(), name="top"),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += staticfiles_urlpatterns()

