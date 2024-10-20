from fastapi import FastAPI, BackgroundTasks, Request
from scraper import fetch_traffic_cameras, fetch_camera_images, download_image
from prediction import predict_vehicles
import threading
import time
from typing import Dict
import uvicorn
from utils.logger import setup_logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import datetime

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize the logger
logger = setup_logger(__name__)

# Global vehicle count storage
vehicle_counts_per_location: Dict[str, Dict[str, int]] = {}
# Lock for thread safety
lock = threading.Lock()

# Data retention and storage settings
retention_time = 30 * 60  # 30 minutes in seconds

def run_scraper(base_url: str, interval: int = 30):
    """
    Run the scraper periodically and update vehicle counts.
    
    :param base_url: Base URL for the traffic cameras.
    :param interval: Time interval for scraping.
    """
    global vehicle_counts_per_location

    start_time = time.time()

    while True:
        try:
            camera_ids = fetch_traffic_cameras(base_url)
            for camera_id in camera_ids:
                location = 'woodlands' if camera_id in ('wtc', 'wtc1') else camera_id
                image_urls = fetch_camera_images(camera_id, base_url)
                
                for img_url in image_urls:
                    image_path = download_image(img_url, location)
                    if image_path:
                        vehicle_counts = predict_vehicles(image_path)
                        
                        with lock:
                            if location not in vehicle_counts_per_location:
                                vehicle_counts_per_location[location] = vehicle_counts
                            else:
                                for vehicle_type, count in vehicle_counts.items():
                                    vehicle_counts_per_location[location][vehicle_type] += count

        except Exception as e:
            logger.error(f"Error in scraper loop: {e}")
        
        # Check if it's time to archive the data
        if time.time() - start_time >= retention_time:
            archive_vehicle_counts()
            vehicle_counts_per_location.clear()
            start_time = time.time()

        time.sleep(interval)

def archive_vehicle_counts():
    """
    Archive vehicle counts into a results folder with a unique timestamp.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    results_folder = "results"
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
    
    filepath = os.path.join(results_folder, f"vehicle_counts_{timestamp}.txt")
    
    with open(filepath, "w") as f:
        for location, counts in vehicle_counts_per_location.items():
            f.write(f"{location}: {counts}\n")
    
    logger.info(f"Data archived at {filepath}")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    response = HTMLResponse(content=open("static/index.html", "r").read(), status_code=200)
    return response

@app.get("/vehicle-counts/")
def get_vehicle_counts():
    global vehicle_counts_per_location

    with lock:
        return vehicle_counts_per_location

@app.on_event("startup")
async def start_scraper_on_startup():
    """
    Automatically start the scraper when the app starts.
    """
    base_url = "https://onemotoring.lta.gov.sg/content/onemotoring/home/driving/traffic_information/traffic-cameras"
    threading.Thread(target=run_scraper, args=(base_url,), daemon=True).start()

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")
