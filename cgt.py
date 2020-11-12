import cv2
import pytesseract
import string
import numpy as np
from matplotlib import pyplot as plt

def preprocessing(img):
    # Grayscale, Gaussian blur, Otsu's threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = ((gray/255)**20 * 255).astype(np.uint8)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    return thresh

def get_cgt_text(img):
    thresh = preprocessing(img)
    data = pytesseract.image_to_string(thresh, lang='eng', config='--psm 6')
    allowed = string.ascii_uppercase+string.ascii_lowercase + " ?"
    lines = data.split("\n")
    res = []
    for line in lines:
        t = []
        correct = 0
        for i in line:
            if i in allowed:
                t.append(i)
                correct+=1
            elif i in "1234567890":
                t.append(i)
            elif len(t) > 0 and t[-1] != " ":
                t.append(" ")
        if correct > len(line)*3/5 and correct > 2:
            res.append("".join(t))
    data = "\n".join(res)
    return data