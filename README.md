# GeekParitySystem
### 数据库
- MySQL：用户信息
- MongoDB：产品信息
使用数据库路由，自动选择数据库

### 微信相关开源库

- [itchat](https://github.com/littlecodersh/ItChat)

修改了部分源码：

    1. itchat/components/login.py
    
    get_QR()方法：1. 注释掉默认打开登录二维码窗口 2. 二维码保存路径以及二维码名称
    