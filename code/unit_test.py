from keras.preprocessing import image
from keras.models import Sequential, Model
from keras.layers import *
from keras import backend as K
from bilinear_layer import Bilinear
from keras.callbacks import *
import numpy as np
import utility as util
import data_generators as d_gen
import h5py, pdb, os
import viewsyn_architecture as model

def test_load_weights():
	weights_path = '../model/weights.29-0.95.hdf5'
	f = h5py.File(weights_path)

	# Create Full Network with autoencoder weight initialization
	full_network = fnetwork.build_full_network()
	fnetwork.load_autoenocoder_model_weights(full_network, weights_path)
	
	# Create autoencoder network for test purpose only
	autoencoder = model.build_autoencoder()
	autoencoder.load_weights(weights_path)

	layers = full_network.layers
	
	image_encoder_network = layers[2].layers
	image_decoder_network = layers[5].layers
	
	# Subset of layer that acts as autoencoder in full network
	combined_network = np.concatenate((image_encoder_network, image_decoder_network))

	# Layer names in both the network
	layer_auto_n = ['convolution2d_7', 'convolution2d_8', 'convolution2d_9', 'convolution2d_10', 'convolution2d_11', 'convolution2d_12', 'flatten_2', 'dense_9', 'dropout_3', 'dense_10', 'dropout_4', 'dense_11', 'dense_12', 'reshape_7', 'deconvolution2d_13', 'deconvolution2d_14', 'deconvolution2d_15', 'deconvolution2d_16', 'deconvolution2d_17', 'deconvolution2d_18', 'reshape_8', 'lambda_3', 'reshape_9']
	layer_full_n = [x.name for x in combined_network]
	
	# Load weights layer by layer and compute the difference. Exception occurs for flatten, dropout, reshape layers.
	for i in range(len(layer_full_n)):
		try:
			layer_name_full = layer_full_n[i]
			layer_name_auto = layer_auto_n[i]
			
			layer_auto = autoencoder.get_layer(layer_name_auto)
			layer_full = combined_network[i]
			
			w_auto = layer_auto.get_weights()[0]
			w_full = layer_full.get_weights()[0]
			try:
				diff = (w_auto - w_full) ** 2
				print np.sum(diff)
			except:
				print "Inner Exception, for layer:", layer_full_n[i]
				pdb.set_trace()
		except:
			print "Exception for layer:", layer_full_n[i]
			pdb.set_trace()

def test_bilinear_layer():
	model = Sequential()
	model.add(Bilinear(input_shape=(224, 224, 5)))
	tensor_callback = TensorBoard(log_dir='../logs/', histogram_freq=1, write_graph=True, write_images=True)
	print model.summary()

	current_chair_folder = "../data/debug_input/"
	test_data = util.load_data_bilinear(current_chair_folder)
	model.compile(optimizer='rmsprop', loss='mean_squared_error', metrics=['accuracy'])
	model.fit(test_data, test_data[:,:,:,:-2], batch_size=1, nb_epoch=10, verbose=1, callbacks = [tensor_callback])
	
	out = model.predict(test_data)
	# pdb.set_trace()
	util.save_as_image("../data/debug_output/", out)

def test_transformed_autoencoder():
	weights_path = '../model/weights.39-376.69.hdf5'
	
	t_autoencoder = model.build_transformed_autoencoder()
	t_autoencoder.load_weights(weights_path)

	current_chair_folder = "../data/test/input/"
	test_data, vpt_transformation = util.load_test_image_view(current_chair_folder)
	# pdb.set_trace()
	out = t_autoencoder.predict([test_data, vpt_transformation])
	util.save_as_image("../data/test/", out)

def test_replication_network():
	weights_path = '../model/weights.04-8.03.hdf5'
	
	replication_net = model.build_replication_network()
	replication_net.load_weights(weights_path)

	current_chair_folder = "../data/debug_input/"
	test_data, vpt_transformation = util.load_test_image_view(current_chair_folder)
	# pdb.set_trace()
	out = replication_net.predict([test_data, vpt_transformation])
	
	out[1] = np.reshape(out[1],(-1,224,224))
	util.save_as_image("../data/debug_output/trans_", out[0])
	util.save_as_image("../data/debug_output/", out[1])

if __name__ == '__main__':
	# test_bilinear_layer()
	# test_transformed_autoencoder()
	test_replication_network()