from mongoengine import Document,StringField,IntField,DecimalField,DateTimeField,ListField
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
    # 标签关键字
    tags = ListField()
    # 设置关键字的人 默认值：Geekview
    tags_user = ListField()
    # 设置关键字的时间
    tags_time = DateTimeField()
    # 关键字状态 0：未分词或分词异常 1：已分词
    tags_status = IntField()
    # 评论数
    comment_count = IntField()
    # 更新时间
    last_updated = DateTimeField()

# 提取所有的产品信息
class UniqueProduct(Document):
    meta = {'collection': 'unique_product'}
    # 原始产品编号
    original_id = StringField()
    # 产品归属平台  (网易：1；小米：2)
    website_id = IntField()
    # 分类编号,一个产品可能属于多个分类,但是这样处理下相关业务逻辑的时候会比较麻烦:比如根据某一个分类来查询产品列表
    # category_id = ListField()
    category_id = IntField(default=0)
    # 关键字状态 0：未分类或分类异常 1：已分类
    category_status = IntField(default=0)
    # 产品名称
    project_name = StringField()
    # 产品价格
    project_price = DecimalField()
    # 产品地址
    project_url = StringField()
    # 产品销售商
    project_platform = StringField()
    # 产品评分
    project_score = StringField()
    # 产品图片
    project_picUrl = StringField()
    # 标签关键字
    tags = ListField()
    # 关键字状态 0：未分词或分词异常 1：已分词
    tags_status = IntField()
    # 设置关键字的人 默认值：Geekview
    tags_user = ListField(default=['Geekview'])# 设置这个字段是为了后面推出用户自建来分词，并记录用户
    # 设置关键字的时间
    tags_time = DateTimeField()
    tags_status = IntField()
    # 评论数
    comment_count = IntField()
    # 第一次收录时间
    first_updated = DateTimeField()
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

class Category(Document):
    # 指定collection
    meta = {'collection': 'category'}
    # 分类编号
    category_id = IntField(primary_key=True)
    # 分类名称
    category_name = StringField()
    # 分类关键字
    tags = ListField()
