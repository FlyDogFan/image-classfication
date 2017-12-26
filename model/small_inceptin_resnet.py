
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import tensorflow.contrib.slim as slim

# Inception-Renset-A
def block35(net, scale=1.0, activation_fn=tf.nn.relu, scope=None, reuse=None):
    """Builds the 35x35 resnet block."""
    with tf.variable_scope(scope, 'Block35', [net], reuse=reuse):
        with tf.variable_scope('Branch_0'):
            tower_conv = slim.conv2d(net, 32, 1, scope='Conv2d_1x1')
        with tf.variable_scope('Branch_1'):
            tower_conv1_0 = slim.conv2d(net, 32, 1, scope='Conv2d_0a_1x1')
            tower_conv1_1 = slim.conv2d(tower_conv1_0, 32, 3, scope='Conv2d_0b_3x3')
        with tf.variable_scope('Branch_2'):
            tower_conv2_0 = slim.conv2d(net, 32, 1, scope='Conv2d_0a_1x1')
            tower_conv2_1 = slim.conv2d(tower_conv2_0, 32, 3, scope='Conv2d_0b_3x3')
            tower_conv2_2 = slim.conv2d(tower_conv2_1, 32, 3, scope='Conv2d_0c_3x3')
        mixed = tf.concat([tower_conv, tower_conv1_1, tower_conv2_2], 3)
        up = slim.conv2d(mixed, net.get_shape()[3], 1, normalizer_fn=None,
                         activation_fn=None, scope='Conv2d_1x1')
        net += scale * up
        if activation_fn:
            net = activation_fn(net)
    return net

# Inception-Renset-B
def block17(net, scale=1.0, activation_fn=tf.nn.relu, scope=None, reuse=None):
    """Builds the 17x17 resnet block."""
    with tf.variable_scope(scope, 'Block17', [net], reuse=reuse):
        with tf.variable_scope('Branch_0'):
            tower_conv = slim.conv2d(net, 128, 1, scope='Conv2d_1x1')
        with tf.variable_scope('Branch_1'):
            tower_conv1_0 = slim.conv2d(net, 128, 1, scope='Conv2d_0a_1x1')
            tower_conv1_1 = slim.conv2d(tower_conv1_0, 128, [1, 7],
                                        scope='Conv2d_0b_1x7')
            tower_conv1_2 = slim.conv2d(tower_conv1_1, 128, [7, 1],
                                        scope='Conv2d_0c_7x1')
        mixed = tf.concat([tower_conv, tower_conv1_2], 3)
        up = slim.conv2d(mixed, net.get_shape()[3], 1, normalizer_fn=None,
                         activation_fn=None, scope='Conv2d_1x1')
        net += scale * up
        if activation_fn:
            net = activation_fn(net)
    return net


# Inception-Resnet-C
def block8(net, scale=1.0, activation_fn=tf.nn.relu, scope=None, reuse=None):
    """Builds the 8x8 resnet block."""
    with tf.variable_scope(scope, 'Block8', [net], reuse=reuse):
        with tf.variable_scope('Branch_0'):
            tower_conv = slim.conv2d(net, 128, 1, scope='Conv2d_1x1')
        with tf.variable_scope('Branch_1'):
            tower_conv1_0 = slim.conv2d(net, 128, 1, scope='Conv2d_0a_1x1')
            tower_conv1_1 = slim.conv2d(tower_conv1_0, 128, [1, 3],
                                        scope='Conv2d_0b_1x3')
            tower_conv1_2 = slim.conv2d(tower_conv1_1, 128, [3, 1],
                                        scope='Conv2d_0c_3x1')
        mixed = tf.concat([tower_conv, tower_conv1_2], 3)
        up = slim.conv2d(mixed, net.get_shape()[3], 1, normalizer_fn=None,
                         activation_fn=None, scope='Conv2d_1x1')
        net += scale * up
        if activation_fn:
            net = activation_fn(net)
    return net
  
def reduction_a(net, k, l, m, n):
    with tf.variable_scope('Branch_0'):
        tower_conv = slim.conv2d(net, n, 3, stride=2, padding='VALID',
                                 scope='Conv2d_1a_3x3')
    #with tf.variable_scope('Branch_1'):
        #tower_conv1_0 = slim.conv2d(net, k, 1, scope='Conv2d_0a_1x1')
        #tower_conv1_1 = slim.conv2d(tower_conv1_0, l, 3,
                                    #scope='Conv2d_0b_3x3')
        #tower_conv1_2 = slim.conv2d(tower_conv1_1, m, 3,
                                   # stride=2, padding='VALID',
                                   # scope='Conv2d_1a_3x3')
    with tf.variable_scope('Branch_2'):
        tower_pool = slim.max_pool2d(net, 3, stride=2, padding='VALID',
                                     scope='MaxPool_1a_3x3')
    net = tf.concat([tower_conv, tower_pool], 3)
    return net

