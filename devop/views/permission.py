#!/usr/bin/env python
# coding = uft-8

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from django.contrib.auth.decorators import login_required

from opman.forms import PermissionListForm
from opman.models import RoleList, PermissonList
from django.contrib.auth.models import User, Group
from opman.views import SelfPaginator

def PermissionVerify():
    '''
    权限认证模块;
     此模块先判断用户是不是管理员（is_superuser为True）,如果是管理，则有全部权限，如果不是则获取request.user和request.path,
     判断2个参数是不是匹配，匹配则有权限，反之则无
    '''

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            iUser = User.objects.get(username=request.user)

            uid = iUser.id
            print(uid)
            if not iUser.is_superuser:
                if not PermissonList.objects.get(username=request.user):
                    return HttpResponseRedirect(reverse('permissiondenyurl'))
                role_permisson = PermissonList.objects.get(username=iUser.username)
                role_permisson_list = role_permisson.permission.all()
                matchurl = []
                for x in role_permisson_list:
                    if request.path == x.url or request.path.rstrip('/') == x.url:
                        matchurl.append(x.url)
                    elif request.path.startswith(x.url):
                        matchurl.append(x.url)
                    else:
                        pass
                print('%s---->matchUrl:%s' %(request.user, str(matchurl)))
                if len(matchurl) == 0:
                    return HttpResponseRedirect(reverse('permissiondenyurl'))
            else:
                pass
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

@login_required
def Nopermisson(request):

    kwvars = {
        'request':request,
    }

    return render_to_response('UserManage/permission.no.html', kwvars, RequestContext(request))

@login_required
@PermissionVerify()
def AddPermission(request):
    form = PermissionListForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('listpermissonurl'))
    else:
        form = PermissionListForm()

    kwvars = {
        'form':form,
        'request':request,
    }

    return render_to_response('UserManage/permission.add.html',kwvars, RequestContext(request))

@login_required
@PermissionVerify()
def ListPermission(request):
    mList = PermissonList.objects.all()

    #分页展示
    lst = SelfPaginator(request, mList, 20)

    kwvars = {
        '1Page':lst,
        'request':request,
    }

    return render_to_response('UserManage/permission.list.html', kwvars, RequestContext(request))

@login_required
@PermissionVerify()
def EditPermission(request, ID):
    iPermission = PermissonList.objects.get(id=ID)

    if request.method == "POST":
        form = PermissionListForm(request.POST, instance=iPermission)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("listpermissononurl"))
    else:
        form = PermissionListForm(instance=iPermission)

    kwvars = {
        'ID':ID,
        'form':form,
        'request':request,
    }
    return render_to_response('UserManage/permission.edit.html',kwvars, RequestContext(request))

@login_required
@PermissionVerify()
def DelePermission(request, ID):
    PermissonList.objects.filter(id= ID).delete()

    return HttpResponseRedirect(reverse('listpermissionurl'))