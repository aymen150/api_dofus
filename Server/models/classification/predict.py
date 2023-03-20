# The steps implemented in the object detection sample code: 
# 1. for an image of width and height being (w, h) pixels, resize image to (w', h'), where w/h = w'/h' and w' x h' = 262144
# 2. resize network input size to (w', h')
# 3. pass the image to network and do inference
# (4. if inference speed is too slow for you, try to make w' x h' smaller, which is defined with DEFAULT_INPUT_SIZE (in object_detection.py or ObjectDetection.cs))
"""Sample prediction script for TensorFlow 2.x."""
import cv2
import sys
import tensorflow as tf
import numpy as np
from PIL import Image

MODEL_FILENAME = 'model.pb'
LABELS_FILENAME = 'labels.txt'


class TFObjectClassification():
    """Object Detection class for TensorFlow"""

    def __init__(self, graph_def, labels):
        self.labels = labels
        self.graph = tf.compat.v1.Graph()
        # Get the input size of the model
        with self.graph.as_default():
            input_data = tf.compat.v1.placeholder(tf.float32, [1, None, None, 3], name='Placeholder')
            tf.import_graph_def(graph_def, input_map={"Placeholder:0": input_data}, name="")


    def predict_image(self, image):
            inputs = self.preprocess(image)
            prediction_outputs = self.predict(inputs)
            return self.postprocess(prediction_outputs)

    def preprocess(self, image):
            # Update orientation based on EXIF tags, if the file has orientation info.
        image = self.update_orientation(image)

            # Convert to OpenCV format
        image = self.convert_to_opencv(image)
        # If the image has either w or h greater than 1600 we resize it down respecting
        # aspect ratio such that the largest dimension is 1600
        image = self.resize_down_to_1600_max_dim(image)
        # We next get the largest center square
        h, w = image.shape[:2]
        min_dim = min(w,h)
        max_square_image = self.crop_center(image, min_dim, min_dim)
        # Resize that square down to 256x256
        augmented_image = self.resize_to_256_square(max_square_image)
        return augmented_image
    

    def predict(self, augmented_image): 
        output_layer = 'loss:0'
        input_node = 'Placeholder:0'
        with tf.compat.v1.Session() as sess:
            try:
                input_tensor_shape = sess.graph.get_tensor_by_name('Placeholder:0').shape.as_list()
                network_input_size = input_tensor_shape[1]
                augmented_image = self.crop_center(augmented_image, network_input_size, network_input_size)
                prob_tensor = sess.graph.get_tensor_by_name(output_layer)
                predictions = sess.run(prob_tensor, {input_node: [augmented_image] })
                return predictions
            except KeyError:
                print ("Couldn't find classification output layer: " + output_layer + ".")
                print ("Verify this a model exported from an Object Detection project.")
                exit(-1)
        
    
    def postprocess(self, predictions_outputs):
        highest_probability_index = np.argmax(predictions_outputs)
        return  self.labels[highest_probability_index]
    
    def crop_center(self,img,cropx,cropy):
        h, w = img.shape[:2]
        startx = w//2-(cropx//2)
        starty = h//2-(cropy//2)
        return img[starty:starty+cropy, startx:startx+cropx]
    
    
    def convert_to_opencv(self,image):
            # RGB -> BGR conversion is performed as well.
        image = image.convert('RGB')
        r,g,b = np.array(image).T
        opencv_image = np.array([b,g,r]).transpose()
        return opencv_image



    def resize_down_to_1600_max_dim(self,image):
        h, w = image.shape[:2]
        if (h < 1600 and w < 1600):
            return image

        new_size = (1600 * w // h, 1600) if (h > w) else (1600, 1600 * h // w)
        return cv2.resize(image, new_size, interpolation = cv2.INTER_LINEAR)

    def resize_to_256_square(self,image):
        h, w = image.shape[:2]
        return cv2.resize(image, (256, 256), interpolation = cv2.INTER_LINEAR)

    def update_orientation(self,image):
        exif_orientation_tag = 0x0112
        if hasattr(image, '_getexif'):
            exif = image._getexif()
            if (exif != None and exif_orientation_tag in exif):
                orientation = exif.get(exif_orientation_tag, 1)
                # orientation is 1 based, shift to zero based and flip/transpose based on 0-based values
                orientation -= 1
                if orientation >= 4:
                    image = image.transpose(Image.TRANSPOSE)
                if orientation == 2 or orientation == 3 or orientation == 6 or orientation == 7:
                    image = image.transpose(Image.FLIP_TOP_BOTTOM)
                if orientation == 1 or orientation == 2 or orientation == 5 or orientation == 6:
                    image = image.transpose(Image.FLIP_LEFT_RIGHT)
            return image

    #############################################""

# Crop the center for the specified network_input_Size
        

def load_model(MODEL_FILENAME,LABELS_FILENAME):
    # Load a TensorFlow model
    graph_def = tf.compat.v1.GraphDef()
    labels = []
        
    with tf.io.gfile.GFile(MODEL_FILENAME, 'rb') as f:
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def, name='')

    # Create a list of labels.
    with open(LABELS_FILENAME, 'rt') as lf:
        for l in lf:
            labels.append(l.strip())   
    od_model = TFObjectClassification(graph_def, labels)
    return od_model



if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('USAGE: {} image_filename'.format(sys.argv[0]))
    else:
        main(sys.argv[1])
