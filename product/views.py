from django.shortcuts import render
from .models import ProductModel,CommentModel


def get_product_by_id(request,original_id):
    print('=====================>',original_id)
    product = ProductModel.objects.first()
    comment = CommentModel.objects.first()
    context = {}
    context['product'] = product
    context['comment'] = comment
    return render(request,'product/product_detail.html',context)


def get_product_list(request):
    product_list = ProductModel.objects.filter(original_id='1478002')

    context = {}
    context['product_list'] = product_list
    return render(request,'product/product_list.html',context)
