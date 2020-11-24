# Load the necessary modules 
import numpy as np
import cv2
import string
import nltk
from imutils.object_detection import non_max_suppression
import pytesseract
from pytesseract import Output
from matplotlib import pyplot as plt

# Global variables 
# Uncomment the line below on first use to
# Download a dictionary used in the postprocesssing stage 
# nltk.download('words')
english_vocab = set(w.lower() for w in nltk.corpus.words.words())
EAST = 'east/frozen_east_text_detection.pb'

def get_text(image, padding=0):
    """
    Gets the text from a natural scene image
    image: image inputed by the user 
    padding: padding to be applied on the bounding boxes
    output: returns detected text
    """
    #Saving a original image and shape
    orig = image.copy()
    (origH, origW) = image.shape[:2]

    # set the new height and width to default 320  
    (newW, newH) = (320, 320)

    #Calculate the ratio between original and new image for both height and weight. 
    #This ratio will be used to translate bounding box location on the original image. 
    rW = origW / float(newW)
    rH = origH / float(newH)

    # resize the original image to new dimensions
    image = cv2.resize(image, (newW, newH))
    (H, W) = image.shape[:2]
 
    # construct a blob from the image to forward pass it to EAST model
    blob = cv2.dnn.blobFromImage(image, 1.0, (H, W),
        (123.68, 116.78, 103.94), swapRB=True, crop=False)
    
    # load the pre-trained EAST model for text detection 
    net = cv2.dnn.readNet(EAST)

    # We would like to get two outputs from the EAST model. 
    #1. Probabilty scores for the region whether that contains text or not. 
    #2. Geometry of the text -- Coordinates of the bounding box detecting a text
    # The following two layer need to pulled from EAST model for achieving this. 
    layerNames = [
	    "feature_fusion/Conv_7/Sigmoid",
	    "feature_fusion/concat_3"]

    # Forward pass the blob from the image to get the desired output layers
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)

    # Find predictions and  apply non-maxima suppression
    (boxes, confidence_val) = predictions(scores, geometry)
    boxes = non_max_suppression(np.array(boxes), probs=confidence_val)

    # Text Detection and Recognition 
    # initialize the list of results
    results = []

    # loop over the bounding boxes to find the coordinate of bounding boxes
    for (startX, startY, endX, endY) in boxes:
        # scale the coordinates based on the respective ratios in order to reflect bounding box on the original image
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)
    
        #extract the region of interest
        r = orig[startY:endY+padding, startX:endX+padding]
    
        #configuration setting to convert image to string.  
        configuration = ("-l eng --oem 1 --psm 8")
    
        #This will recognize the text from the image of bounding box
        text = pytesseract.image_to_string(r, config=configuration)
        allowed = string.ascii_uppercase+string.ascii_lowercase+string.digits
        append_text = ''
        for letter in text:
            if letter in allowed:
                append_text = append_text + letter

        # append bbox coordinate and associated text to the list of results 
        results.append(((startX, startY, endX, endY), append_text))
    
    # Create list of words 
    output = ''
    for _, text in results:
        output = output + text + ' '
    #display_image(results, orig)
    return output
    

def predictions(prob_score, geo):
    """
    Gets the bounding boxes from the 
    East net output layers and returns it if 
    the probability score is more than the 
    0.5 minimum confidence level
    prob_score: probability score
    geo: geometry fron East
    boxes: 4 corners of bounding boxes as coordinates
    confidence_val: confidence levels 
    """
    (numR, numC) = prob_score.shape[2:4]
    boxes = []
    confidence_val = []

    # loop over rows
    for y in range(0, numR):
        scoresData = prob_score[0, 0, y]
        x0 = geo[0, 0, y]
        x1 = geo[0, 1, y]
        x2 = geo[0, 2, y]
        x3 = geo[0, 3, y]
        anglesData = geo[0, 4, y]

        # loop over the number of columns
        for i in range(0, numC):
            if scoresData[i] < 0.70:
                continue
            
            (offX, offY) = (i * 4.0, y * 4.0)

            # extracting the rotation angle for the prediction and computing the sine and cosine
            angle = anglesData[i]
            cos = np.cos(angle)
            sin = np.sin(angle)

            # using the geo volume to get the dimensions of the bounding box
            h = x0[i] + x2[i]
            w = x1[i] + x3[i]

            # compute start and end for the text pred bbox
            endX = int(offX + (cos * x1[i]) + (sin * x2[i]))
            endY = int(offY - (sin * x1[i]) + (cos * x2[i]))
            startX = int(endX - w)
            startY = int(endY - h)

            boxes.append((startX, startY, endX, endY))
            confidence_val.append(scoresData[i])
    # return bounding boxes and associated confidence_val
    return (boxes, confidence_val)

def display_image(results, orig):
    """
    Displays the results by drawing bounding boxes
    on top of original image and detected text
    results: coordinates for the bounding boxes
    and extracted text
    orig: copy of the original image
    """
    #Display the image with bounding box and recognized text
    orig_image = orig.copy()

    # Moving over the results and display on the image
    for ((start_X, start_Y, end_X, end_Y), text) in results:
        # display the text detected by Tesseract
        print("{}\n".format(text))

        # Displaying text
        text = "".join([x if ord(x) < 128 else "" for x in text]).strip()
        cv2.rectangle(orig_image, (start_X, start_Y), (end_X, end_Y),
            (0, 0, 255), 2)
        cv2.putText(orig_image, text, (start_X, start_Y - 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,0, 255), 2)

    plt.imshow(orig_image)
    plt.title('Output')
    plt.show()

def get_ns_text(image):
    """
    Gets text from a natural scene image by applying 2 
    filters, blur and Otsu threshold with padding and 
    no padding and returns the best scoring text
    image: image inputed by the user 
    text: returns detected text
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    blur_image = cv2.cvtColor(blur, cv2.COLOR_GRAY2RGB)
    blur_text_no_padding = get_text(blur_image)
    blur_text_padding = get_text(blur_image, 5)
    if get_score(blur_text_padding) > get_score(blur_text_no_padding):
        blur_text = blur_text_padding
    else:
        blur_text = blur_text_no_padding
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    thresh_image = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
    thresh_text_no_padding = get_text(thresh_image)
    thresh_text_padding = get_text(thresh_image, 5)
    if get_score(thresh_text_padding) >= get_score(thresh_text_no_padding) and get_score(thresh_text_padding) != 1:
        thresh_text = thresh_text_padding
    else:
        thresh_text = thresh_text_no_padding

    #print('blur text: {}'.format(blur_text))
    #print('blur text score: {}'.format(get_score(blur_text)))
    #print('thresh text: {}'.format(thresh_text))
    #print('thresh text score: {}'.format(get_score(thresh_text)))

    if get_score(blur_text) > get_score(thresh_text):
        return blur_text
    else:
        return thresh_text

def get_score(text):
    """
    Calculate a score of the text by getting how many 
    words in the text are english words divided by the 
    total number of words
    text: text to be evaluated
    percent: calculated score is returned 
    """
    words = text.split()
    en_count = 0.0
    for word in words:
        if hasNumbers(word):
            break
        word = word.lower()
        if word in english_vocab or (word[len(word)-1] == 's' and word[0:len(word)-1] in english_vocab):
            en_count += 1

    percent = en_count/len(words) if len(words) != 0 else 0
    return percent

def hasNumbers(inputString):
    """
    Helper function that checks if input string 
    has any numbers 
    inputString: string to be evaluated
    boolean: returns True or False
    """
    return any(char.isdigit() for char in inputString)