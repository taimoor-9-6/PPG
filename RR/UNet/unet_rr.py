# -*- coding: utf-8 -*-
"""UNet_rr.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13APHhCdOgH0K9DAmt4-VvwzhbjwlWYKA
"""

#Importing google drive
from google.colab import drive
drive.mount('/content/drive')

#Importing required libraries
from tensorflow.keras.layers import  Dense, Dropout,  Input, Reshape, Conv1D, Activation,BatchNormalization, MaxPooling1D,LSTM
from tensorflow.keras.optimizers import Adam, RMSprop, Adagrad, SGD
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, CSVLogger
from tensorflow.keras.utils import to_categorical, plot_model
import scipy.io
from scipy import signal
import glob
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import seaborn as sns
import time

pip install -q git+https://github.com/tensorflow/examples.git

import PIL
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

import keras
from keras.models import Sequential
from keras.layers import Dense, Conv2D , MaxPool2D , Flatten , Dropout 
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam

from tensorflow.keras.layers import  Dense, Dropout,  Input, Reshape, Conv1D, Activation,BatchNormalization, MaxPooling1D,LSTM
from tensorflow.keras.optimizers import Adam, RMSprop, Adagrad, SGD
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, CSVLogger
from tensorflow.keras.utils import to_categorical, plot_model

from tensorflow.keras import datasets, layers, models
from tensorflow_examples.models.pix2pix import pix2pix

import os
import numpy as np
import cv2
from glob import glob
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, CSVLogger, TensorBoard
import tensorflow as tf
from tensorflow.keras.layers import *
from tensorflow.keras.models import Model

#Loading data
# trainname='bidmc'
# truename='bidmc_true'
# train_raw=pd.read_csv('/content/drive/MyDrive/RAship/'+trainname+'.csv',header=None)
# true=pd.read_csv('/content/drive/MyDrive/RAship/'+truename+'.csv',header=None)

# # # For bidmc
# true=true.drop(true.index[0])
# del train_raw[0]
# train_raw=train_raw.drop(train_raw.index[0])
# del true[0]


# true=true.drop(true.index[0])
# train_raw=train_raw.drop(train_raw.index[0])

# q=true
# w=train_raw

# q=np.array(q)
# w=np.array(w)

# true=true.iloc[0:8000,:]
# train_raw=train_raw.iloc[0:8000,:]

# train_raw=np.array(train_raw)
# true=np.array(true)

#Synthetic without windows
# train_raw=pd.read_csv('/content/drive/MyDrive/RAship/synthetic_rr_am_proc.csv',header=None)
# true=pd.read_csv('/content/drive/MyDrive/RAship/synthetic_rr_true_am_proc.csv',header=None)

# train_raw=np.array(train_raw)
# true=np.array(true)



#Synthetic with windows
trainname='synthetic_windows'
truename='synthetic_windows_true'
train_raw=pd.read_csv('/content/drive/MyDrive/RAship/synthetic_rr_am_windows.csv',header=None)
true=pd.read_excel('/content/drive/MyDrive/RAship/synthetic_true_windows.xlsx')

# true=true.drop(true.index[0])
train_raw=train_raw.drop(train_raw.index[0])
train_raw=np.array(train_raw)
true=np.array(true)

print("Shape of training data with windows=",train_raw.shape)
print("Shape of true data with windows=",true.shape)

train_raw

#Declaring the variables
BATCH_SIZE=25
EPOCHS=100
BASE_DIR='/content/drive/MyDrive/RAship/M_weights'
train_raw=train_raw[:,0:4000]
INPUT_SHAPE=train_raw.shape[1]
print(INPUT_SHAPE)
# print(q.shape)

