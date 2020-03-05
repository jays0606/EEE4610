import glob
import numpy as np
import cv2

image_path = "./remove_250/image"
mask_path = "./remove_250/mask"

image_list = glob.glob(image_path + "/*")
mask_list = glob.glob(image_path + "/*")

print("Num of image :", len(image_list))
print("Num of mask :", len(mask_list))

lung_buf = 0
lung_list = []
image_list = []

for mask_dir in mask_list: #./remove_250/image\001_000067.jpg
    image_list.append(mask_dir.split("\\")[1])
    if lung_buf != int((mask_dir.split("\\")[1]).split("_")[0]):
        lung_list.append(int((mask_dir.split("\\")[1]).split("_")[0]))
        lung_buf = int((mask_dir.split("\\")[1]).split("_")[0])

print("\nFound " + str(len(lung_list)) + " lungs")
print("Found " + str(len(image_list)) + " images")

def make_concat_img(img, gt):
    ret, gt = cv2.threshold(gt,127,255,cv2.THRESH_BINARY)

    gt_ori = gt.copy()

    gt_ori_white = img.copy()
    gt_ori_white[:,:,0] = gt_ori
    gt_ori_white[:,:,1] = gt_ori
    gt_ori_white[:,:,2] = gt_ori

    gt_ori_g = img.copy()
    gt_ori_g[:,:,0] = 0
    gt_ori_g[:,:,1] = 0
    gt_ori_g[:,:,2] = gt_ori

    gt_edge = cv2.Canny(gt, 50, 150)

    gt_color = img.copy()
    gt_color[:,:,0] = 0
    gt_color[:,:,1] = 0
    gt_color[:,:,2] = gt_edge

    gt_sum = cv2.add(img.copy(),gt_color.copy())

    return gt_sum

def high_and_low(img, high, low):
    img = np.array(img, dtype="uint16")
    img[img > 5] = img[img > 5] + (255 - high)
    img[img < low] = 0
    img[img > 255] = 255
    img = np.array(img, dtype="uint8")

    return img

def onChange(x): 
    pass 

def load_list(image_list, lung_num):
    load = []
    for fname in image_list:
        if int(fname.split("_")[0]) == lung_num:
            load.append(fname)

    return load


cv2.namedWindow('Setting', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Setting', 600, 200)

current_list = load_list(image_list, 1)

cv2.createTrackbar('LUNG', 'Setting', 0, len(lung_list)-1, onChange)
cv2.createTrackbar('IMAGE', 'Setting', 0, len(current_list)-1, onChange)

cv2.createTrackbar('LOW', 'Setting', 0, 255, onChange)
cv2.createTrackbar('HIGH','Setting', 0, 255, onChange)
switch = "Gray-Jet"
cv2.createTrackbar(switch, 'Setting', 0, 1, onChange)

###
lung_num_buf = 0
img_num_buf = 0
img = cv2.imread(image_path + "/" + image_list[0], 1)
img_buf = img.copy()
mask = cv2.imread(mask_path + "/" + image_list[0], 0)
img = make_concat_img(img, mask)
cv2.setTrackbarPos('HIGH','Setting', 255)
low = cv2.getTrackbarPos('LOW', 'Setting') 
high = cv2.getTrackbarPos('HIGH', 'Setting') 
###

while True:
    setting_img = np.zeros((50, 512, 3), np.uint8)

    lung_num = cv2.getTrackbarPos('LUNG', 'Setting')
    img_num = cv2.getTrackbarPos('IMAGE', 'Setting')
    img = img_buf.copy()

    if lung_num_buf != lung_num:
        current_list = load_list(image_list, lung_list[lung_num])
        cv2.createTrackbar('IMAGE', 'Setting', 0, len(current_list)-1, onChange)

        img = cv2.imread(image_path + "/" + current_list[img_num], 1)
        mask = cv2.imread(mask_path + "/" + current_list[img_num], 0)
        img_buf = img.copy()

    if lung_num_buf != img_num:
        img = cv2.imread(image_path + "/" + current_list[img_num], 1)
        mask = cv2.imread(mask_path + "/" + current_list[img_num], 0)
        img_buf = img.copy()

    img = high_and_low(img, high, low)
    img = make_concat_img(img, mask)
    
    lung_num_buf = lung_num

    color_map = cv2.getTrackbarPos(switch, 'Setting') 

    if color_map == 1:
        img = cv2.applyColorMap(img, cv2.COLORMAP_JET)

    cv2.putText(setting_img, "Lung : " + str(lung_list[lung_num]), \
        (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
    cv2.putText(setting_img, "IMAGE : " + str(current_list[img_num]), \
        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
    
    img = cv2.vconcat([img, setting_img])
    cv2.imshow('image', img)

    low = cv2.getTrackbarPos('LOW', 'Setting') 
    high = cv2.getTrackbarPos('HIGH', 'Setting')
    k = cv2.waitKey(1) 

    if k == 27: 
        break 
    
cv2.destroyAllWindows()