from PIL import Image
import numpy as np
from scipy.signal import correlate2d


def find_template_pillow(large_image_path, template_path):
    """
    Alternative approach using Pillow and scipy
    """
    # Load images
    large_img = Image.open(large_image_path).convert('L')  # Grayscale
    template = Image.open(template_path).convert('L')
    
    # Convert to numpy arrays
    large_array = np.array(large_img, dtype=np.float32)
    template_array = np.array(template, dtype=np.float32)
    
    # Normalize arrays
    large_array = (large_array - np.mean(large_array)) / np.std(large_array)
    template_array = (template_array - np.mean(template_array)) / np.std(template_array)
    
    # Perform correlation
    correlation = correlate2d(large_array, template_array, mode='valid')
    
    # Find maximum correlation
    max_idx = np.unravel_index(np.argmax(correlation), correlation.shape)
    
    top_left = (max_idx[1], max_idx[0])
    h, w = template_array.shape
    bottom_right = (top_left[0] + w, top_left[1] + h)
    confidence = correlation[max_idx]
    
    return top_left, bottom_right, confidence


# Usage
result = find_template_pillow('haystack.png', 'needle.png')
if result:
    top_left, bottom_right, confidence = result
    print(f"Best match with confidence {confidence:.4f} at {top_left},{bottom_right}")