def reduction_b(net):
    with tf.variable_scope('Branch_0'):
        tower_conv = slim.conv2d(net, 64, 1, scope='Conv2d_0a_1x1')
        tower_conv_1 = slim.conv2d(tower_conv, 128, 3, stride=2,
                                   padding='VALID', scope='Conv2d_1a_3x3')
    with tf.variable_scope('Branch_2'):
        tower_conv2 = slim.conv2d(net, 96, 1, scope='Conv2d_0a_1x1')
        #tower_conv2_1 = slim.conv2d(tower_conv2, 128, 3,
                                   # scope='Conv2d_0b_3x3')
        tower_conv2_2 = slim.conv2d(tower_conv2, 196, 3, stride=2,
                                    padding='VALID', scope='Conv2d_1a_3x3')
    with tf.variable_scope('Branch_3'):
        tower_pool = slim.max_pool2d(net, 3, stride=2, padding='VALID',
                                     scope='MaxPool_1a_3x3')
    net = tf.concat([tower_conv_1, 
                        tower_conv2_2, tower_pool], 3)
    return net
    
def inference(images, keep_probability, phase_train=True, 
              bottleneck_layer_size=128, weight_decay=0.0, reuse=None):
    batch_norm_params = {
        # Decay for the moving averages.
        'decay': 0.995,
        # epsilon to prevent 0s in variance.
        'epsilon': 0.001,
        # force in-place updates of mean and variance estimates
        'updates_collections': None,
        # Moving averages ends up in the trainable variables collection
        'variables_collections': [ tf.GraphKeys.TRAINABLE_VARIABLES ],
    }
    
    with slim.arg_scope([slim.conv2d, slim.fully_connected],
                        weights_initializer=tf.truncated_normal_initializer(stddev=0.1),
                        weights_regularizer=slim.l2_regularizer(weight_decay),
                        normalizer_fn=slim.batch_norm,
                        normalizer_params=batch_norm_params):
        return inception_resnet_v1(images, is_training=phase_train,
              dropout_keep_prob=keep_probability, bottleneck_layer_size=bottleneck_layer_size, reuse=reuse)


def inception_resnet_v1(inputs, is_training=True,
                        dropout_keep_prob=0.8,
                        bottleneck_layer_size=512,
                        reuse=None, 
                        scope='InceptionResnetV1'):
    """Creates model
    Args:
      inputs: a 4-D tensor of size [batch_size, 32, 32, 3].
      num_classes: number of predicted classes.
      is_training: whether is training or not.
      dropout_keep_prob: float, the fraction to keep before final layer.
      reuse: whether or not the network and its variables should be reused.
      scope: Optional variable_scope.
    Returns:
      logits: the logits outputs of the model.
      end_points: the set of end_points from the inception model.
    """
    end_points = {}
  
    with tf.variable_scope(scope, 'InceptionResnetV1', [inputs], reuse=reuse):
        with slim.arg_scope([slim.batch_norm, slim.dropout],
                            is_training=is_training):
            with slim.arg_scope([slim.conv2d, slim.max_pool2d, slim.avg_pool2d],
                                stride=1, padding='SAME'):

                
                print("inputs ",inputs.get_shape().as_list())
                #30, 30, 32
                net = slim.conv2d(inputs,32,3,stride=1,padding='VALID',scope='conv_1_3x3')
                print("after conv_1_3x3 ",net.get_shape().as_list())

                #14, 14, 96
                net = slim.conv2d(net,96,3,stride=2,padding='VALID',scope='conv_2_3x3')
                print("after conv_2_3x3 ",net.get_shape().as_list())

                #14, 14, 96
                #net = slim.conv2d(net,96,3,scope='conv_3_3x3')
                #print("after conv_3_3x3 ",net.get_shape().as_list())

                #14, 14, 96
                net = slim.repeat(net, 1, block35, scale=1)
                print("after block35 4 ci ",net.get_shape().as_list())
                

                #6 * 6 * 256
                with tf.variable_scope('Mixed_6a'):
                    net = reduction_a(net, 32, 32, 64, 96)
                print("after  reduction_a(net) ",net.get_shape().as_list())
                #6 * 6 * 256
                net = slim.repeat(net, 1, block8, scale=1)
                print("after slim.repeat(net, 4, block8, scale=1) ",net.get_shape().as_list())
                
                #2 * 2 * 512
                with tf.variable_scope('Mixed_7a'):
                    net = reduction_b(net)
                print("after  reduction_b(net) ",net.get_shape().as_list())

                with tf.variable_scope('Logits'):

                    #pylint: disable=no-member
                    net = slim.avg_pool2d(net, net.get_shape()[1:3], padding='VALID',
                                          scope='AvgPool_1a_8x8')
                    net = slim.flatten(net)

                    net = slim.dropout(net, dropout_keep_prob, is_training=is_training,
                                       scope='Dropout')

                    end_points['PreLogitsFlatten'] = net

                net = slim.fully_connected(net, bottleneck_layer_size, activation_fn=None,
                        scope='Bottleneck', reuse=False)
                print("after fully_connected ",net.get_shape().as_list())
    return net, end_points

