# OCR
OCR text extraction for complex images

This project attempts to extract text from Images using Object Character Recognition. Additionally, it attemps to flag images as appropriate or inappropriate given the text extracted from the image. This was a project for CS 6220 Big Data Systems and Analytics.

To run the project please clone the repository and run python app.py. This will pull up our website on the given local host and allow the user to upload an image and download the extracted text as a txt file. Note you will first need to have all the required modules downloaded first to run this.

CAUTION: Some of the images in test_images may be offensive as we are trying to identify such offensive images. These test images consist of images from the Facebook competition dataset available here: https://www.drivendata.org/competitions/64/hateful-memes/page/206/. Images also include screenshots from twitter, images posted on subreddits, and images in natural settings. Some of the natural setting images include car licesnse plates from the Kaggle dataset available here: https://www.kaggle.com/andrewmvd/car-plate-detection.

This project aims to improve the performance of pytesseract: https://pypi.org/project/pytesseract/ in terms of being able to accurately extract text from computer generated images. Pytesseract is an optical character recognition (OCR) tool for python to extract text from images. We used pytesseract in about 4 lines of our project code and did not attempt to alter its process but instead apply computer vision and text correction techniques to improve its performance.

Although our project does have an implementation of natural scene image text extraction as well, we did not want to focus on this as there is already a Google Vision API that can handle this well but is not free for developers. We improved upon the accuracy of tesserect in terms of extracting text correctly from complicated images, which we considered images not in a pdf style or black text on white background, using the code in OCR.py and island.py. Additionally, we have showcased a way to use our method to flag inappropriate images in real time on a subreddit showcased here: https://www.youtube.com/watch?v=wtqyZCahSIQ&feature=emb_title&ab_channel=RishabhGhora.
