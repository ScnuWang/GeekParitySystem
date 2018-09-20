from django.shortcuts import render,reverse,redirect
from django.http import JsonResponse
from django.core import serializers
from .models import ProductModel,CommentModel,UniqueProduct,Category
import datetime
import jieba,json
import jieba.analyse
from GeekParitySystem.settings import MY_SEG_DICT_PATH,MY_CATEGORY_PATH,ENABLE_WEBSITE_DIC
jieba.load_userdict(MY_SEG_DICT_PATH)

def get_product_comment_id(request,original_id):
    # 解决提示错误：Object of type 'QuerySet' is not JSON serializable
    comment = serializers.serialize('json',CommentModel.objects.filter(project_id=int(original_id)).order_by('-last_updated').limit(3))
    context = {}
    context['comments'] = comment
    return JsonResponse(context)

def get_product(website_id,original_id,keyword):
    # 获取最新的产品信息
    if original_id:
        product = ProductModel.objects.filter(original_id=original_id, website_id=website_id).order_by('-last_updated').first()
    elif keyword:
        product = ProductModel.objects.filter(project_name__contains=keyword, website_id=website_id).order_by('-last_updated').first()
        if product:
            original_id = product.original_id
        else:
            return None,None,None
    else:
        return None,None,None
    # 获取产品的历史价格列表
    product_price_list = ProductModel.objects.filter(original_id=original_id, website_id=website_id).order_by('last_updated').values_list('project_price')
    product_price_list = [float(price) for price in product_price_list]
    # 历史价格对应的时间
    product_date_list = ProductModel.objects.filter(original_id=original_id, website_id=website_id).order_by('last_updated').values_list('last_updated')
    product_date_list = [date.strftime('%Y-%m-%d') for date in product_date_list]
    return product,product_price_list,product_date_list

def get_product_by_id(request,website_id,original_id):
    # 从原始抓取回来的collection中获取产品信息
    product, product_price_list, product_date_list = get_product(website_id,original_id,keyword=None)
    # 获取对应的最新评论的前3条
    comments = CommentModel.objects.filter(project_id=original_id,website_id=website_id).order_by('-last_updated')
    # print('=====================>',product)
    # 从分类后的collection中获取某个产品同一类的数据信息
    unique_product = UniqueProduct.objects.filter(original_id=original_id, website_id=website_id,category_status=1).first()
    # 已分类:查询同类产品的最高价，最低价
    product_price_max,product_price_min = 0.0, 0.0
    if unique_product:
        # unique = UniqueProduct.objects.filter(category_id = unique_product.category_id).order_by('-project_price')
        product_price_max =  UniqueProduct.objects.filter(category_id = unique_product.category_id).order_by('-project_price').first().project_price
        # 不知道为什么提示：'QuerySet' object has no attribute 'last'
        product_price_min =  UniqueProduct.objects.filter(category_id = unique_product.category_id).order_by('project_price').first().project_price
    # 未分类
    context = {}
    context['product'] = product
    context['comments'] = comments.limit(3)
    # 历史数据列表--折线图数据
    context['product_price_list'] = product_price_list
    context['product_date_list'] = product_date_list
    # 柱形图数据
    context['people_support'] = len(comments)
    context['product_price_max'] = product_price_max
    context['product_price_min'] = product_price_min
    return render(request,'product/product_detail.html',context)


def get_product_list(request):
    # 关键字查询
    keyword = request.POST.get('keyword')
    website_id = request.POST.get('website_id')
    product_list = []
    # 只是关键字查询
    if keyword and not website_id :
        for product in UniqueProduct.objects.all():
            if keyword in product.tags:
                product_list.append(product)
    # 只是平台查询
    elif website_id and not keyword:
         product_list = UniqueProduct.objects.filter(website_id=website_id)
    # 关键字和平台混合查询
    elif website_id and keyword:
        for product in UniqueProduct.objects.filter(website_id=website_id):
            if keyword in product.tags:
                product_list.append(product)
    else:
        product_list = ProductModel.objects.limit(10)
    context = {}
    context['product_list'] = product_list
    return render(request,'product/product_list.html',context)

# 分词分类,将抓取的产品信息保留最新的数据到UniqueProduct
def classify(request):
    # 如果数据库没有分类数据，则初始化分类数据
    if not Category.objects.all():
        with open(MY_CATEGORY_PATH, encoding='UTF-8') as file:
            json_categorylist = json.loads(file.read())
            for json_category in json_categorylist:
                category = Category()
                category.category_id = json_category['category_id']
                category.category_name = json_category['category_name']
                category.tags = json_category['tags']
                category.save()
    #  获取分类数据
    category_tags_dic = {category_id:tags for category_id,tags in Category.objects.all().values_list('category_id','tags')}

    # 获取上一次抓取（抓取频率做相应的调整）的产品数据全部产品数据
    # nontags_products = ProductModel.objects.filter(last_updated__gt=datetime.datetime.now().date() + datetime.timedelta(days=-1))
    nontags_products =  ProductModel.objects.all()
    # 更新产品数据
    for product in nontags_products:
        # 如果未收录，则进行分词分类等
        unique_product = UniqueProduct.objects.filter(original_id=product.original_id,website_id=product.website_id)
        if not unique_product:
            # 对没有分类的没每一个产品进行分类
            unique_product = UniqueProduct()
            unique_product.project_name = product['project_name']
            unique_product.original_id = product['original_id']
            unique_product.website_id = product['website_id']
            unique_product.project_price = product['project_price']
            unique_product.project_url = product['project_url']
            unique_product.project_picUrl = product['project_picUrl']
            unique_product.project_score = product['project_score']
            unique_product.project_platform = product['project_platform']
            tags_from_serach = jieba.lcut_for_search(product.project_name)# jieba引擎模式，直接返回list
            tags = jieba.analyse.extract_tags(product.project_name, topK=20, withWeight=False, allowPOS=()) # 分析模式
            # 为了尽可能多的分词，所以就结合两种模式，取并集设立关键字，并去除空格
            tags.extend([tag for tag in tags_from_serach if tag not in ('',' ','  ')])
            unique_product.tags = list(set(tags))
            unique_product.tags_status = 1
            unique_product.tags_time = datetime.datetime.now()
            # 处理产品分类信息取第一个匹配的分类： 这个分类方案不完善，
            for category_id,category_tags in category_tags_dic.items():
                # 通过两个list有交集来判断产品关键字里面是否包含在分类关键字里面
                if list(set(tags).intersection(set(category_tags))):
                    unique_product.category_id = category_id
                    unique_product.category_status = 1
                    break
            unique_product.last_updated = datetime.datetime.now()
            unique_product.save()
        #     如果已收录但是为分类，则进行分类
        # elif unique_product.category_status == 0:
        #     pass
        # 如果已收录已分类，则直接更新价格数据等等
        else:
            unique_product.update(project_price=product['project_price'], project_score = product['project_score'])
    return redirect(reverse('home',args=[]))

# 对某个产品进行分类
def classify_for_product(unique_product):
    pass




# 菜单获取产品列表
def get_products_by_category(request,category_id):
    product_list_1 = []
    product_list_2 = []
    for product in UniqueProduct.objects.all():
        if category_id in  product.category_id and product.website_id == 1:
            product_list_1.append(product)
        if category_id in  product.category_id and product.website_id == 2:
            product_list_2.append(product)
    products = {'xiaomi': product_list_1, 'wangyi': product_list_2}
    context = {}
    context['products'] = products
    return render(request, 'index.html', context)