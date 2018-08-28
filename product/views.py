from django.shortcuts import render,reverse,redirect
from django.http import JsonResponse
from django.core import serializers
from .models import ProductModel,CommentModel,UniqueProduct,Category
from datetime import datetime
import jieba,json
import jieba.analyse
from GeekParitySystem.settings import MY_SEG_DICT_PATH,MY_CATEGORY_PATH
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
    product, product_price_list, product_date_list = get_product(website_id,original_id,keyword=None)
    # 其他平台此类产品信息
    product_name = product.project_name
    seg_list = jieba.lcut(product_name,cut_all=False)
    xiaomi_product,xiaomi_product_price_list,xiaomi_product_date_list = None,None,None
    wangyi_product,wangyi_product_price_list,wangyi_product_date_list = None,None,None
    for word in seg_list:
        if jieba.user_word_tag_tab.__contains__(word):
                xiaomi_product,xiaomi_product_price_list,xiaomi_product_date_list = get_product(keyword=word,website_id=1,original_id=None)
                wangyi_product,wangyi_product_price_list,wangyi_product_date_list = get_product(keyword=word,website_id=2,original_id=None)
                break
    # 获取对应的最新评论的前3条
    comments = CommentModel.objects.filter(project_id=original_id,website_id=website_id).order_by('-last_updated').limit(3)
    # print('=====================>',product)
    context = {}
    context['product'] = product
    context['comments'] = comments
    context['product_price_list'] = product_price_list
    context['product_date_list'] = product_date_list
    context['xiaomi_product'] = xiaomi_product
    context['xiaomi_product_price_list'] = xiaomi_product_price_list
    context['wangyi_product'] = wangyi_product
    context['wangyi_product_price_list'] = wangyi_product_price_list
    return render(request,'product/product_detail.html',context)


def get_product_list(request):
    # 关键字查询
    if request.POST.get('keyword'):
        keyword = request.POST.get('keyword')
        product_list = []
        for product in UniqueProduct.objects.all():
            if keyword in product.tags:
                product_list.append(product)
    else:
        product_list = ProductModel.objects.limit(10)
    context = {}
    context['product_list'] = product_list
    return render(request,'product/product_list.html',context)

# 分词分类
def classify(request):
    nontags_products = ProductModel.objects.filter(tags_status=0,last_updated__gt=datetime.now().date())
    # 初始化分类数据
    if not Category.objects.all():
        with open(MY_CATEGORY_PATH, encoding='UTF-8') as file:
            json_categorylist = json.loads(file.read())
            for json_category in json_categorylist:
                category = Category()
                category.category_id = json_category['category_id']
                category.category_name = json_category['category_name']
                category.tags = json_category['tags']
                category.save()

    #   避免多次查询数据库
    category_tags_dic = {category_id:tags for category_id,tags in Category.objects.all().values_list('category_id','tags')}
    for product in nontags_products:
        if not UniqueProduct.objects.filter(original_id=product.original_id,website_id=product.website_id):
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
            # tags = jieba.lcut_for_search(product.project_name)# jieba引擎模式，直接返回list
            tags = jieba.analyse.extract_tags(product.project_name, topK=20, withWeight=False, allowPOS=())
            unique_product.tags = tags
            unique_product.tags_status = 1
            category_list = []
            # 处理产品分类信息
            for category_id,category_tags in category_tags_dic.items():
                # 通过两个list有交集来判断产品关键字里面是否包含在分类关键字里面
                if list(set(tags).intersection(set(category_tags))):
                    category_list.append(category_id) # 一个产品可能有多个分类
                    unique_product.category_status = 1

            unique_product.category_id = category_list
            unique_product.last_updated = datetime.now()
            unique_product.save()
    return redirect(reverse('home',args=[]))

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