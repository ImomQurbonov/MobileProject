# import os
#
# from skimage.metrics import structural_similarity
# import cv2
#
# absolute_path = '/media/file'
# temporarily_path = '/media/temporarily/'
#
#
# def get_all_image_paths():
#     directory = absolute_path
#     files = os.listdir(directory)
#     image_files = []
#     for image in files:
#         if image.endswith(('.jpg', '.jpeg', '.png', '.gif')):
#             image_files.append(image)
#     return image_files
#
#
# def check_image_similarity(photo_path: str):
#     own_image_data = get_all_image_paths()
#     photo_data = []
#     for image in own_image_data:
#         first_photo = cv2.imread(f'{absolute_path}/{image}')
#         second_photo = cv2.imread(f'{temporarily_path}{photo_path}')
#
#         first_gray = cv2.cvtColor(first_photo, cv2.COLOR_BGR2GRAY)
#
#         second_photo_resized = cv2.resize(second_photo, (first_photo.shape[1], first_photo.shape[0]))
#
#         second_gray = cv2.cvtColor(second_photo_resized, cv2.COLOR_BGR2GRAY)
#
#         score, diff = structural_similarity(first_gray, second_gray, full=True)
#
#         result_percentage = "{:.3f}".format(score * 100)
#
#         photo_data.append({image: result_percentage})
#
#     return photo_data
