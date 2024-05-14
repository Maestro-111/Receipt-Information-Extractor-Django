
from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect
from django.template.loader import render_to_string
from django.conf import settings
import os
import shutil
import subprocess
import pandas as pd
from ocr import run_craft
from ocr import text_extraction
from create_folders import create_folders


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
            'good_path': '/static/good.jpeg',
            'bad_path': '/static/bad.jpg'
    }

    return render(request,'single_receipt/index_1_1.html',context)



def download_receipt(request):
    output_path = request.GET.get('output_path')

    if output_path:
        filename = os.path.basename(output_path)  # Get the filename from the path
        context = {
            'output_path': output_path,
            'filename': filename,
            'path': '/static/success_1.jpg'
        }
        return render(request, 'single_receipt/result_1_1.html', context)

    else:
        return HttpResponse("Error downloading file.")


def download_file(request, filename):

    file_path = os.path.join(settings.EXPORTS_DIR, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    else:
        return HttpResponse("File not found", status=404)



def upload_receipt(request):  # Updated function name
    if request.method == 'POST' and request.FILES.get('receipt_image'):

        create_folders(settings.SINGLE_RECEIPT_DIR)

        receipt_image = request.FILES['receipt_image']
        file_path = os.path.join(settings.SINGLE_MEDIA_ROOT,receipt_image.name)

        test_path = os.path.join(settings.SINGLE_TEST_ROOT, receipt_image.name)

        with open(file_path, 'wb+') as destination:
            for chunk in receipt_image.chunks():
                destination.write(chunk)

        images = os.listdir(settings.SINGLE_MEDIA_ROOT)

        for image in images:
            shutil.copy(file_path, test_path)

        run_craft(settings.SINGLE_RECEIPT_DIR)


        delete_files_in_directory(os.path.join(settings.SINGLE_RECEIPT_DIR,'test'))
        delete_files_in_directory(os.path.join(settings.SINGLE_RECEIPT_DIR, 'result'))
        delete_files_in_directory(os.path.join(settings.SINGLE_RECEIPT_DIR, 'test_boxes_from_craft/coords'))
        delete_files_in_directory(os.path.join(settings.SINGLE_RECEIPT_DIR, 'test_boxes_from_craft/imgs'))
        delete_files_in_directory(os.path.join(settings.SINGLE_RECEIPT_DIR, 'uploads'))

        with open(os.path.join(settings.SINGLE_RECEIPT_DIR,'text_output.txt'), 'r') as file:
            lines = file.readlines()

        txt_output = [line.strip() for line in lines]
        txt_output = [line for line in txt_output if line]


        with open(os.path.join(settings.SINGLE_RECEIPT_DIR,'text_output.txt'), 'w') as file:
            file.write(" ")

        output_path = os.path.join(settings.SINGLE_RECEIPT_DIR, f'exports/output.xlsx')


        if len(txt_output)>0:

            extarcted_text,product_text = text_extraction(txt_output) # dict


            general_info = pd.DataFrame(extarcted_text)
            product_info = pd.DataFrame(product_text)

            general_info["Image Name"] = receipt_image.name

            output_path = os.path.join(settings.SINGLE_RECEIPT_DIR, f'exports/output.xlsx')

            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                general_info.to_excel(writer, sheet_name='general_info', index=False)

            with pd.ExcelWriter(output_path, engine='openpyxl', mode='a') as writer:
                product_info.to_excel(writer, sheet_name='product_info', index=False)

            return HttpResponseRedirect(reverse('download_receipt') + f'?output_path={output_path}')

        else:
            context = {
             'path': '/static/failure_1.jpg'
            }

            return render(request,'single_receipt/result_2_2.html',context)

    else:
        return HttpResponse("Error uploading receipt.")

