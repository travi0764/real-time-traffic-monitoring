from ultralytics import YOLO
from typing import Dict
from utils.logger import setup_logger

# Initialize the logger
logger = setup_logger(__name__)

# Load YOLO model
model = YOLO("yolov8s.pt")

def predict_vehicles(image_path: str) -> Dict[str, int]:
    """
    Predict the number of cars, buses, trucks, and motorcycles in an image.
    
    :param image_path: Path of the image to predict on.
    :return: Dictionary containing vehicle counts.
    """
    try:
        results = model(image_path, verbose = False)
        
        vehicles = ['car', 'bus', 'truck', 'motorcycle']
        vehicle_counts = {v: 0 for v in vehicles}
        
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = model.names[class_id]

                if class_name in vehicles:
                    vehicle_counts[class_name] += 1

        
        logger.info(f"Predictions for {image_path}: {vehicle_counts}")
        return vehicle_counts
    except Exception as e:
        logger.error(f"Failed to predict vehicles for {image_path}: {e}")
        return {}
