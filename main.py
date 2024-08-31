import cv2
from ultralytics import YOLO
import numpy as np
import math
from sort_b import Sort  # Ensure you have the SORT tracker implemented or imported

# Load the YOLOv8 model
model_path = '/Users/anuragcse/Downloads/results/weights/best.pt'  # Update with your path
model = YOLO(model_path)

# Video capture
cap = cv2.VideoCapture("/Users/anuragcse/Downloads/a.mp4")

# Initialize counting lists
total_count_down = []

# Define the lines for counting
limit_down = [200, 650, 600, 650]

# Initialize the tracker
tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)
    for result in results:
        # Check if there are any detections (boxes)
        if result.boxes is not None:
            detections = np.empty((0, 5))

            # Iterate over each detected box
            for box in result.boxes:
                x1,y1,x2,y2 = map(int,box.xyxy[0])
                conf = math.ceil((box.conf[0].item()*100))/100
                cls = int(box.cls[0].item())
                classname = result.names[cls]
                if classname in ['car', 'motorcycle', 'truck']:  # Filter for vehicles
                    currentArray = np.array([x1, y1, x2, y2, conf])
                    detections = np.vstack((detections, currentArray))

            results_tracker = tracker.update(detections)
            cv2.line(frame, (limit_down[0], limit_down[1]), (limit_down[2], limit_down[3]), (255, 0, 0), 5)

            for z in results_tracker:
                x1, y1, x2, y2, obj_id = map(int, z)
                cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
                cv2.circle(frame, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (85, 45, 255), 3)
                label = f'{int(obj_id)}'

                if limit_down[0] < cx < limit_down[2] and limit_down[1] - 15 < cy < limit_down[3] + 15:
                    if obj_id not in total_count_down:
                        total_count_down.append(obj_id)
                        cv2.line(frame, (limit_down[0], limit_down[1]), (limit_down[2], limit_down[3]), (0, 255, 0), 5)
            cv2.putText(frame, f'Vehicles Entering: {len(total_count_down)}', (300, 91), cv2.FONT_HERSHEY_PLAIN, 3,(255, 0, 0), 5)

    cv2.imshow("vid",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()