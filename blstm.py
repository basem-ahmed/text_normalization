import tensorflow as tf
from tensorflow.contrib import rnn
import numpy as np


def BiRNN(num_hidden, num_classes, learning_rate):


	# Inputs
	# None allows it to be of variable size
	X = tf.placeholder(tf.float32, [None, None, num_input])
	Y = tf.placeholder(tf.float32, [None, num_classes])
	timesteps = tf.placeholder(tf.float32, shape=())

	# Define weights
	weights = {
		# Hidden layer weights => 2*n_hidden because of forward + backward cells
		'out': tf.Variable(tf.random_normal([2*num_hidden, num_classes]))
	}
	biases = {
		'out': tf.Variable(tf.random_normal([num_classes]))
	}

	# Reshape to match rnn.static_bidirectional_rnn function requirements
	# Current data input shape: (batch_size, timesteps, n_input)
	# Required shape: 'timesteps' tensors list of shape (batch_size, num_input)
	X = tf.unstack(X, timesteps, 1)

	# Define lstm cells with tensorflow
	# Forward direction cell
	lstm_fw_cell = rnn.BasicLSTMCell(num_hidden, forget_bias=1.0)
	# Backward direction cell
	lstm_bw_cell = rnn.BasicLSTMCell(num_hidden, forget_bias=1.0)

	# Get lstm cell output
	try:
		outputs, _, _ = rnn.static_bidirectional_rnn(lstm_fw_cell, lstm_bw_cell, X,
											  dtype=tf.float32)
	except Exception: # Old TensorFlow version only returns outputs not states
		outputs = rnn.static_bidirectional_rnn(lstm_fw_cell, lstm_bw_cell, X,
										dtype=tf.float32)

	#@TODO Linear activation for now. Not sure what the paper uses!
	logits = tf.matmul(outputs[-1], weights['out']) + biases['out']
	prediction = tf.nn.softmax(logits)

	# Cross entropy loss
	loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(
		logits=logits, labels=Y))

	#Automatically updates variables
	optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(loss_op)

	# # Uncomment for Mean accuracy if needed
	# correct_pred = tf.equal(tf.argmax(prediction, 1), tf.argmax(Y, 1))
	# accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

	return x, Y, timesteps, prediction, loss_op, optimizer



if __name__ == '__main__':

	#@TODO
	# input_data = get_input() #How do we do this?
	# validation_data = get_input() 
	# test_data = get_input()

	learning_rate = 0.001 # Can do Cross Validation
	epochs = 100 # Need more?
	batch_size = 128 #@TODO Not sure if we can do batches
	display_step = 200

	num_input = 28 # Depending on character embeddings we get on google
	num_hidden = 128 # hidden layer num of features
	num_classes = 256 # Number of possible characters, 256 ASCII for now

	# Initialize the variables (i.e. assign their default value)
	init = tf.global_variables_initializer()

	# Save checkpoints on the way
	saver = tf.train.Saver()

	# Start training
	with tf.Session() as sess:
		x, Y, timesteps, prediction, loss_op, optimizer = BiRNN(num_hidden, num_classes, learning_rate)
		# Run the initializer
		sess.run(init)

		for epoch in range(1, epochs+1):
			for batch_x, batch_y in input_data(): #Define input_data of size 1 x timesteps x num_input : @TODO Can we do batches?
				feed_dict = {X:batch_x, Y:batch_y, timesteps:batch_x.shape[1]}
				#Run and train
				batch_loss, _ = sess.run([loss_op, optimizer], feed_dict)
				if step % display_step == 0 or step == 1:
					print("Step " + str(step) + ", Minibatch Loss= " + \
						  "{:.4f}".format(loss))

		print("Optimization Finished!")


		#@TODO Validation and Test Should be quite similar