import cv2
import numpy as np
from PIL import Image
import subprocess

# Load image
img = cv2.imread("impokc.jpg", cv2.IMREAD_GRAYSCALE)
_, thresh = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY_INV)

# Save temporary bitmap
bitmap_path = "outline.bmp"
cv2.imwrite(bitmap_path, thresh)

# Use potrace to convert BMP to SVG
subprocess.run(["potrace", bitmap_path, "-s", "-o", "outline.svg"])

