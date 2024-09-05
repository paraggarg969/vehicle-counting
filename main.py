from flask import Flask, request, jsonify, Response, render_template, send_from_directory
import cv2
from ultralytics import YOLO
import numpy as np
import math
import os
from sort_b import Sort  

app = Flask(__name__)


UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


model_path = 'best.pt'  
model = YOLO(model_path)


total_count_down = []


limit_down = [100, 650, 500, 650]


tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

@app.route('/')
def index():
    return render_template('vehicle.html')

@app.route('/set-line', methods=['POST'])
def set_line():
    global limit_down
    data = request.json
    x1, y1, x2, y2 = data.get('x1'), data.get('y1'), data.get('x2'), data.get('y2')
    limit_down = [x1, y1, x2, y2]
    print(limit_down)
    return jsonify({"message": "Line coordinates updated successfully"}), 200

@app.route('/upload-video', methods=['POST'])
def upload_video():
    global cap, width, height, ratiowidth, ratioheight
    if 'video' not in request.files:
        return jsonify({'success': False, 'message': 'No video part'}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        cap = cv2.VideoCapture(filepath)

        if cap.isOpened():
            # Get the width and height of the video frames
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"Width: {width}, Height: {height}")

        ratiowidth = width/640
        ratioheight = height/360

        print("ratiowidth : ",ratiowidth," ","ratioheight : ",ratioheight)

        # print(filepath)

        return jsonify({'success': True, 'video_url': '/uploads/' + file.filename}), 200

    return jsonify({'success': False, 'message': 'Unknown error'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def generate_video():
    global cap, limit_down
    print("p1",limit_down)
    # cap = cv2.VideoCapture('vehicle.mp4')  # Ensure the correct path
    # print(cap)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        for result in results:
            if result.boxes is not None:
                detections = np.empty((0, 5))

                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = math.ceil((box.conf[0].item() * 100)) / 100
                    cls = int(box.cls[0].item())
                    classname = result.names[cls]
                    if classname in ['car', 'motorcycle', 'truck']:  # Filter for vehicles
                        currentArray = np.array([x1, y1, x2, y2, conf])
                        detections = np.vstack((detections, currentArray))

                results_tracker = tracker.update(detections)
                # limit_down = (float(limit_down[0]), float(limit_down[1]), float(limit_down[2]), float(limit_down[3]))
                limit_down = (int(limit_down[0]), int(limit_down[1]), int(limit_down[2]), int(limit_down[3]))
                print(f"limit_down: {limit_down}")
                # cv2.line(frame, (limit_down[0]*ratiowidth, limit_down[1]*ratioheight), (limit_down[2]*ratiowidth, limit_down[3]*ratioheight), (255, 0, 255), 2)
                cv2.line(frame, (limit_down[0], limit_down[1]), (limit_down[2], limit_down[3]), (255, 0, 255), 2)

                for result in results_tracker:
                    x1, y1, x2, y2, id = map(int, result)
                    w, h = x2 - x1, y2 - y1
                    cx, cy = x1 + w // 2, y1 + h // 2
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f'{int(id)}', (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

                    if limit_down[1] < cy < limit_down[1] + 20:
                        if id not in total_count_down:
                            total_count_down.append(id)

                cv2.putText(frame, f'VEHICLE COUNT: {len(total_count_down)}', (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

        # Encode the frame in JPEG format
        ret, jpeg = cv2.imencode('.jpg', frame)
        # if not ret:
        #     break

        # Convert to byte array
        frame_bytes = jpeg.tobytes()

        # Yield the frame as a byte response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/video-feed')
def video_feed():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
