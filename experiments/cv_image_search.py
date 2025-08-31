import cv2
import numpy as np


def find_template_multiscale(large_image_path, template_path, 
                             scale_range=(0.5, 2.0), scale_steps=20):
    """
    Find template at different scales for better matching
    """
    large_img = cv2.imread(large_image_path)
    template = cv2.imread(template_path)
    
    if large_img is None or template is None:
        raise ValueError("Could not load images")
    
    best_match = None
    best_val = -1
    
    # Test different scales
    scales = np.linspace(scale_range[0], scale_range[1], scale_steps)
    
    for scale in scales:
        # Resize template
        resized_template = cv2.resize(template, None, fx=scale, fy=scale)
        
        # Skip if template is larger than image
        if (resized_template.shape[0] > large_img.shape[0] or 
            resized_template.shape[1] > large_img.shape[1]):
            continue
        
        # Perform template matching
        result = cv2.matchTemplate(large_img, resized_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Update best match if better
        if max_val > best_val:
            best_val = max_val
            h, w = resized_template.shape[:2]
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            best_match = (top_left, bottom_right, best_val, scale)
    
    return best_match


# Usage
result = find_template_multiscale('haystack.png', 'needle.png')
if result:
    top_left, bottom_right, confidence, scale = result
    print(f"Best match at scale {scale:.2f} with confidence {confidence:.4f} at {top_left},{bottom_right}")