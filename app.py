from flask import Flask, request, jsonify
import cv2
import numpy as np
import requests
import base64
import io
from PIL import Image

app = Flask(__name__)

def process_image(image_url):
    response = requests.get(image_url, stream=True)
    image = Image.open(io.BytesIO(response.content)).convert("RGB")
    img_np = np.array(image)

    # Convert to LAB for better contrast
    lab = cv2.cvtColor(img_np, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)

    # Enhance contrast
    l = cv2.equalizeHist(l)
    lab = cv2.merge((l, a, b))
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    _, buffer = cv2.imencode(".png", enhanced)
    encoded_img = base64.b64encode(buffer).decode("utf-8")

    return f"data:image/png;base64,{encoded_img}"

@app.route("/process_image", methods=["POST"])
def process():
    data = request.json
    if "image_url" not in data:
        return jsonify({"error": "No image URL provided"}), 400

    processed_image = process_image(data["image_url"])
    return jsonify({"processed_image": processed_image})

if __name__ == "__main__":
    app.run(debug=True)
