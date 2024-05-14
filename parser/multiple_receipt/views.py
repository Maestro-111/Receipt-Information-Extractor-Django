from django.shortcuts import render
from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect
from django.template.loader import render_to_string
from django.conf import settings
import os
import shutil
from ocr import run_craft
from ocr import text_extraction
from  create_folders import create_folders

def delete_files_in_directory(directory_path):
    files = os.listdir(directory_path)
    for file_name in files:
        file_path = os.path.join(directory_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted: {file_path}")
    print("All files deleted successfully.")



def index(request):

    context = {
            'folder_path': '/static/folder.png',
    }


    return render(request,'multiple_receipt/parse_multiple.html',context)


def upload_multiple_receipts(request):

    if request.method == 'POST' and request.FILES.get('receipt_images'):

        receipt_images = request.FILES.getlist('receipt_images')

        create_folders(settings.MULTIPLE_RECEIPT_DIR)

        for uploaded_file in receipt_images:

            file_path = os.path.join(settings.MULTIPLE_MEDIA_ROOT, uploaded_file.name)
            test_path = os.path.join(settings.MULTIPLE_TEST_ROOT, uploaded_file.name)

            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

        images = os.listdir(settings.MULTIPLE_MEDIA_ROOT)

        for image in images:

            file_path = os.path.join(settings.MULTIPLE_MEDIA_ROOT, image)
            test_path = os.path.join(settings.MULTIPLE_TEST_ROOT, image)

            shutil.copy(file_path, test_path)

        run_craft(path=settings.MULTIPLE_RECEIPT_DIR, multiple=True)

        delete_files_in_directory(os.path.join(settings.MULTIPLE_RECEIPT_DIR,'test'))
        delete_files_in_directory(os.path.join(settings.MULTIPLE_RECEIPT_DIR, 'result'))
        delete_files_in_directory(os.path.join(settings.MULTIPLE_RECEIPT_DIR, 'test_boxes_from_craft/coords'))
        delete_files_in_directory(os.path.join(settings.MULTIPLE_RECEIPT_DIR, 'test_boxes_from_craft/imgs'))
        delete_files_in_directory(os.path.join(settings.MULTIPLE_RECEIPT_DIR, 'uploads'))

       # add parsing txt logic database?


       #delete_files_in_directory(os.path.join(settings.MULTIPLE_RECEIPT_DIR, 'txt_output'))

        return HttpResponse(f"Success")

    else:
        return HttpResponse(f"error")
