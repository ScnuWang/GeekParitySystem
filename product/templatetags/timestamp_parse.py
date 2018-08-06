from django import template
from datetime import datetime


register = template.Library()

@register.filter(expects_localtime=True, is_safe=False)
def timestamp_parse(value, format_string):
    if value in (None, ''):
        return ''
    # 由于网易严选的时间戳没有小数点会导致报错，故只去掉小数部分的时间戳
    value = int(str(value)[0:10])
    return datetime.fromtimestamp(value).strftime(format_string)
