from django.shortcuts import render,redirect,reverse
from .forms import LoginForm,RegistForm
from django.contrib import auth
from django.contrib.auth.models import User
from geekuser.models import GeekUser,GeekCode

def home(request):
    return render(request,'index.html')

# 处理登录相关
def login(request):
    # POST请求，则是登录页面发起的登录请求
    if request.POST:
        login_form = LoginForm(request.POST)
        # 判断参数是否合法
        if login_form.is_valid():
            # 登录验证
            auth.login(request,login_form.cleaned_data['user'])
            # 登录成功跳转
            return redirect(reverse('product:product_list',args=[]))
    # 其他请求或者验证出现异常，则认为是跳转到登录页面
    else:
        login_form = LoginForm()
    context = {}
    context['login_form'] = login_form
    return render(request,'registration/login.html',context)

def regist(request):
    if request.POST:
        regist_form = RegistForm(request.POST)
        if regist_form.is_valid():
            # 保存数据
            username = regist_form.cleaned_data['username']
            password = regist_form.cleaned_data['password']
            email = regist_form.cleaned_data['email']
            invation_code = regist_form.cleaned_data['invation_code']
            user = GeekUser.objects.create_user(username=username,email=email,password=password,invation_code=invation_code)
            user.save()

            # 修改邀请码状态
            GeekCode.objects.filter(invation_code=invation_code).update(is_available=False)

            # 页面跳转到登录页面，也可以直接在这里进行授权登录
            auth.login(request,user)
            return redirect(reverse('home',args=[]))
    else:
        regist_form = RegistForm()
    context = {}
    context['regist_form'] = regist_form
    return render(request,'registration/regist.html',context)


