import numpy as np

import tensorflow as tf
import model
import text_loader
from frostings.loader import *
from gen_dummy_data import get_batch

with tf.Session() as sess:
    # list of sequences' length
    seq_lens = tf.placeholder(tf.int32, name='seq_lengths')

    X = tf.placeholder(tf.int32, shape=[None, 25], name='input')
    t = tf.placeholder(tf.int32, shape=[None, 25], name='target_truth')
    X_lengths = tf.placeholder(tf.int32, shape=[None])
    t_mask = tf.placeholder(tf.float32, shape=[None, 25])

    # predict
    output_logits = model.inference(
                  alphabet_size=200,
                  input=X,
                  input_lengths=X_lengths,
                  target=t)

    loss = model.loss(output_logits, t, t_mask)

    train_op = model.training(loss, learning_rate=0.01)

    # initialize parameters
    tf.initialize_all_variables().run()

    text_load_method = text_loader.TextLoadMethod()
    sample_info = SampleInfo(len(text_load_method.samples))
    sample_gen = SampleGenerator(text_load_method, sample_info)
    batch_info = BatchInfo(batch_size=32)
    text_batch_gen = text_loader.TextBatchGenerator(sample_gen, batch_info)

    for i, (batch, batch_size) in enumerate(text_batch_gen.gen_batch()):
        feed_dict = {X: batch['x_encoded'],
                     t: batch['t_encoded'],
                     X_lengths: batch['x_len'],
                     t_mask: batch['t_mask']}
        res = sess.run([loss, train_op],
                       feed_dict=feed_dict)

        # if i % 10 == 0:
        print 'Iteration %i Loss: %f' % (i, np.mean(res[0]))
