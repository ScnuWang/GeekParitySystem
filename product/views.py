from django.shortcuts import render
from django.http import JsonResponse
from .models import ProductModel,CommentModel
from datetime import datetime
import jieba
from GeekParitySystem.settings import MY_SEG_DICT_PATH
jieba.load_userdict(MY_SEG_DICT_PATH)

def get_product_comment_id(request,original_id):
    comment = CommentModel.objects.filter(project_id=int(original_id)).order_by('-last_updated').limit(3)
    context = {}
    context['comments'] = comment
    return JsonResponse(context)

def get_product(website_id,original_id,keyword):
    # 获取最新的产品信息
    if original_id:
        product = ProductModel.objects.filter(original_id=original_id, website_id=website_id).order_by('-last_updated').first()
    elif keyword:
        product = ProductModel.objects.filter(project_name__contains=keyword, website_id=website_id).order_by('-last_updated').first()
        original_id = product.original_id
    else:
        return
    # 获取产品的历史价格列表
    product_price_list = ProductModel.objects.filter(original_id=original_id, website_id=website_id).order_by('last_updated').values_list('project_price')
    product_price_list = [float(price) for price in product_price_list]
    # 历史价格对应的时间并去重
    product_date_list = ProductModel.objects.filter(original_id=original_id, website_id=website_id).order_by('last_updated').values_list('last_updated')
    product_date_list = [datetime.strptime(date, '%Y-%m-%d %X').strftime('%Y-%m-%d') for date in product_date_list]
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
    comments = CommentModel.objects.filter(project_id=str(original_id),website_id=website_id).order_by('-last_updated').limit(3)
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
    if request.POST.get('keyword') or request.POST.get('website_id'):
        keyword = request.POST.get('keyword')
        website_id = request.POST.get('website_id')
        product_list = ProductModel.objects(project_name__contains=keyword,website_id=website_id)
    else:
        product_list = ProductModel.objects.limit(10)

    context = {}
    context['product_list'] = product_list
    return render(request,'product/product_list.html',context)

def keyword_serach(request):
    pass