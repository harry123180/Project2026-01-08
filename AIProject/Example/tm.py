import os
import warnings
import numpy as np
import tensorflow as tf
from tf_keras.models import load_model
from PIL import Image, ImageOps

# Suppress TensorFlow logging and warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' # Disable oneDNN custom operations messages
tf.get_logger().setLevel('ERROR')
warnings.filterwarnings("ignore")

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Try to find the files
# 1. First try the path you provided
# 2. If not found, try the directory where the script is located
model_path = r"D:\AWORKSPACE\Github\Project2026-01-08\HarryAIProject\keras_model.h5"
labels_path = r"D:\AWORKSPACE\Github\Project2026-01-08\HarryAIProject\labels.txt"

if not os.path.exists(model_path):
    # Fallback to local directory
    local_model = os.path.join(os.path.dirname(__file__), "keras_model.h5")
    if os.path.exists(local_model):
        model_path = local_model
        labels_path = os.path.join(os.path.dirname(__file__), "labels.txt")
    else:
        print(f"Error: Model file not found!")
        print(f"Looked in: {model_path}")
        print(f"And also: {local_model}")
        exit()

if not os.path.exists(labels_path):
    print(f"Error: Labels file not found at {labels_path}")
    exit()

# Load the model
model = load_model(model_path, compile=False)

# Load the labels
with open(labels_path, "r", encoding="utf-8") as f:
    class_names = [line.strip() for line in f.readlines()]

# Create the array of the right shape to feed into the keras model
# The 'length' or number of images you can put into the array is
# determined by the first position in the shape tuple, in this case 1
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# Replace this with the path to your image
image_path = r"D:\user\Pictures\Camera Roll\WIN_20260108_14_19_16_Pro.jpg"

if image_path == "<IMAGE_PATH>" or not os.path.exists(image_path):
    print(f"Error: Please update <IMAGE_PATH> with a valid image file path. (Current: {image_path})")
    exit()

try:
    image = Image.open(image_path).convert("RGB")
except Exception as e:
    print(f"Error opening image: {e}")
    exit()

# resizing the image to be at least 224x224 and then cropping from the center
size = (224, 224)
image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

# turn the image into a numpy array
image_array = np.asarray(image)

# Normalize the image
normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

# Load the image into the array
data[0] = normalized_image_array

# Predicts the model
prediction = model.predict(data, verbose=0)
index = np.argmax(prediction)
class_name = class_names[index]
confidence_score = prediction[0][index]

# Print prediction and confidence score
display_name = class_name.split(" ", 1)[1] if " " in class_name else class_name
print(f"Class: {display_name}")
print(f"Confidence Score: {confidence_score:.4f}")
