# Load the necessary modules 
import cv2
import pytesseract
from pytesseract import Output
import string
import numpy as np
import nltk
from ns import get_ns_text
from island import isolateText

# Uncomment the line below on first use to
# Download a dictionary used in the postprocesssing stage 
# nltk.download('words')
english_vocab = set(w.lower() for w in nltk.corpus.words.words())


def preprocessing(img, thresh_value):
    """
    Preprocesses the input image by converting to 
    grayscale, applying a threshold, bluring the image
    and then applying Otsu's threshold
    img: image inputed by the user 
    thresh_value: value of thresholding to be applied 
    thresh: filtered image is returned
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = ((gray/255)**thresh_value * 255).astype(np.uint8)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    return thresh

def get_cgt_text(img, thresh_value):
    """
    Extracts text from an image by filtering the 
    image then running the image through pytesseract
    and cleaning the text outputted  
    img: image inputed by the user 
    thresh_value_ value of thresholding to be applied 
    data: extracted text is returned
    """
    thresh = preprocessing(img, thresh_value)
    data = pytesseract.image_to_string(thresh, lang='eng', config='--psm 6')
    allowed = string.ascii_uppercase+string.ascii_lowercase + """?'."!"""
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


def get_pdf_text(img):
    """
    Extracts text from an image without 
    using any filters with regular 
    pytesseract method
    img: image inputed by the user 
    text: extracted text is returned
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    d = pytesseract.image_to_data(gray, output_type=Output.DICT)
    text = ''
    for word in d['text']:
        text = text + word + ' '
    return text

def get_island_text(img):
    """
    Extracts text from an image by filtering
    with our island filter, running through pytesseract
    and cleaning the text outputted  
    img: image inputed by the user 
    data: extracted text is returned 
    """
    island_img = isolateText(img)
    data = pytesseract.image_to_string(island_img, lang='eng', config='--psm 6')
    allowed = string.ascii_uppercase+string.ascii_lowercase + """?'."!"""
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

def get_score(text):
    """
    Calculate a score of the text by getting how many 
    words in the text are english words divided by the 
    total number of words
    text: text to be evaluated
    percent: calculated score is returned 
    under_limit_word: number of words under 2 characters
    """
    words = text.split()
    en_count = 0.0
    under_limit_word = 0
    i = 0
    for word in words:
        if i > 20:
            break
        if hasNumbers(word):
            i = i + 1
            continue
        word = word.lower()
        if word in english_vocab:
            en_count += 1
        if len(word) <= 2:
            under_limit_word += 1
        i = i + 1

    percent = en_count/i if i > 0 else 0
    return percent, under_limit_word

def hasNumbers(inputString):
    """
    Helper function that checks if input string 
    has any numbers 
    inputString: string to be evaluated
    boolean: returns True or False
    """
    return any(char.isdigit() for char in inputString)
    
def get_text(img):
    """
    Method that takes an input image and 
    applies 3 different filters on it, 
    extracts the text with pytesseract, 
    and returns the text with the best score. 
    img: image inputed by the user 
    text: returns best scoring text
    """
    cgt_text_20 = get_cgt_text(img, 20)
    cgt_text_100 = get_cgt_text(img, 100)
    pdf_text = get_pdf_text(img)
    island_text = get_island_text(img)
    cgt_text_20_score,x = get_score(cgt_text_20)
    cgt_text_100_score,y = get_score(cgt_text_100)
    pdf_text_score,z = get_score(pdf_text)
    island_text_score, i = get_score(island_text)

    #print('cgt_text_20: {} \n score: {} \n under limit words: {} \n len: {}'.format(cgt_text_20, cgt_text_20_score,x, len(cgt_text_20)))
    #print('cgt_text_100: {} \n score: {} \n under limit words: {}\n len: {}'.format(cgt_text_100, cgt_text_100_score,y, len(cgt_text_100)))
    #print('pdf_text: {} \n score: {} \n under limit words: {}'.format(pdf_text, pdf_text_score,z))
    #print('island_text: {} \n score: {} \n under limit words: {}'.format(island_text, island_text_score,i))

    if island_text_score >= cgt_text_20_score and island_text_score >= cgt_text_100_score and island_text_score >= pdf_text_score and island_text_score != 0:
        return island_text

    if cgt_text_20_score == cgt_text_100_score == 0 or (pdf_text_score < 0.3 and cgt_text_100_score < 0.3):
        ns_text = get_ns_text(img)
        return ns_text

    if cgt_text_20_score >= cgt_text_100_score and cgt_text_20_score > pdf_text_score and x < z:
        return cgt_text_20
    elif cgt_text_100_score > cgt_text_20_score and cgt_text_100_score > pdf_text_score:
        return cgt_text_100
    elif pdf_text_score > cgt_text_100_score and pdf_text_score > cgt_text_20_score and len(pdf_text) >= len(cgt_text_20):
        return pdf_text
    elif cgt_text_20_score > pdf_text_score and x > z and len(pdf_text) >= len(cgt_text_20):
        return pdf_text
    else:
        return cgt_text_20

