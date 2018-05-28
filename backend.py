from keras.layers import Input,BatchNormalization,Conv2D,MaxPooling2D,Lambda
from keras.models import Model
import tensorflow as tf

ALPHA=1.0
TINY_YOLO_WEIGHTS="models/tiny_yolo_backend.h5"
##add leakyrelu from https://github.com/tensorflow/tensorflow/issues/4079, for saving memory
def lrelu(x,alpha=0.1,name="lrelu"):
  with tf.variable_scope(name):
    f1=0.5*(1+alpha)
    f2=0.5*(1-alpha)
    return f1*x+f2*tf.abs(x)

def lrelu_outshape(input_shape):
  return input_shape

class BaseFeatureExtractor(object):
  def __init__(self,input_size):
    raise NotImplementedError("intialized failed...")

  def normalize(self,img):
    raise NotImplementedError("normalized failed...")

  def get_output_shape(self):
    return self.feature_extractor.get_output_shape_at(-1)[1:3]

  def extract(self,input_img):
    return self.feature_extractor(input_img)

class TinyYolo(BaseFeatureExtractor):
  def __init__(self,input_size):
    my_lrelu_layer=Lambda(lrelu,output_shape=lrelu_outshape)
    input_=Input(shape=(input_size,input_size,3))
    
    #Layer 1
    x=Conv2D(int(ALPHA*16),(3,3),padding="same",use_bias=False)(input_)
    x=BatchNormalization()(x)
    x=my_lrelu_layer(x)
    x=MaxPooling2D()(x)

    #Layer 2-5
    for i in range(4):
      x=Conv2D(int(ALPHA*32*(2**i)),(3,3),padding="same",use_bias=False)(x)
      x=BatchNormalization()(x)
      x=my_lrelu_layer(x)
      x=MaxPooling2D()(x)

    #Layer 6
    x=Conv2D(int(ALPHA*512),(3,3),padding="same",use_bias=False)(x)
    x=BatchNormalization()(x)
    x=my_lrelu_layer(x)
    x=MaxPooling2D(strides=(1,1),padding="same")(x)

    #Layer 7-8
    for i in range(2):
      x=Conv2D(int(ALPHA*1024),(3,3),padding="same",use_bias=False)(x)
      x=BatchNormalization()(x)
      x=my_lrelu_layer(x)
    
    self.feature_extractor=Model(input_,x)
    self.feature_extractor.load_weights(TINY_YOLO_WEIGHTS)
    print("load weights from "+TINY_YOLO_WEIGHTS)
  def normalize(self,img):
    return img/255.

if __name__=="__main__":
  model=TinyYolo(416)
  print(model.feature_extractor.summary())
