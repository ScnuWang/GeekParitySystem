from django.shortcuts import render
from django.http import JsonResponse
from .models import ProductModel,CommentModel

def get_product_comment_id(request,original_id):
    comment = CommentModel.objects.filter(project_id=int(original_id)).order_by('-last_updated').limit(3)
    context = {}
    context['comments'] = comment
    return JsonResponse(context)

def get_product_by_id(request,original_id):
    # 获取最新的产品信息
    product = ProductModel.objects.filter(original_id=original_id).first()
    # 获取产品的历史价格列表
    product_prict_list = ProductModel.objects.filter(original_id=original_id).order_by('-last_updated').values_list('project_price')
    product_prict_list = [float(n) for n in product_prict_list]
    # 获取对应的最新评论的前3条
    comment = CommentModel.objects.filter(project_id=int(original_id)).order_by('-last_updated').limit(3)
    # print('=====================>',product)
    context = {}
    context['product'] = product
    context['comments'] = comment
    context['product_prict_list'] = product_prict_list
    return render(request,'product/product_detail.html',context)


def get_product_list(request):

    # 关键字查询
    if request.POST.get('keyword'):
        keyword = request.POST.get('keyword')
        product_list = ProductModel.objects(project_name__contains=keyword)
    else:
        product_list = ProductModel.objects.limit(10)

    context = {}
    context['product_list'] = product_list
    return render(request,'product/product_list.html',context)

def keyword_serach(request):
    pass