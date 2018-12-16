#Imports and set Camera
import numpy as np
import cv2
import os
import re
import tensorflow as tf
import sys
sys.path.append('D:/Informatik/tensorflowModels/models') # point to your tensorflow dir
sys.path.append('D:/Informatik/tensorflowModels/models/research/object_detection') # point ot your slim dir
sys.path.append('D:/Informatik/tensorflowModels/models/research') # point at your slim dir
from utils import label_map_util
from utils import visualization_utils as vis_util
from http.server import BaseHTTPRequestHandler
import json



# HTTPRequestHandler class
class HTTPServer_RequestHandler(BaseHTTPRequestHandler):
    personWarning = False
    # GET
    def do_GET(self):
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        send_back = {}
        send_back["warning"] = self.personWarning
        send_back = json.dumps(send_back)
        self.wfile.write(bytes(send_back, "UTF-8"))


    def do_POST(self):
        # Send response status code
        self.send_response(200)
        # Send headers
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        send_back = {"warning": True}
        send_back = json.dumps(send_back)
        self.wfile.write(send_back)




class VideoProcessor:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.PATH_TO_MODEL_DIR = os.path.join(os.getcwd(), 'ssd_mobilenet_v1_coco_11_06_2017')
        # Path to frozen detection graph. This is the actual model that is used for the object detection.
        self.PATH_TO_MODEL = os.path.join(self.PATH_TO_MODEL_DIR, 'frozen_inference_graph.pb')
        # List of the strings that is used to add correct label for each box.
        self.PATH_TO_LABELS = os.path.join(self.PATH_TO_MODEL_DIR, 'mscoco_label_map.pbtxt')
        # Load classes ids/labels dictionnary
        self.labels = self.loadClassesLabels(self.PATH_TO_LABELS)
        # Number of classes to detect
        self.NUM_CLASSES = 90
        # Loading label map
        # Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine
        self.label_map = label_map_util.load_labelmap(self.PATH_TO_LABELS)
        self.categories = label_map_util.convert_label_map_to_categories(
            self.label_map, max_num_classes=self.NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(self.categories)
        # Load a frozen TensorFlow model into memory.
        self.graph = tf.Graph()
        self.graph_def = tf.GraphDef()

        with tf.gfile.GFile(self.PATH_TO_MODEL, 'rb') as f:
            self.serialized_graph = f.read()
            self.graph_def.ParseFromString(self.serialized_graph)
        with self.graph.as_default():
            tf.import_graph_def(self.graph_def, name='')
        # Create TensorFlow session
        self.sess = tf.Session(graph=self.graph)
        # Retrieve input image tensor
        self.image_tensor = self.graph.get_tensor_by_name('image_tensor:0')
        # Retrieve bouding box (output) tensor
        # Each box represents a part of the image where a particular object was detected.
        self.boxes_tensor = self.graph.get_tensor_by_name('detection_boxes:0')
        # Retrieve score (output) tensor
        # Each score represent how level of confidence for each of the objects.
        self.scores_tensor = self.graph.get_tensor_by_name('detection_scores:0')
        # Retrieve class index (output) tensor
        self.classes_tensor = self.graph.get_tensor_by_name('detection_classes:0')
        # Retrieve number of detection (output) tensor
        self.num_detections_tensor = self.graph.get_tensor_by_name('num_detections:0')

    @staticmethod
    # Load Tensorflow Graph
    def loadClassesLabels(labels_path):
        labels = {}
        current_id = 0
        with open(labels_path) as f:
            for line in f:
                line = line.strip()
                match = re.match(r'id: ([0-9]+)', line)
                if match:
                    current_id = int(match.group(1))
                else:
                    match = re.match(r'display_name: \"([a-z:A-Z: ]+)\"', line)
                    if match:
                        labels[current_id] = match.group(1)
        # report_info(str(labels))
        return labels

    def create_dict_important_detections(self, boxes, scores, classes, num_detections, threshold):
        important_detections = []
        i = 0
        scores = np.squeeze(scores)
        boxes = np.squeeze(boxes)
        classes = np.squeeze(classes)
        for score in scores:
            if score > threshold:
                important_detection = {}
                important_detection["class"] = self.labels[int(classes[i])]
                important_detection["score"] = scores[i]
                important_detection["box"] = boxes[i]
                important_detections.append(important_detection)
            if i > num_detections:
                break
            i += 1
        return important_detections

    @staticmethod
    def on_person_detect(important_detections):
        person_detected = False
        for important_detection in important_detections:
            if important_detection["class"] == 'person':
                #Change personWarning True
                HTTPServer_RequestHandler.personWarning = True
                person_detected = True
                break
        #change PersonWarning False
        if person_detected == False:
            #print("personWarning False")
            HTTPServer_RequestHandler.personWarning = False

    def start_detection(self):
        nextFrame = True
        while (True):
            if nextFrame:
                # Capture frame-by-frame
                frame = None
                ret, frame = self.cap.read()

                # Reduce Resolution of frame
                #frame_resiszed = cv2.resize(frame, dsize=(320, 240), interpolation=cv2.INTER_CUBIC)
                frame_resiszed = frame

                # Operations on the frame
                frame_expanded = np.expand_dims(frame_resiszed, axis=0)

                (boxes, scores, classes, num_detections) = self.sess.run(
                    [self.boxes_tensor, self.scores_tensor, self.classes_tensor, self.num_detections_tensor],
                    feed_dict={self.image_tensor: frame_expanded})
                # print(num_detections)
                # Display the resulting frame
                # Visualization of the results of a detection.
                frame = vis_util.visualize_boxes_and_labels_on_image_array(
                    frame,
                    np.squeeze(boxes),
                    np.squeeze(classes).astype(np.int32),
                    np.squeeze(scores),
                    self.category_index,
                    use_normalized_coordinates=True,
                    line_thickness=8)

                # Process Results
                important_detections = self.create_dict_important_detections(boxes, scores, classes, num_detections, 0.75)
                self.on_person_detect(important_detections)
                # Display output
                cv2.imshow('object detection', cv2.resize(frame, (640, 480)))
                # cv2.imshow('Webcam', frame)

            # Control Settings
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                self.cap.release()
                break
            # elif cv2.waitKey(1) & 0xFF == ord('n'):
            #    nextFrame= True
            else:
                nextFrame = True