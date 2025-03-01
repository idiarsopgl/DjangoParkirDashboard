import cv2
import numpy as np
from PIL import Image
import pytesseract
from pathlib import Path
import re

class ANPR:
    def __init__(self):
        # Initialize path for Tesseract executable (Windows)
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if Path(tesseract_path).exists():
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def preprocess_image(self, image):
        # Make a copy of the image
        img_copy = image.copy()
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter to remove noise while keeping edges sharp
        bilateral = cv2.bilateralFilter(gray, 11, 17, 17)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(bilateral, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY_INV, 19, 9)
        
        # Find contours in the thresholded image
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort contours by area, largest first
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]
        
        # List to store potential license plate regions
        plate_candidates = []
        
        # Loop through contours to find license plate
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            
            # Check if it's a rectangle (4 points) and has the right aspect ratio
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h
                
                # License plates usually have an aspect ratio of 2:1 to 4:1
                if 1.5 <= aspect_ratio <= 5.0 and w > 100 and h > 30:
                    # Extract the region
                    plate_region = gray[y:y+h, x:x+w]
                    plate_candidates.append(plate_region)
        
        # If we found candidates, return the largest one
        if plate_candidates:
            # Return the largest plate candidate
            return plate_candidates[0]
        
        # If no plate was detected using contour method, return the entire grayscale image
        return gray

    def enhance_plate_image(self, plate_image):
        if plate_image is None:
            return None
            
        # Resize image for better OCR - make it larger
        plate_image = cv2.resize(plate_image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        
        # Apply multiple preprocessing techniques and combine results for better accuracy
        
        # 1. Standard binary thresholding
        _, binary_thresh = cv2.threshold(plate_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 2. Adaptive thresholding
        adaptive_thresh = cv2.adaptiveThreshold(plate_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                               cv2.THRESH_BINARY, 11, 2)
        
        # 3. Use morphological operations to clean up the image
        kernel = np.ones((3, 3), np.uint8)
        morph_img = cv2.morphologyEx(binary_thresh, cv2.MORPH_CLOSE, kernel)
        morph_img = cv2.morphologyEx(morph_img, cv2.MORPH_OPEN, kernel)
        
        # Return the enhanced image
        return morph_img

    def detect_plate(self, image_path):
        try:
            # Read image
            if isinstance(image_path, str):
                image = cv2.imread(image_path)
            else:
                # Convert PIL Image to OpenCV format
                image = cv2.cvtColor(np.array(image_path), cv2.COLOR_RGB2BGR)
            
            if image is None:
                raise ValueError("Could not read image")
            
            # Preprocess image
            plate_image = self.preprocess_image(image)
            if plate_image is None:
                return None
                
            # Enhance plate image
            enhanced_plate = self.enhance_plate_image(plate_image)
            if enhanced_plate is None:
                return None
            
            # Try different PSM modes for better accuracy
            text_results = []
            
            # PSM 7 - Treat the image as a single text line
            text1 = pytesseract.image_to_string(enhanced_plate, config='--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            text_results.append(text1)
            
            # PSM 8 - Treat the image as a single word
            text2 = pytesseract.image_to_string(enhanced_plate, config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            text_results.append(text2)
            
            # PSM 13 - Raw line
            text3 = pytesseract.image_to_string(enhanced_plate, config='--psm 13 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            text_results.append(text3)
            
            # Post-process each result
            processed_results = []
            for text in text_results:
                # Clean up the text - keep only alphanumeric
                clean_text = ''.join(c for c in text if c.isalnum())
                if clean_text:
                    processed_results.append(clean_text)
            
            # Try to find a result that looks like an Indonesian license plate
            for result in processed_results:
                # Indonesian license plates often follow patterns like "B 1234 XYZ"
                if re.search(r'[A-Z][0-9]{1,4}[A-Z]{1,3}', result):
                    return result
            
            # If no pattern matched, return the longest result if available
            if processed_results:
                return max(processed_results, key=len)
            
            return None
            
        except Exception as e:
            print(f"Error in plate detection: {str(e)}")
            return None

    def compare_images(self, image1_path, image2_path, method=cv2.HISTCMP_CORREL):
        try:
            # Read images
            img1 = cv2.imread(image1_path)
            img2 = cv2.imread(image2_path)
            
            if img1 is None or img2 is None:
                raise ValueError("Could not read one or both images")
            
            # Convert images to the same size
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Convert to HSV color space
            hsv1 = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
            hsv2 = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)
            
            # Calculate histograms
            hist1 = cv2.calcHist([hsv1], [0, 1], None, [180, 256], [0, 180, 0, 256])
            hist2 = cv2.calcHist([hsv2], [0, 1], None, [180, 256], [0, 180, 0, 256])
            
            # Normalize histograms
            cv2.normalize(hist1, hist1, 0, 1, cv2.NORM_MINMAX)
            cv2.normalize(hist2, hist2, 0, 1, cv2.NORM_MINMAX)
            
            # Compare histograms
            similarity = cv2.compareHist(hist1, hist2, method)
            
            return similarity
            
        except Exception as e:
            print(f"Error in image comparison: {str(e)}")
            return 0.0
