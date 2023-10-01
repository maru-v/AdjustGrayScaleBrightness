import os
import sys
import retinex
import cv2
import numpy as np
from matplotlib import pyplot as plt


def load_grayimg(file_path):
    img = cv2.imread(str(file_path))
    if len(img[0,0,:]) == 3:
        print("Convert color to grayscale.")
        grayimg = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        print("Unexpected number of channels in the image, terminate the process.")
        sys.exit(1)
    return grayimg


def extract_and_create_directory(image_path):
    file_name = os.path.splitext(os.path.basename(image_path))[0]
    save_directory = os.path.join("data", "save", file_name)

    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
        print(f"Created directory: {save_directory}")
    else:
        print(f"Directory already exists: {save_directory}")
    return save_directory


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)

    # set file path
    file_path = sys.argv[1]

    # prepare gray image
    grayimg = load_grayimg(file_path)

    # 1.equalizeHist : http://labs.eecs.tottori-u.ac.jp/sd/Member/oyamada/OpenCV/html/py_tutorials/py_imgproc/py_histograms/py_histogram_equalization/py_histogram_equalization.html
    equalizeimg = cv2.equalizeHist(grayimg)

    # 2.clahe : http://labs.eecs.tottori-u.ac.jp/sd/Member/oyamada/OpenCV/html/py_tutorials/py_imgproc/py_histograms/py_histogram_equalization/py_histogram_equalization.html
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    claheimg = clahe.apply(grayimg)

    # 3.retinex : https://github.com/aravindskrishnan/Retinex-Image-Enhancement, https://santhalakshminarayana.github.io/blog/retinex-image-enhancement
    variance_list = [15, 80, 250]
    variance = 250
    grayimg3ch = np.stack((grayimg,) * 3, -1)
    img_ssr = retinex.SSR(grayimg3ch, variance)
    img_msr = retinex.MSR(grayimg3ch, variance_list)

    # save result
    save_directory = extract_and_create_directory(file_path)
    cv2.imwrite(save_directory + "/grayimg.jpg", grayimg)
    cv2.imwrite(save_directory + "/equalizeimg.jpg", equalizeimg)
    cv2.imwrite(save_directory + "/claheimg.jpg", claheimg)
    cv2.imwrite(save_directory + "/img_ssr.jpg", img_ssr)
    cv2.imwrite(save_directory + "/img_msr.jpg", img_msr)

    # display
    titles = ["original", "equalize", "clahe", "ssr", "msr"]
    graphs = [grayimg, equalizeimg, claheimg, img_ssr, img_msr]
    graphs_diff = [
        np.abs(grayimg - grayimg),
        np.abs(grayimg - equalizeimg),
        np.abs(grayimg - claheimg),
        np.abs(grayimg3ch - img_ssr),
        np.abs(grayimg3ch - img_msr),
    ]
    fig, ax = plt.subplots(2, len(graphs))
    for i in range(len(graphs)):
        plt.subplot(2, len(graphs), i + 1)
        plt.title(titles[i], fontsize=10)
        plt.tick_params(color="white")
        plt.tick_params(
            labelbottom=False, labelleft=False, labelright=False, labeltop=False
        )
        plt.imshow(graphs[i], cmap="gray")
        plt.subplot(2, len(graphs), i + 1 + len(graphs))
        plt.tick_params(color="white")
        plt.tick_params(
            labelbottom=False, labelleft=False, labelright=False, labeltop=False
        )
        plt.title(titles[i] + "_diff", fontsize=10)
        plt.imshow(graphs_diff[i], cmap="gray")
    plt.savefig(save_directory + "/" +os.path.split(save_directory)[1] + "_result.jpg")
    plt.show()
