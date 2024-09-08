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


limit_down = [499, 642, 137, 632]

# Variables to store separate coordinates
left_line = [0,0,0,0]
right_line = [0,0,0,0]
top_line = [0,0,0,0]
bottom_line = [0,0,0,0]

tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

@app.route('/')
def index():
    return render_template('vehicle.html')

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


@app.route('/set-line', methods=['POST'])
def set_line():
    global limit_down, left_line, right_line, top_line, bottom_line, width, height
    data = request.json
    x1, y1, x2, y2 = data.get('x1'), data.get('y1'), data.get('x2'), data.get('y2')
    limit_down = [x1, y1, x2, y2]
    print(limit_down)

    # Calculate the center of the video
    video_center_x = width // 2
    video_center_y = height // 2

    print("video_center_x ",video_center_x," ","video_center_y ",video_center_y)
    
    # Classify and store coordinates based on their relation to the center
    if x1 < video_center_x and x2 < video_center_x and y1>y2:
        left_line = [x1*ratiowidth, y1*ratioheight, x2*ratiowidth, y2*ratioheight]
    elif x1 > video_center_x and x2 > video_center_x and y1>y2:
        right_line = [x1*ratiowidth, y1*ratioheight, x2*ratiowidth, y2*ratioheight]
    
    if y1 < video_center_y and y2 < video_center_y and x2>x1:
        bottom_line = [x1*ratiowidth, y1*ratioheight, x2*ratiowidth, y2*ratioheight]
    elif y1 > video_center_y and y2 > video_center_y and x2>x1:
        top_line = [x1*ratiowidth, y1*ratioheight, x2*ratiowidth, y2*ratioheight]

    print(f"Left Line: {left_line}, Right Line: {right_line}, Top Line: {top_line}, Bottom Line: {bottom_line}")
    
    return jsonify({"message": "Line coordinates updated successfully"}), 200



def generate_video():
    global cap, limit_down, left_line, right_line, top_line, bottom_line
    print("p1",limit_down)
    print("p1",left_line)
    print("p1",right_line)
    print("p1",top_line)
    print("p1",bottom_line)
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
                left_line = (int(left_line[0]), int(left_line[1]), int(left_line[2]), int(left_line[3]))
                right_line = (int(right_line[0]), int(right_line[1]), int(right_line[2]), int(right_line[3]))
                top_line = (int(top_line[0]), int(top_line[1]), int(top_line[2]), int(top_line[3]))
                bottom_line = (int(bottom_line[0]), int(bottom_line[1]), int(bottom_line[2]), int(bottom_line[3]))

                 # Draw the lines (left, right, top, and bottom)
                if left_line:
                    cv2.line(frame, (left_line[0], left_line[1]), (left_line[2], left_line[3]), (255, 0, 0), 2)
                if right_line:
                    cv2.line(frame, (right_line[0], right_line[1]), (right_line[2], right_line[3]), (255, 0, 0), 2)
                if top_line:
                    cv2.line(frame, (top_line[0], top_line[1]), (top_line[2], top_line[3]), (255, 0, 0), 2)
                if bottom_line:
                    cv2.line(frame, (bottom_line[0], bottom_line[1]), (bottom_line[2], bottom_line[3]), (255, 0, 0), 2)

                print(f"limit_down: {limit_down}")
                print(f"left_line: {left_line}")
                print(f"right_line: {right_line}")
                print(f"top_line: {top_line}")
                print(f"bottom_line: {bottom_line}")
                # # cv2.line(frame, (limit_down[0]*ratiowidth, limit_down[1]*ratioheight), (limit_down[2]*ratiowidth, limit_down[3]*ratioheight), (255, 0, 255), 2)
                # cv2.line(frame, (limit_down[0], limit_down[1]), (limit_down[2], limit_down[3]), (255, 0, 255), 2)

                for result in results_tracker:
                    x1, y1, x2, y2, id = map(int, result)
                    cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
                    cv2.circle(frame,(cx,cy),5,(255,0,255),cv2.FILLED)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    #cv2.putText(frame, f'{int(id)}', (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

                    if limit_down[0] < cx < limit_down[2] and limit_down[1] -15 < cy < limit_down[3] + 15 :
                    #if limit_down[1] - 15 < cy < limit_down[3] + 15:
                        if id not in total_count_down:
                            total_count_down.append(id)
                            cv2.line(frame, (limit_down[0], limit_down[1]), (limit_down[2], limit_down[3]), (0, 255, 0),5)

                cv2.putText(frame, f'VEHICLE COUNT: {len(total_count_down)}', (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

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
