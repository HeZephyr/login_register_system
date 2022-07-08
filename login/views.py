from django.shortcuts import render, redirect
from django.conf import settings
from .models import User, ConfirmString
from . import forms
import hashlib
import datetime


# Create your views here.
def index(request):
    # 说明没有登录
    if not request.session.get('is_login', None):
        return redirect('/login/')
    return render(request, 'login/index.html')


def login(request):
    # 不允许重复登录
    if request.session.get('is_login', None):
        return redirect('/index/')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        login_form = forms.UserForm(request.POST)
        message = "用户名或密码为空"
        # 需要删除前面的空格和后面的空格
        # 进行数据验证
        if login_form.is_valid():
            # 获取表单的具体值
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            # 判断是否存在该用户
            try:
                user = User.objects.get(name=username)
            except User.DoesNotExist:
                message = "用户不存在"
                return render(request, 'login/login.html', locals())
            if not user.has_confirmed_email:
                message = '该用户还未经过邮件确认！'
                return render(request, 'login/login.html', locals())
            if user.password == hash_code(password):
                # 登录成功，写入用户状态和数据
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('/index/')
            else:
                message = "密码不正确"
                return render(request, 'login/login.html', locals())
        else:
            return render(request, 'login/login.html', locals())
    login_form = forms.UserForm()
    return render(request, 'login/login.html', locals())


def logout(request):
    # 删除用户的相关信息
    request.session.pop('is_login', None)
    request.session.pop('user_name', None)
    request.session.pop('user_id', None)
    return redirect('/login/')


def register(request):
    if request.session.get('is_login', None):
        return redirect('/index/')
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = '注册信息填写不完整！'
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password = register_form.cleaned_data['password']
            confirm_password = register_form.cleaned_data['confirm_password']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password != confirm_password:
                message = '两次输入的密码不一致！'
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = User.objects.filter(name=username)
                if same_name_user:
                    message = '用户名已经存在！'
                    return render(request, 'login/register.html', locals())
                same_email_user = User.objects.filter(email=email)
                if same_email_user:
                    message = '邮箱已经注册了！'
                    return render(request, 'login/register.html', locals())
                new_user = User()
                new_user.name = username
                new_user.password = hash_code(password)
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                code = make_confirm_string(new_user)
                send_email(email, code)

                message = '请前往邮箱确认!'
                return render(request, 'login/confirm.html', locals())
        else:
            return render(request, 'login/register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())


# 密码加密算法
def hash_code(s, salt='login_register_system'):
    h = hashlib.sha256()
    s += salt
    # update方法只能接收bytes类型
    h.update(s.encode())
    return h.hexdigest()


def make_confirm_string(user):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    code = hash_code(user.name, now)
    ConfirmString.objects.create(user=user, code=code)
    return code


def send_email(email, code):

    from django.core.mail import EmailMultiAlternatives

    subject = '注册确认邮件'

    text_content = '感谢注册！如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'

    html_content = '''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.liujiangblog.com</a>，\
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def user_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = ConfirmString.objects.get(code=code)
    except ConfirmString.DoesNotExist:
        message = '无效的确认请求!'
        return render(request, 'login/confirm.html', locals())

    create_time = confirm.create_time
    now = datetime.datetime.now()
    if now > create_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已经过期！请重新注册!'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed_email = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
        return render(request, 'login/confirm.html', locals())
