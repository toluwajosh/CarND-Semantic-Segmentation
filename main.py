import os.path
import tensorflow as tf
import helper
import warnings
from distutils.version import LooseVersion
import project_tests as tests


# Check TensorFlow Version
assert LooseVersion(tf.__version__) >= LooseVersion('1.0'), 'Please use TensorFlow version 1.0 or newer.  You are using {}'.format(tf.__version__)
print('TensorFlow Version: {}'.format(tf.__version__))

# Check for a GPU
if not tf.test.gpu_device_name():
    warnings.warn('No GPU found. Please use a GPU to train your neural network.')
else:
    print('Default GPU Device: {}'.format(tf.test.gpu_device_name()))


def load_vgg(sess, vgg_path):
    """
    Load Pretrained VGG Model into TensorFlow.
    :param sess: TensorFlow Session
    :param vgg_path: Path to vgg folder, containing "variables/" and "saved_model.pb"
    :return: Tuple of Tensors from VGG model (image_input, keep_prob, layer3_out, layer4_out, layer7_out)
    """
    # TODO: Implement function ##### DONE
    #   Use tf.saved_model.loader.load to load the model and weights
    vgg_tag = 'vgg16'
    vgg_input_tensor_name = 'image_input:0'
    vgg_keep_prob_tensor_name = 'keep_prob:0'
    vgg_layer3_out_tensor_name = 'layer3_out:0'
    vgg_layer4_out_tensor_name = 'layer4_out:0'
    vgg_layer7_out_tensor_name = 'layer7_out:0'

    tf.saved_model.loader.load(sess, [vgg_tag], vgg_path)

    graph = tf.get_default_graph()
    image_input = graph.get_tensor_by_name(vgg_input_tensor_name)
    keep_prob = graph.get_tensor_by_name(vgg_keep_prob_tensor_name)
    layer3_out = graph.get_tensor_by_name(vgg_layer3_out_tensor_name)
    layer4_out = graph.get_tensor_by_name(vgg_layer4_out_tensor_name)
    layer7_out = graph.get_tensor_by_name(vgg_layer7_out_tensor_name)

    
    return image_input, keep_prob, layer3_out, layer4_out, layer7_out

# tests.test_load_vgg(load_vgg, tf)


def layers(vgg_layer3_out, vgg_layer4_out, vgg_layer7_out, num_classes):
    """
    Create the layers for a fully convolutional network.  Build skip-layers using the vgg layers.
    :param vgg_layer7_out: TF Tensor for VGG Layer 3 output
    :param vgg_layer4_out: TF Tensor for VGG Layer 4 output
    :param vgg_layer3_out: TF Tensor for VGG Layer 7 output
    :param num_classes: Number of classes to classify
    :return: The Tensor for the last layer of output
    """
    # TODO: Implement function
    conv7 = tf.layers.conv2d(vgg_layer7_out, num_classes, 1, strides=(1,1), padding='same', 
                                kernel_initializer=tf.truncated_normal_initializer(stddev=0.01),
                                kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))

    # print('\nsize of conv7:\n')
    # print_out_ = tf.Print(conv7, [tf.shape(conv7)])
    # print(print_out_)

    conv4 = tf.layers.conv2d(vgg_layer4_out, num_classes, 1, strides=(1,1), padding='same', 
                                kernel_initializer=tf.truncated_normal_initializer(stddev=0.01),
                                kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))

    # print('\nsize of conv4:\n')
    # print_out_ = tf.Print(conv4, [tf.shape(conv4)])
    # print(print_out_)

    conv3 = tf.layers.conv2d(vgg_layer3_out, num_classes, 1, strides=(1,1), padding='same', 
                                kernel_initializer=tf.truncated_normal_initializer(stddev=0.01),
                                kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))

    # print('\nsize of conv3:\n')
    # print_out_ = tf.Print(conv3, [tf.shape(conv3)])
    # print(print_out_)

    # upsample by 2
    upsamp_32x = tf.layers.conv2d_transpose(conv7, num_classes, 4, strides=(2, 2), padding='same', 
                                        kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))


    # add skip connection and upsample by 2
    skip_add_1 = tf.add(upsamp_32x, conv4)
    upsamp_16x = tf.layers.conv2d_transpose(skip_add_1, num_classes, 4, strides=(2, 2), padding='same', 
                                        kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))


    # add skip connection and upsample by 8
    skip_add_2 = tf.add(upsamp_16x, conv3)
    output = tf.layers.conv2d_transpose(skip_add_2, num_classes, 32, strides=(8, 8), padding='same', 
                                        kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))

    # output = tf.layers.conv2d_transpose(output, num_classes, 32, strides=(4, 4), padding='same', 
    #                                     kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))

    # use the right padding and reg
    # upsample by 2, 2, and 8
    # return final output which is the same size as the image
    return output

# tests.test_layers(layers)


