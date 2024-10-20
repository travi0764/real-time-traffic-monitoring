import os
import requests
from bs4 import BeautifulSoup
from typing import List
from utils.logger import setup_logger

# Initialize the logger
logger = setup_logger(__name__)

def fetch_traffic_cameras(url: str) -> List[str]:
    """
    Fetch the IDs of the traffic cameras from the main page.
    
    :param url: URL of the traffic cameras page.
    :return: List of camera IDs.
    """
    try:
        response = requests.get(url + ".html")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        buttons = soup.find_all('button', class_='btn btn-primary')
        return [button['id'] for button in buttons if buttons]
    except Exception as e:
        logger.error(f"Failed to fetch traffic cameras from {url}: {e}")
        return []

def fetch_camera_images(camera_id: str, base_url: str) -> List[str]:
    """
    Fetch image URLs for a specific traffic camera.
    
    :param camera_id: ID of the traffic camera.
    :param base_url: Base URL for constructing image URLs.
    :return: List of image URLs.
    """
    try:
        camera_image_url = f"{base_url}/{camera_id}.html#trafficCameras"
        response = requests.get(camera_image_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img')
        
        image_urls = []
        for img in images:
            img_src = img.get('src')
            if img_src and 'View from' in img.get('alt', ''):
                img_src = f"http:{img_src}" if img_src.startswith('//') else img_src
                image_urls.append(img_src)
        
        return image_urls
    except Exception as e:
        logger.error(f"Failed to fetch images for {camera_id}: {e}")
        return []

def download_image(image_url: str, location: str) -> str:
    """
    Download an image and save it to the specified location folder.
    
    :param image_url: URL of the image to download.
    :param location: Directory where the image will be saved.
    :return: Path of the saved image.
    """
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        
        location_dir = os.path.join('traffic_images', location)
        if not os.path.exists(location_dir):
            os.makedirs(location_dir)

        img_filename = os.path.join(location_dir, image_url.split('/')[-1])
        with open(img_filename, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Image saved: {img_filename}")
        return img_filename
    except Exception as e:
        logger.error(f"Failed to download image {image_url}: {e}")
        return ""
