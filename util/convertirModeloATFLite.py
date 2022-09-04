from os import stat
import tensorflow as tf
import numpy as np
import time
from PIL import Image
path = "D:/Documentos/Cole/Carrera/5/TFG/tfg-comportamientosVisualesSencillos/Webots/controllers/tensorforceController/evaluacion/agenteDeepQLearning_03_10.07.2022_16.32.28/agentModel/agenteDeepQLearning_03"

img_path = "D:/Documentos/Cole/Carrera/5/TFG/tfg-comportamientosVisualesSencillos/Webots/controllers/tensorforceController/evaluacion/agenteDeepQLearning_03_10.07.2022_16.32.28/states/state_agenteDeepQLearning_03_10.07.2022_16.32.28.000954.png"
# Convert the model
'''converter = tf.lite.TFLiteConverter.from_saved_model(path) # path to the SavedModel directory

tflite_model = converter.convert()

# Save the model.
with open('model.tflite', 'wb') as f:
  f.write(tflite_model)
'''
interpreter = tf.lite.Interpreter(model_path='model.tflite')

interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

floating_model = input_details[1]['dtype'] == np.float32

# NxHxWxC, H:1, W:2
height = input_details[1]['shape'][1]
width = input_details[1]['shape'][2]

print(floating_model)
print(height, width)

img = Image.open(img_path)

input_data = np.expand_dims(img, axis=0)
input_data = np.int64(input_data)

interpreter.set_tensor(input_details[1]['index'], input_data)
print(input_data)
start_time = time.time()
interpreter.invoke()
stop_time = time.time()

output_data = interpreter.get_tensor(output_details[0]['index'])
results = np.squeeze(output_data)
print(output_data, "Tiempo: ", stop_time-start_time)