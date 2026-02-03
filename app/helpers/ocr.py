import cv2
import requests
import json
from typing import Dict, Any, Optional
import numpy as np
from io import BytesIO

class ImageReader:
    def __init__(self, base_url: str = "http://127.0.0.1:8080"):
        self.base_url = base_url
    
    def read_image(self, image_path: str, target_rect) -> Dict[str, Any]:
        # Read and crop the image
        big_image = cv2.imread(image_path)
        if big_image is None:
            raise ValueError(f"Could not read image from {image_path}")
        
        x1, y1, x2, y2 = target_rect
        cropped_image = big_image[y1:y2, x1:x2]
        
        # Prepare the multipart request
        files = {'file': self._image_to_bytes(cropped_image)}
        
        try:
            # Send POST request
            response = requests.post(
                f"{self.base_url}/ocr/upload",
                files=files
            )
            response.raise_for_status()  # Raise exception for bad status codes
            json_resp = response.json()
            text = "  \n".join(json_resp[0]["rec_texts"])
            # Parse and return JSON response
            return text
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to OCR service: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from server: {e}")
    
    def _image_to_bytes(self, image: np.ndarray) -> tuple:
        """Convert OpenCV image to bytes for multipart upload"""
        # Convert BGR to RGB if needed (depending on your OCR service requirements)
        # rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Encode image to bytes
        success, encoded_image = cv2.imencode('.jpg', image)
        if not success:
            raise ValueError("Failed to encode image to bytes")
        
        image_bytes = BytesIO(encoded_image.tobytes())
        
        # Return tuple for requests' files parameter
        # Format: (filename, file_object, content_type, headers)
        return ('image.jpg', image_bytes, 'image/jpeg')
    
    # Alternative method if you need to send additional data
    def read_image_with_params(self, image_path: str, target_rect, 
                              additional_params: Optional[Dict] = None) -> Dict[str, Any]:
        # Read and crop the image
        big_image = cv2.imread(image_path)
        if big_image is None:
            raise ValueError(f"Could not read image from {image_path}")
        
        x1, y1, x2, y2 = target_rect
        cropped_image = big_image[y1:y2, x1:x2]
        
        # Prepare files and data
        files = {'file': self._image_to_bytes(cropped_image)}
        data = additional_params or {}
        
        try:
            # Send POST request with both files and data
            response = requests.post(
                f"{self.base_url}/ocr/upload",
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to OCR service: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from server: {e}")
