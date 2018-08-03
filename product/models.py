from django.db import models
from mongoengine import Document,StringField,IntField,DecimalField,DateTimeField
# Create your models here.
class ProductModel(Document):
    # 指定collection
    meta={'collection': 'projects'}
    # 原始产品编号
    original_id = StringField()
    # 产品归属平台  (网易：1；小米：2)
    website_id = IntField()
    # 产品名称
    project_name = StringField()
    # 产品价格
    project_price = DecimalField()
    # 产品地址
    project_url = StringField()
    # 产品简介
    project_desc = StringField()
    # 产品销售商
    project_platform = StringField()
    # 产品评分
    project_score = StringField()
    # 产品图片
    project_picUrl = StringField()
    # 更新时间
    last_updated = DateTimeField()


class CommentModel(Document):
    # 指定collection
    meta = {'collection': 'comments'}

    # 产品归属平台  (网易：1；小米：2)
    website_id = IntField()
    # 产品编号
    project_id = StringField()
    # 评论人
    comment_user = StringField()
    # 产品评论
    comment_content = StringField()
    # 评论时间
    comment_time = DateTimeField()
    # 更新时间
    last_updated = DateTimeField()