def optimize(nn_last_layer, correct_label, learning_rate, num_classes):
    """
    Build the TensorFLow loss and optimizer operations.
    :param nn_last_layer: TF Tensor of the last layer in the neural network
    :param correct_label: TF Placeholder for the correct label image
    :param learning_rate: TF Placeholder for the learning rate
    :param num_classes: Number of classes to classify
    :return: Tuple of (logits, train_op, cross_entropy_loss)
    """
    # TODO: Implement function
    
    # reshape parameters
    logits = tf.reshape(nn_last_layer, (-1, num_classes))
    correct_label = tf.reshape(correct_label, (-1, num_classes))

    cross_entropy_loss = tf.reduce_mean(
        tf.nn.softmax_cross_entropy_with_logits(
            labels=correct_label, logits=logits)
        )

    with tf.name_scope("training"):
      optimizer = tf.train.AdamOptimizer()
      # Create a variable to track the global step.
      global_step = tf.Variable(0, name='global_step', trainable=False)
      # Use the optimizer to apply the gradients that minimize the loss
      # (and also increment the global step counter) as a single training step.
      train_op = optimizer.minimize(cross_entropy_loss, global_step=global_step)

    return logits, train_op, cross_entropy_loss

# tests.test_optimize(optimize)


def train_nn(sess, epochs, batch_size, get_batches_fn, train_op, 
    cross_entropy_loss, input_image, correct_label, keep_prob, learning_rate):
    """
    Train neural network and print out the loss during training.
    :param sess: TF Session
    :param epochs: Number of epochs
    :param batch_size: Batch size
    :param get_batches_fn: Function to get batches of training data.  Call using get_batches_fn(batch_size)
    :param train_op: TF Operation to train the neural network
    :param cross_entropy_loss: TF Tensor for the amount of loss
    :param input_image: TF Placeholder for input images
    :param correct_label: TF Placeholder for label images
    :param keep_prob: TF Placeholder for dropout keep probability
    :param learning_rate: TF Placeholder for learning rate
    """
    # TODO: Implement function
    #correct_prediction = tf.equal(tf.arg_max(logits))
    #accuracy_operation = tf.reduce_mean((tf.cast(correct_prediction, tf.float32)))
    for epoch in range(epochs):
      for i, (image, label) in enumerate(get_batches_fn(batch_size)):
        # Training

        _, loss = sess.run([train_op, cross_entropy_loss], 
            feed_dict={input_image:image, correct_label:label, keep_prob:0.4})

        print("epoch: {}, batch: {}, loss: {}".format(epoch+1, i, loss))
      
# tests.test_train_nn(train_nn)


def run():
    num_classes = 2
    image_shape = (160, 576)
    data_dir = './data'
    runs_dir = './runs'
    tests.test_for_kitti_dataset(data_dir)

    # Download pretrained vgg model
    helper.maybe_download_pretrained_vgg(data_dir)

    # OPTIONAL: Train and Inference on the cityscapes dataset instead of the Kitti dataset.
    # You'll need a GPU with at least 10 teraFLOPS to train on.
    #  https://www.cityscapes-dataset.com/

    tf.reset_default_graph()

    
    
    epochs = 30
    batches = 2

    with tf.Session() as sess:
        # Path to vgg model
        vgg_path = os.path.join(data_dir, 'vgg')
        # Create function to get batches
        get_batches_fn = helper.gen_batch_function(os.path.join(data_dir, 'data_road/training'), image_shape)

        # OPTIONAL: Augment Images for better results
        #  https://datascience.stackexchange.com/questions/5224/how-to-prepare-augment-images-for-neural-network
        # Augmentation was implemented in the helper function get_batches_fn()

        # TODO: Build NN using load_vgg, layers, and optimize function
        input_image, keep_prob, layer3_out, layer4_out, layer7_out = load_vgg(sess, vgg_path)
        final_layer = layers(layer3_out, layer4_out, layer7_out, num_classes)
        label = tf.placeholder(tf.int32, shape=[None, None, None, num_classes])
        learning_rate = tf.placeholder(tf.float32)
        logits, train_op, loss = optimize(final_layer, label, learning_rate, num_classes)

        # to save the trained model (preparation)
        saver = tf.train.Saver()

        # restore saved model here:
        saver.restore(sess, './runs/sem_seg_model.ckpt')

        # # TODO: Train NN using the train_nn function
        # sess.run(tf.global_variables_initializer())

        # train_nn(sess, epochs, batches, get_batches_fn, train_op, loss, 
        #         input_image, label, keep_prob, learning_rate)

        # # # TODO: Save inference data using helper.save_inference_samples
        # helper.save_inference_samples(runs_dir, data_dir, sess, image_shape, logits, keep_prob, input_image)


        # OPTIONAL: Apply the trained model to a video
        data_sub_dir = 'project_video'
        helper.save_to_clip(data_sub_dir, data_dir, sess, image_shape, logits, keep_prob, input_image)

        data_sub_dir = 'challenge_video'
        helper.save_to_clip(data_sub_dir, data_dir, sess, image_shape, logits, keep_prob, input_image)

        data_sub_dir = 'harder_challenge_video'
        helper.save_to_clip(data_sub_dir, data_dir, sess, image_shape, logits, keep_prob, input_image)


        # save model
        # saver.save(sess, './runs/sem_seg_model_01.ckpt')


if __name__ == '__main__':
    # pass
    run()
