import base64
import cv2
import numpy as np

def encode_image(image_data):
    """Encodes image data to base64."""
    return base64.b64encode(image_data).decode('utf-8')

def enhance_image(image_data):
    """Enhances image clarity."""
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    alpha = 1.5
    beta = 45
    contrast_img = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
    blurred = cv2.GaussianBlur(contrast_img, (5, 5), 0)
    enhanced_image = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 7)
    kernel = np.array([[0, -1, 0], [-1, 7, -1], [0, -1, 0]])
    enhanced_image = cv2.filter2D(enhanced_image, -1, kernel)
    kernel = np.ones((1, 1), np.uint8)
    enhanced_image = cv2.dilate(enhanced_image, kernel, iterations=1)
    enhanced_image = cv2.erode(enhanced_image, kernel, iterations=1)
    _, encoded_image = cv2.imencode('.jpg', enhanced_image)
    return encoded_image.tobytes()