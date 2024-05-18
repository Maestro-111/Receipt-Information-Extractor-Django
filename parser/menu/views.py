from django.shortcuts import render
from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect
from django.template.loader import render_to_string
from django.conf import settings


def main_menu(request):

    context = {
        'receipt':'/static/receipt_image.jpg',
        'information':'/static/data.png'
    }

    return render(request,'menu/menu_temp.html',context)



def parse_multiple(request):

    multiple_receipt_url = reverse('multiple_receipt')

    return redirect(multiple_receipt_url)


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1> No such Page!! </h1>")