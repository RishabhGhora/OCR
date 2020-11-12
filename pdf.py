import re
import cv2 
import pytesseract 
from pytesseract import Output

def get_pdf_text(img, pdf_choice):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    d = pytesseract.image_to_data(gray, output_type=Output.DICT)
    if pdf_choice == 'all text':
        text = ''
        for word in d['text']:
            text = text + word + ' '
        return text
    elif pdf_choice == 'dates':
        text = ''
        date_pattern = '^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/(19|20)|(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[012])-(19|20)\d\d$'
        n_boxes = len(d['text'])
        for i in range(n_boxes):
            if int(d['conf'][i]) > 60:
                if re.match(date_pattern, d['text'][i]):
                    text = text + d['text'][i] + ' '
        return text
    else:
        text = ''
        money_pattern = "^\$?\-?([1-9]{1}[0-9]{0,2}(\,\d{3})*(\.\d{0,2})?|[1-9]{1}\d{0,}(\.\d{0,2})?|0(\.\d{0,2})?|(\.\d{1,2}))$|^\-?\$?([1-9]{1}\d{0,2}(\,\d{3})*(\.\d{0,2})?|[1-9]{1}\d{0,}(\.\d{0,2})?|0(\.\d{0,2})?|(\.\d{1,2}))$|^\(\$?([1-9]{1}\d{0,2}(\,\d{3})*(\.\d{0,2})?|[1-9]{1}\d{0,}(\.\d{0,2})?|0(\.\d{0,2})?|(\.\d{1,2}))\)$"
        n_boxes = len(d['text'])
        for i in range(n_boxes):
            if int(d['conf'][i]) > 60:
                if re.match(money_pattern, d['text'][i]):
                    if '$' in d['text'][i]:
                        text = text + d['text'][i] + ' '
        return text