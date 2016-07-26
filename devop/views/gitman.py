#!/usr/bin/python
# coding = utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, RequestContext
from django.contrib.auth.decorators import login_required
from devop.views.permission import PermissionVerify, SelfPaginator
from .gitlab import all_projects, user_all_projects, gitlab_log
from opman.forms import GitSettingForm, TokenForm, ProSettingForm, ApplyUploadForm
from opman.models import GitSetting, GitToken, ProjectSetting, ProjectApply
from git import Repo, cmd, Git
import os
from datetime import datetime


@login_required
def ProSetting(request, Url):
    try:
        cProSetting = ProjectSetting.objects.get(url=Url)
    except Exception as e:
        print(e)
        form = ProSettingForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('listallprojectsurl'))
        else:
            form = ProSettingForm()
        kwvars = {
            'url': Url,
            'form': form,
            'request': request,
        }
        return render_to_response('GitLab/project.setting.html', kwvars, RequestContext(request))
    else:
        iProSetting = ProjectSetting.objects.get(url=Url)
        form = ProSettingForm(request.POST, instance=iProSetting)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('listallprojectsurl'))
        else:
            form = ProSettingForm(instance=iProSetting)
        kwvars = {
            'url': Url,
            'form': form,
            'request': request,
        }
        return render_to_response('GitLab/project.setting.html', kwvars, RequestContext(request))


@login_required
@PermissionVerify()
def Setting(request):
    cSetting = GitSetting.objects.all()
    if len(cSetting) == 0:
        form = GitSettingForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('gitsettingurl'))
        else:
            form = GitSettingForm()
        kwvars = {
            'form': form,
            'request': request,
        }
        return render_to_response('GitLab/setting.add.html', kwvars, RequestContext(request))
    else:
        iGitSetting = GitSetting.objects.get(id=1)
        form = GitSettingForm(request.POST, instance=iGitSetting)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('gitsettingurl'))
        else:
            form = GitSettingForm(instance=iGitSetting)
        kwvars = {
            'form': form,
            'request': request,
        }
        return render_to_response('GitLab/setting.add.html', kwvars, RequestContext(request))


@login_required
@PermissionVerify()
def AddToken(request):
    form = TokenForm(request.POST)
    if form.is_valid():
        i = GitToken()
        form.save(commit=False)
        usertoken = form.cleaned_data['usertoken']
        i.usertoken = usertoken
        i.fullname = request.user
        i.save()
        return HttpResponseRedirect(reverse('listallprojectsurl'))
    else:
        form = TokenForm()
    kwvars = {
        'form': form,
        'request': request,
    }
    return render_to_response('GitLab/token.add.html', kwvars, RequestContext(request))


@login_required
@PermissionVerify()
def ListProjects(request):
    cUser = request.user
    cGitSetting = GitSetting.objects.get(id=1)
    host = cGitSetting.hostname
    rootoken = cGitSetting.rootoken
    path = '/api/v3/'
    if cUser.is_superuser:
        KList = all_projects(host, path, rootoken)
        lst = SelfPaginator(request, KList, 20)
    else:
        fullnameid = cUser.id
        try:
            usertoken = GitToken.objects.get(fullname_id=fullnameid)
        except Exception as e:
            print(e)
            return HttpResponseRedirect(reverse('tokenaddurl'))
        else:
            usertoken = GitToken.objects.get(fullname_id=fullnameid).usertoken
            KList = user_all_projects(host, path, usertoken)
            lst = SelfPaginator(request, KList, 20)

    kwvars = {
        'lpage': lst,
        'request': request,
    }
    return render_to_response('GitLab/projects.list.html', kwvars)


@login_required
def UploadProject(request, Url):
    codepath = Url.split('/')[-1].split('.')[0]
    sourcepath = GitSetting.objects.get(id=1).sourcepath
    sourcepath = sourcepath.rstrip('/')
    if not os.path.exists(sourcepath):
        os.mkdir(sourcepath)
    if not os.path.exists(sourcepath + '/' + codepath):
        Repo.clone_from(Url, sourcepath + '/' + codepath)
    else:
        os.chdir(sourcepath)
        g = cmd.Git(codepath)
        g.pull()
    return HttpResponseRedirect(reverse('listallprojectsurl'))


@login_required
def UploadApply(request, ID, Pname, Url):
    form = ApplyUploadForm(request.POST)
    if form.is_valid():
        i = ProjectApply()
        form.save(commit=False)
        title = form.cleaned_data['title']
        branch = form.cleaned_data['projectbranch']
        commitid = form.cleaned_data['commitid']
        i.title = title
        i.projectbranch = branch
        i.commitid = commitid
        i.projectname = Pname
        i.projectid = ID
        i.projecturl = Url
        i.save()
        return HttpResponseRedirect(reverse('listallprojectsurl'))
    else:
        form = ApplyUploadForm()
    kwvars = {
        'ID': ID,
        'Pname': Pname,
        'Url':Url,
        'form': form,
        'request': request,
    }
    return render_to_response('GitLab/project.apply.upload.html', kwvars, RequestContext(request))

@login_required
def Reset(request, Url):
    codepath = Url.split('/')[-1].split('.')[0]
    sourcepath = GitSetting.objects.get(id=1).sourcepath
    sourcepath = sourcepath.rstrip('/')
    os.chdir(sourcepath)
    repo = Repo(codepath)
    repo.head.reset('HEAD~1', working_tree=1)
    return HttpResponseRedirect(reverse('listallprojectsurl'))


@login_required
def GitLog(request, ID):
    cGitSetting = GitSetting.objects.get(id=1)
    host = cGitSetting.hostname
    rootoken = cGitSetting.rootoken
    pro_Log = gitlab_log(host, rootoken, ID, '30')
    kwvars = {
        'log': pro_Log,
        'request': request,
    }
    return render_to_response('GitLab/log.list.html', kwvars)
