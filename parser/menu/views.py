from django.shortcuts import render
from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect
from django.template.loader import render_to_string
from django.conf import settings


def main_menu(request):
    return render(request,'menu/menu_temp.html')


def parse_single(request):
    single_receipt_url = reverse('single_receipt')
    return redirect(single_receipt_url)



def parse_multiple(request):

    multiple_receipt_url = reverse('multiple_receipt')

    return redirect(multiple_receipt_url)
