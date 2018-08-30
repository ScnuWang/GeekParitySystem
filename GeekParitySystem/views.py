from django.shortcuts import render,redirect,reverse
from .forms import LoginForm,RegistForm
from django.contrib import auth
from geekuser.models import GeekUser,GeekCode
from product.models import ProductModel
from .settings import QRCODE_IMAGE_PATH
import qrcode,uuid

# 首页
def home(request):
    product_list_1 = ProductModel.objects.filter(website_id=1).order_by('-last_updated').limit(8)
    product_list_2 = ProductModel.objects.filter(website_id=2).order_by('-last_updated').limit(8)
    products = {'xiaomi':product_list_1,'wangyi':product_list_2}
    context = {}
    # 轮播图展示产品 : 小米第一个作为默认激活产品；小米网易各取两个产品
    # 后续调整一下数据
    context['product_Carousel_active'] = product_list_1[0] # 默认激活
    product_Carousel_list = []
    product_Carousel_list.append(product_list_1[1])
    product_Carousel_list.extend(product_list_2[0:2])
    context['product_Carousel_list'] = product_Carousel_list # 默认激活
    context['products'] = products
    return render(request,'index.html',context)

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
            return redirect(reverse('home',args=[]))
    # 其他请求或者验证出现异常，则认为是跳转到登录页面
    else:
        login_form = LoginForm()
    context = {}
    context['login_form'] = login_form
    return render(request,'registration/login.html',context)

# 处理注册相关
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
    # 由于邀请码的链接是变量，所以需要将邀请码的链接名称当做参数传入，否则在渲染的时候，不知道变量的值是什么
    context['get_invation_qrcode'] = 'get_invation_qrcode'
    return render(request,'registration/regist.html',context)


# 处理注销相关
def logout(request):
    auth.logout(request)
    return redirect(reverse('home',args=[]))

# 邀请码获取 并生成图片，让用户扫描二维码获取图片，这样设计师用户体验很差，不够方便
# 可以在用户分享的时候，通过用户信息，生成相应二维码，完成图片分享
# 但是如果直接通过注册页面点击一个按钮就获取邀请码，就没人会愿意用别人的邀请码了
# 可以导流到微信公众号
def get_invation_qrcode(request):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    code = GeekCode.objects.filter(is_available=True).first()
    if code:
        qr.add_data("您的专属邀请码为："+code.invation_code)
    else:
        generate_invation_code()
        code = GeekCode.objects.filter(is_available=True).first()
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(QRCODE_IMAGE_PATH + str(code.invation_code)+'.png')
    context = {}
    context['invation_code'] =  'qrcode/'+ code.invation_code + '.png'
    return render(request,'qrcode.html',context)

# 生成邀请码
def generate_invation_code():
    for i in range(1, 10001):
        geek_code = GeekCode()
        geek_code.is_available = True
        geek_code.invation_code = str(uuid.uuid1()).split('-')[0]
        geek_code.save()