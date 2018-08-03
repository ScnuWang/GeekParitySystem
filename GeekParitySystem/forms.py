from django import forms
from django.contrib import auth
from geekuser.models import GeekUser,GeekCode

class LoginForm(forms.Form):
    username = forms.CharField(label='用户名',widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'请输入用户名'}),max_length=32,min_length=3)
    password = forms.CharField(label='密码',widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'请输入密码'}),max_length=32,min_length=6)

    # 校验
    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        user = auth.authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError('用户名或密码不正确')
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data


class RegistForm(forms.Form):
    username = forms.CharField(label='用户名',widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'请输入用户名'}),max_length=32,min_length=3)
    email = forms.EmailField(label='邮箱',widget=forms.EmailInput(attrs={'class': 'form-control','placeholder':'请输入邮箱地址'}))
    password = forms.CharField(label='密码',widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'请输入密码'}),max_length=32,min_length=6)
    password_again = forms.CharField(label='确认密码',widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'请输入密码'}),max_length=32,min_length=6)
    invation_code = forms.CharField(label='邀请码',widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'请输入邀请码'}),min_length=6,max_length=8)

    # 字段验证
    def clean_username(self):
        username = self.cleaned_data['username']
        if GeekUser.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已经存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if GeekUser.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱已经注册')
        return email

    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']

        if password != password_again:
            raise forms.ValidationError('两次输入的密码不一致')

        return password

    def clean_invation_code(self):
        invation_code = self.cleaned_data['invation_code']

        if GeekCode.objects.filter(invation_code=invation_code,is_available = True):
            return invation_code
        else:
            raise forms.ValidationError('请输入有效的邀请码')