def conv_block(x, num_filters):
    x = Conv1D(num_filters, 40, padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    x = Dropout(0.1)(x)

    x = Conv1D(num_filters, 40, padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    x = Dropout(0.1)(x)
    return x

#Splitting the training data into train and test
PPG_train, PPG_test, PPG_true_train, PPG_true_test=train_test_split(train_raw,true,test_size=0.32,random_state=42)

def build_model():
    size =INPUT_SHAPE
    num_filters = [40,40, 40, 40]
    inputs = Input((INPUT_SHAPE,1))
    skip_x = []
    x = inputs
    # print(x.shape)
    ## Encoder
    for f in num_filters:
        x = conv_block(x, f)
        # print(x.shape)
        skip_x.append(x)
        x = MaxPooling1D(pool_size=2)(x)
        # print(x.shape)
    ## Bridge
    x = conv_block(x, num_filters[-1])
    print("Filter no", num_filters[-1])
    num_filters.reverse()
    skip_x.reverse()

    # print(x.shape)
    ## Decoder
    for i, f in enumerate(num_filters):
        print("i=",i)
        x = UpSampling1D(size=2)(x)
        xs = skip_x[i]
        print(xs)
        # xs=xs.reshape(xs.shape[0]-1,xs.shape[0]-1)
        print(xs.shape)
        print(x.shape)
        x = Concatenate()([x, xs])
        x = conv_block(x, f)
    ## Output
    m=x
    # x = Conv1D(30, 40, padding="same")(x)
    # x=Dropout(0.1)(x)
    # x=LSTM(128,activation='tanh')(x)
    # # x = Activation("sigmoid")(x)
    # # x = Flatten()(x)
    # # x = Dense(64,activation='relu')(x)
    # x = Dense(1)(x)
    # m=Conv1D(30,kernel_size=40,padding='same')(m)
    # m=BatchNormalization()(m)
    # m=Activation('relu')(m)
    # m=MaxPooling1D(pool_size=2)(m)
    # m=Dropout(0.1)(m)
    # m=Conv1D(30,kernel_size=40,padding='same')(m)
    # m=BatchNormalization()(m)
    # m=Activation('relu')(m)
    # m=MaxPooling1D(pool_size=2)(m)
    m=Dropout(0.1)(m)
    m=Flatten()(m)
    # m=MaxPooling1D(pool_size=2)(m)
    # m=LSTM(128, activation='tanh',return_sequences=True)(m)
    # m=LSTM(128, activation='tanh')(m)
    m=Dense(1)(m)  
    x=m  
    return Model(inputs, x)

unet=build_model()
unet.summary()

plot_model(unet,show_shapes=True)

# Callback for saving model weights and log training results
def get_callbacks(name_weights):
    mcp_save = ModelCheckpoint(name_weights+"_weights.hdf5", save_best_only=True, monitor='val_loss', mode='min')
    csv_log=CSVLogger(name_weights+'.csv',separator=',')
    return [mcp_save, csv_log]

gen_corenet=build_model()
change="complete"
gen_corenet.compile(optimizer='RMSprop', loss='mean_absolute_error', metrics=['mse'])
weight_dir=BASE_DIR+'/GenModel/'+trainname
if not os.path.exists(weight_dir):
    os.mkdir(weight_dir)
name_weights = weight_dir+"/GenModel"+change

start_time = time.time()

callbacks = get_callbacks(name_weights)
history=gen_corenet.fit(PPG_train,PPG_true_train, batch_size=25,epochs=200,verbose=1,validation_data=(PPG_test,PPG_true_test),callbacks=callbacks,use_multiprocessing=False)
# # history=gen_corenet.fit(PPG_train,PPG_true_train, batch_size=BATCH_SIZE,epochs=EPOCHS,verbose=1,callbacks=callbacks)
print("--- %s seconds ---" % (time.time() - start_time))

plot_model(resnet,show_shapes=True)

def plotHistory(histories, name, metric):
    plt.clf() 
    x_axis = list(range(EPOCHS))
    plt.plot(x_axis, histories.history[metric], label=metric+'_'+name)
    plt.scatter(x_axis, histories.history[metric])
    #for hist, name in zip(histories, names):
    #    plt.plot(x_axis, hist.history[metric], label=metric+'_'+name)
    #    plt.scatter(x_axis, hist.history[metric])
    plt.legend()
    plt.title(metric)
    plt.show()

2
# plotHistory(history,'Cornet Loss','loss')
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('BIDMC Dataset Loss with U-Net Architecture')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
# plotHistory(history,'Cornet Validation','val_loss')

trainloss=history.history['loss']
testloss=history.history['val_loss']

trainloss=np.array(trainloss)
testloss=np.array(testloss)

# bidmc_corenet_trainloss_prior=np.reshape(bidmc_corenet_trainloss_prior,(-1,1))
# bidmc_corenet_testloss_prior=np.reshape(bidmc_corenet_testloss_prior,(-1,1))

loss = {
    'train_loss': trainloss.flatten(),
    'test_loss': testloss.flatten(),
}

loss_1 = pd.DataFrame(loss)

loss_1

with open('drive/My Drive/RAship/syn_unet_loss.csv', 'w') as f:
  loss_1.to_csv(f)

train_raw.shape

y_test=true
y_train=train_raw
#Predicting the testing sample 
StatList=[]
BPM_dir=BASE_DIR+'/Estimated_gen/'+trainname+'/'
if not os.path.exists(BPM_dir):
    os.mkdir(BPM_dir)
preds=gen_corenet.predict(y_train,514,1)
filename = BPM_dir+'/Est_'+change+'S'+trainname+'.mat'
scipy.io.savemat(filename,{"Estimate":preds,"TrueBPM":y_test})
# StatList.append(['Subject '+trainname,np.mean(np.absolute(PPG_true_test-preds)),np.std(np.absolute(PPG_true_test-preds))])

preds.shape

#Calculating the overall MAE of the testing set
n=len(preds)
MAE=(1/n)*np.sum(np.abs(y_test-preds))
print(MAE)

#Storing values for analysis
BIDMC=MAE
BIDMC_preds=preds
BIDMC_true=y_test

#Converting array to dataframe
data = {
    'preds': BIDMC_preds.flatten(),
    'true': BIDMC_true.flatten(),
}

final = pd.DataFrame(data)

MAE_per_sample=np.abs(BIDMC_preds-BIDMC_true)
df2 = pd.DataFrame({'MAE':MAE_per_sample.flatten()})
sns.scatterplot(x=df2.index,y='MAE',data=df2)
plt.title("MAE's of predicted vs true")
plt.xlabel("Window sample")
# df.plot(kind='scatter', x='x1', y='columnA')

sns.set_theme(style="whitegrid")
# df2 = sns.load_dataset(df2)
sns.violinplot(x='MAE',data=df2)
plt.title("Distribution of MAE's for the whole dataset")

final

#Calculating mae for both datasets
mae_bidmc=mean_absolute_error(final.true,final.preds)
# mae_max=mean_absolute_error(maxrefds.true,maxrefds.preds)

std_bidmc=np.std(final.true-final.preds)
# std_maxrefds=np.std(maxrefds.true-maxrefds.preds)
                    
print("Mean absolute error and Standard Deviation for bidmc dataset is=", mae_final,"+-",std_final)
# print("Mean absolute error and Standard Deviation for maxrefds(our own) dataset is=", mae_max,"+-",std_maxrefds)

with open('drive/My Drive/RAship/syn_unet_true.csv', 'w') as f:
  final.to_csv(f)

###EXTRA###

