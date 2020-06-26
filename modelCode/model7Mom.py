from keras.models import Model
from keras.layers import Input
from keras.layers.convolutional import Conv2D
from keras.layers.merge import Multiply
from keras.optimizers import SGD

dim1 = 16
dim2 = 30
# comment out ncwh format, use nwhc format instead
# inputShape = (11,dim1,dim2)   #11 channels
inputShape = (dim1, dim2, 11)

in1 = Input(shape=inputShape)
# in2 = Input(shape=(1,dim1,dim2))
in2 = Input(shape=(dim1, dim2, 1))
conv = Conv2D(64, (3,3), padding='same', data_format = 'channels_last', activation = 'relu', use_bias = True)(in1)
conv = Conv2D(64, (3,3), padding='same', data_format = 'channels_last', activation = 'relu', use_bias = True)(conv)
conv = Conv2D(64, (3,3), padding='same', data_format = 'channels_last', activation = 'relu', use_bias = True)(conv)
conv = Conv2D(64, (3,3), padding='same', data_format = 'channels_last', activation = 'relu', use_bias = True)(conv)
conv = Conv2D(64, (3,3), padding='same', data_format = 'channels_last', activation = 'relu', use_bias = True)(conv)
conv = Conv2D(1, (1,1), padding='same', data_format = 'channels_last', activation = 'sigmoid', use_bias = True)(conv)
out = Multiply()([conv,in2])
model = Model(inputs=[in1,in2], outputs=out)
model.compile(loss='binary_crossentropy',optimizer=SGD(lr = 0.01, momentum = 0.99))

