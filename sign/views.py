from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event, Guest
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.

def index(request):
    return render(request, 'index.html')


def login_action(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            response = HttpResponseRedirect('/event_manage/')
            # response.set_cookie('user', username, 3600) # 添加浏览器cookie
            request.session['user'] = username  # 将 session 信息记录到浏览器
            return response
        else:
            return render(request, 'index.html', {'error': 'username or password error!'})


@login_required
def event_manage(request):
    # username = request.COOKIES.get('user','')  # 读取浏览器cookie
    username = request.session.get('user', '')  # 读取浏览器 session
    event_list = Event.objects.all()
    return render(request, 'event_manage.html', {'user': username, 'events': event_list})


@login_required
def search_name(request):
    username = request.session.get('user', '')
    search_name = request.GET.get('name', '')
    event_list = Event.objects.filter(name__contains=search_name)
    return render(request, 'event_manage.html', {'user': username, 'events': event_list})


@login_required
def guest_manage(request):
    # username = request.COOKIES.get('user','')  # 读取浏览器cookie
    username = request.session.get('user', '')  # 读取浏览器 session
    guest_list = Guest.objects.all()
    paginator = Paginator(guest_list, 10)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # 如果page不是整数，取第一页面数据
        contacts = paginator.page(1)
    except EmptyPage:
        # 如果page不在范围，取最后一页面
        contacts = paginator.page(paginator.num_pages)
    return render(request, 'guest_manage.html', {'user': username, 'guests': contacts})


@login_required
def search_name_email_phone(request):
    username = request.session.get('user', '')
    search_text = request.GET.get('search_text', '')
    guest_list = Guest.objects.filter(
        Q(realname__contains=search_text) | Q(phone__contains=search_text) | Q(email__contains=search_text) | Q(
            event__name__contains=search_text))
    paginator = Paginator(guest_list, 10)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # 如果page不是整数，取第一页面数据
        contacts = paginator.page(1)
    except EmptyPage:
        # 如果page不在范围，取最后一页面
        contacts = paginator.page(paginator.num_pages)
    return render(request, 'guest_manage.html', {'user': username, 'guests': contacts, 'search_text': search_text})


@login_required
def sign_index(request, eid):
    event = get_object_or_404(Event, id=eid)
    total_nunber = Event.objects.get(id=eid).limit
    signed_number = Guest.objects.filter(event_id=eid, sign=True).count()
    return render(request, 'sign_index.html',
                  {'event': event, 'signed_number': signed_number, 'total_number': total_nunber})


@login_required
def sign_index_action(request, eid):
    event = get_object_or_404(Event, id=eid)
    phone = request.POST.get('phone', '')
    total_nunber = Event.objects.get(id=eid).limit
    signed_number = Guest.objects.filter(event_id=eid, sign=True).count()

    result = Guest.objects.filter(phone=phone)
    if not result:
        return render(request, 'sign_index.html', {'event': event, 'hint': '该手机号用户不存在。', 'signed_number': signed_number,
                                                   'total_number': total_nunber})
    result = Guest.objects.filter(phone=phone, event_id=eid)
    if not result:
        return render(request, 'sign_index.html',
                      {'event': event, 'hint': '手机号和发布会不匹配。', 'signed_number': signed_number,
                       'total_number': total_nunber})
    result = Guest.objects.get(phone=phone, event_id=eid)
    if result.sign:
        return render(request, 'sign_index.html',
                      {'event': event, 'hint': '用户已经签到。', 'signed_number': signed_number, 'total_number': total_nunber})
    else:
        Guest.objects.filter(phone=phone, event_id=eid).update(sign='1')
        signed_number = Guest.objects.filter(event_id=eid, sign=True).count()
        return render(request, 'sign_index.html',
                      {'event': event, 'hint': '成功签到！', 'guest': result, 'signed_number': signed_number,
                       'total_number': total_nunber})

@login_required
def logout(request):
    auth.logout(request)
    response=HttpResponseRedirect('/index/')
    return response