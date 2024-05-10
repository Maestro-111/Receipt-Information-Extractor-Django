import os
from django.conf import settings

def create_folder_if_not_exists(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        # If the folder doesn't exist, create it
        os.makedirs(folder_path)
        print(f"Folder created: {folder_path}")
    else:
        print(f"Folder already exists: {folder_path}")



def create_folders():

    create_folder_if_not_exists(os.path.join(settings.SINGLE_RECEIPT_DIR,"tets_boxes_from_craft/coords"))
    create_folder_if_not_exists(os.path.join(settings.SINGLE_RECEIPT_DIR,"tets_boxes_from_craft/imgs"))
    create_folder_if_not_exists(os.path.join(settings.SINGLE_RECEIPT_DIR,"uploads"))
    create_folder_if_not_exists(os.path.join(settings.SINGLE_RECEIPT_DIR,"exports"))
    create_folder_if_not_exists(os.path.join(settings.SINGLE_RECEIPT_DIR,"test"))
    create_folder_if_not_exists(os.path.join(settings.SINGLE_RECEIPT_DIR,"result"))

    with open('exports/number.txt', 'w') as file:
        file.write(f'{0}')

if __name__ == '__main__':
    create_folders()