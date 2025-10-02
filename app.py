# ─────────────────────────────────────────────────────────────
# Flask App — Sign Language Detection via YOLOv11
# ─────────────────────────────────────────────────────────────

import os
import sys
import cv2
from flask                                import Flask, request, jsonify, render_template, Response
from flask_cors                           import CORS, cross_origin
from ultralytics                          import YOLO

from sign_lang.pipeline.training_pipeline import TrainPipeline
from sign_lang.utils.main_utils           import decodeImage, encodeImageIntoBase64
from sign_lang.constant.application       import APP_HOST, APP_PORT

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────────────────
# ClientApp — Holds input image filename
# ─────────────────────────────────────────────────────────
class ClientApp:
    def __init__(self):
        self.filename = "inputImage.jpg"

clApp = ClientApp()

# ─────────────────────────────────────────────────────────
# Route: Trigger Training Pipeline
# ─────────────────────────────────────────────────────────
@app.route("/train")
def trainRoute():
    pipeline = TrainPipeline()
    pipeline.run_pipeline()
    return "Training Successful!!"

# ─────────────────────────────────────────────────────────
# Route: Home Page — Serves Frontend UI
# ─────────────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")

# ─────────────────────────────────────────────────────────
# Route: Predict from Uploaded Image
# ─────────────────────────────────────────────────────────
@app.route("/predict", methods=['POST', 'GET'])
@cross_origin()
def predictRoute():
    try:
        image           = request.json['image']
        decodeImage(image, clApp.filename)

        # Load trained YOLOv11 model
        model_path      = os.path.join("artifacts", "model_trainer", "best.pt")

        if not os.path.exists(model_path):
            return Response(f"Model file not found at {model_path}", status=404)
        
        model           = YOLO(model_path)
        
        # Run inference on uploaded image
        results = model.predict(source=os.path.join("data", clApp.filename), save=True)

        # Encode prediction result
        output_path     = os.path.join("runs", "detect", "predict", clApp.filename)
        opencodedbase64 = encodeImageIntoBase64(output_path)
        result = {"image": opencodedbase64.decode('utf-8')}

        # Cleanup
        os.system("rm -rf runs")

    except ValueError as val:
        print(val)
        return Response("Value not found inside JSON data")
    except KeyError:
        return Response("Incorrect key passed in JSON")
    except Exception as e:
        print(e)
        return Response("Invalid input")

    return jsonify(result)

# ─────────────────────────────────────────────────────────
# Route: Live Camera Detection
# ─────────────────────────────────────────────────────────
# @app.route("/live", methods=['GET'])
# @cross_origin()
# def predictLive():
#     try:
#         model_path  = os.path.join("artifacts", "model_trainer", "best.pt")

#         if not os.path.exists(model_path):
#             return Response(f"Model file not found at {model_path}", status=404)
        
#         model       = YOLO(model_path)  
#         model.predict(source=0, show=True)   # Live webcam feed
#         os.system("rm -rf runs")
#         return "Camera started!!"

#     except ValueError as val:
#         print(val)
#         return Response("Value not found inside JSON data")
#     except Exception as e:
#         print(e)
#         return Response("Camera error")



# Load trained YOLOv11 model from artifact path
model_path = os.path.join("artifacts", "model_trainer", "best.pt")
model      = YOLO(model_path)  


# Frame Generator — Captures webcam, runs inference, streams MJPEG
def gen_frames():
    cap = cv2.VideoCapture(0)  # 0 = default webcam device
    if not cap.isOpened():
        raise RuntimeError("Webcam not accessible — check device or permissions")

    while True:
        success, frame = cap.read()
        if not success:
            break  # Exit loop if frame capture fails

        # ─────────────────────────────────────────────────────
        # Run YOLOv11 inference on current frame
        # stream=True yields generator of Results objects
        # show=False disables OpenCV window popups
        # verbose=False suppresses console spam
        # ─────────────────────────────────────────────────────
        results = model.predict(frame, stream=True, show=False, verbose=False)

        for r in results:
            annotated   = r.plot()  # Overlay bounding boxes and labels
            ret, buffer = cv2.imencode('.jpg', annotated)
            frame_bytes = buffer.tobytes()

            # ─────────────────────────────────────────────────
            # Yield frame in MJPEG format for browser rendering
            # ─────────────────────────────────────────────────
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()  # Ensure camera is released on exit

# ─────────────────────────────────────────────────────────────
# Flask Route — Streams annotated webcam feed to browser
# ─────────────────────────────────────────────────────────────
@app.route("/live", methods=['GET'])
@cross_origin()
def predictLive():
    try:
        if not os.path.exists(model_path):
            return Response(f"Model file not found at {model_path}", status=404)

        # ─────────────────────────────────────────────────────
        # Return MJPEG stream to browser — compatible with Chrome/Firefox
        # ─────────────────────────────────────────────────────
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    except Exception as e:
        print(f"Live stream error: {e}")
        return Response("Camera error", status=500)


# ─────────────────────────────────────────────────────────
# App Entry Point
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host=APP_HOST, port=APP_PORT)