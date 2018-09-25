from django.shortcuts import render,redirect,reverse
from django.http import JsonResponse
from django.forms import model_to_dict
from .forms import LoginForm,RegistForm
from django.contrib import auth
from geekuser.models import GeekUser,GeekCode
from product.models import UniqueProduct
from .settings import QRCODE_IMAGE_PATH,IMAGE_PATH
import qrcode,uuid,itchat,os,time
from .utils import PostMaker,getQRcode

# 由于itchat对象不能直接通过json序列化，后续进行用户登录信息的时候回用到，所以保留全局变量，通过登录时的uuid查询
instancesDic = {}

# 登录成功后进行处理
# args: 用户的uuid编号
def login_success(*args):
    print('登录成功')
    if args:
        pngname = args[0] + '.png'
        os.remove(pngname)
        print('删除登录二维码图片')

# 处理微信登录
def wechat_login(request):
    newInstance = itchat.new_instance()
    # 获取uuid
    while not newInstance.get_QRuuid():
        time.sleep(1)
    # 下载微信二维码
    newInstance.get_QR(enableCmdQR=False,picDir=QRCODE_IMAGE_PATH, qrCallback=None)
    uuid = newInstance.uuid
    instancesDic[uuid] = newInstance
    data = {'qrcode_uuid':uuid,'msg':'操作成功','msg_code':100000}
    return  JsonResponse(data)

# 检查登录状态
def check_login(request):
    # 判断是否包含邀请码
    par_invation_code = None
    try:
        par_invation_code = request.GET['invation_code']
    except:
        pass
    if request.GET['uuid']:
        # 根据uuid查询微信登录相关实例
        uuid = request.GET['uuid']
        itchat_instance = instancesDic[uuid]
        status = itchat_instance.check_login()
        if status == '200':
            itchat_instance.web_init()
            itchat_instance.show_mobile_login()
            itchat_instance.get_contact(True)
            # 获取登录用户的个人信息
            nickName = itchat_instance.loginInfo['User']['NickName']
            # 微信好友列表 (不存入数据库)
            memberList = itchat_instance.memberList
            # 只有wxuin保持不变，并且每个微信号唯一不同
            wxuin = itchat_instance.loginInfo['wxuin']
            # 保留用户基本信息到数据库
            # 判断是否注册
            wechat_user = GeekUser.objects.filter(wxuin=wxuin).first()
            if not wechat_user:
                wechat_user = GeekUser()
                wechat_user.wxuin = wxuin
                wechat_user.nick_name = nickName
                geekcode = GeekCode.objects.filter(is_available=True).first()
                # 判断是否还有可用邀请码
                if not geekcode:
                    # 这里要注意线程安全，后续需要处理一下 ！！！！！！！
                    generate_invation_code()
                wechat_user.invation_code = GeekCode.objects.filter(is_available=True).first().invation_code
                # 判断父邀请码是否有效
                if GeekCode.objects.filter(invation_code=par_invation_code,is_available=False):
                    # 给新用户添加父邀请码
                    wechat_user.par_invation_code = par_invation_code
                    # 查找邀请者并同时给邀请者添加子邀请码并保存
                    invator_user = GeekUser.objects.get(invation_code=par_invation_code)
                    invator_user.sub_invation_code = wechat_user.invation_code
                    invator_user.save()
                # 判断是否是被人邀请的，判断父邀请码

                # 微信用户的用户名为wxuin，密码为invation_code
                wechat_user.username = wxuin
                wechat_user.password = wechat_user.invation_code
                wechat_user.save()
                # 修改邀请码状态
                GeekCode.objects.filter(invation_code=wechat_user.invation_code).update(is_available=False)
            # 将用户信息数据放入模板
            # 这两个字段没有添加到model，所以，前端页面展示不出来
            wechat_user.memberList = memberList[1:]
            wechat_user.uuid = uuid
            # 采用Django自带授权体系给用户授权
            auth.login(request, wechat_user)
            return redirect(reverse('home', args=[]))
    else:
        # 登录异常，请重新登录：通过返回特定参数，启动jquery打开二维码扫描页面
        pass

# 根据发送消息类型
def send(request, uuid, NickName, UserName, invation_code, msg_type):
    """
    :param request:
    :param uuid: 登录时微信分配的uuid
    :param NickName: 用户昵称
    :param UserName: 登录时微信分配的用户名
    :param invation_code: 邀请码
    :param msg_type: 消息类型 1: 文字信息 2：图片信息
    :return:
    """
    itchat_instance = instancesDic[uuid]
    invation_url = 'http://1670a21b58.imwork.net?invation_code='+ invation_code
    if msg_type and msg_type == 1 :
        msg = NickName + ', 我正在使用极客比价，你也来试试吧，立即前往：'+invation_url+' 微信扫码登录！'
        itchat_instance.send(msg,toUserName=UserName)
    if msg_type and msg_type == 2 :
        backImg = IMAGE_PATH + 'post_back_image.png'
        font = IMAGE_PATH + 'msyhl.ttc'
        pMaker = PostMaker(backImg=backImg, font=font)

        # 包含邀请链接的图片文件路径
        qrImg = IMAGE_PATH + uuid + '.png'
        getQRcode(invation_url,qrImg)
        # 海报的文件路径
        post_image = IMAGE_PATH + invation_code + '.png'
        pMaker.create(userName = NickName,qrImg = qrImg,textColor={'R': 0, 'G': 0, 'B': 0},file_name= post_image)
        # 发送海报
        itchat_instance.send_image(post_image,toUserName=UserName)
    return redirect(reverse('home', args=[]))

# 首页
def home(request):
    product_list_1 = UniqueProduct.objects.filter(website_id=1).order_by('-last_updated').limit(8)
    product_list_2 = UniqueProduct.objects.filter(website_id=2).order_by('-last_updated').limit(8)
    products = {'xiaomi':product_list_1,'wangyi':product_list_2}
    context = {}
    context['products'] = products
    context['product_Carousel_active'] = None
    context['product_Carousel_list'] = None
    # 轮播图展示产品 : 小米第一个作为默认激活产品；小米网易各取两个产品
    # 后续根据需要调整一下数据
    product_list_3 = UniqueProduct.objects.filter(website_id=1).order_by('-project_price')
    product_list_4 = UniqueProduct.objects.filter(website_id=2).order_by('-project_price')
    if product_list_3 and product_list_4:
        context['product_Carousel_active'] = product_list_3[0] # 默认激活
        product_Carousel_list = []
        product_Carousel_list.append(product_list_3[1])
        product_Carousel_list.extend(product_list_4[0:2])
        context['product_Carousel_list'] = product_Carousel_list # 默认激活

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