import tensorflow as tf
from tensorflow.python.ops import tensor_array_ops
from utils.tfextensions import mask


def attention_decoder(attention_inputs, attention_lengths, initial_state, target_input,
                      target_input_lengths, num_attn_units, embeddings, W_out, b_out,
                      name='decoder', swap=False):
    """Decoder with attention.

    Note that the number of units in the attention decoder must always
    be equal to the size of the initial state/attention input.

    Keyword arguments:
        attention_input:    the input to put attention on. expected dims: [batch_size, attention_length, attention_dims]
        initial_state:      The initial state for the decoder RNN.
        target_input:       The target to replicate. Expected: [batch_size, max_target_sequence_len, embedding_dims]
        num_attn_units:     Number of units in the alignment layer that produces the context vectors.
    """
    with tf.variable_scope(name):
        h0_input = attention_inputs[0]
        h0_lengths = attention_lengths[0]
        h0_state = initial_state[0]
        target_dims = target_input.get_shape()[2]
        h0_dims = h0_input.get_shape()[2]
        num_units = h0_dims
        h0_len = tf.shape(h0_input)[1]
        max_sequence_length = tf.reduce_max(target_input_lengths)

        weight_initializer = tf.truncated_normal_initializer(stddev=0.1)
        W_z = tf.get_variable('W_z',
                              shape=[target_dims+num_units*2, num_units],
                              initializer=weight_initializer)
        W_r = tf.get_variable('W_r',
                              shape=[target_dims+num_units*2, num_units],
                              initializer=weight_initializer)
        W_h = tf.get_variable('W_h',
                              shape=[target_dims+num_units*2, num_units],
                              initializer=weight_initializer)
        b_z = tf.get_variable('b_z',
                              shape=[num_units],
                              initializer=tf.constant_initializer(1.0))
        b_r = tf.get_variable('b_r',
                              shape=[num_units],
                              initializer=tf.constant_initializer(1.0))
        b_h = tf.get_variable('b_h',
                              shape=[num_units],
                              initializer=tf.constant_initializer())

        # for attention
        W_a = tf.get_variable('W_a',
                              shape=[h0_dims, num_attn_units],
                              initializer=weight_initializer)
        U_a = tf.get_variable('U_a',
                              shape=[1, 1, h0_dims, num_attn_units],
                              initializer=weight_initializer)
        b_a = tf.get_variable('b_a',
                              shape=[num_attn_units],
                              initializer=tf.constant_initializer())
        v_a = tf.get_variable('v_a',
                              shape=[num_attn_units],
                              initializer=weight_initializer)

        # TODO: don't use convolutions!
        # TODO: fix the bias (b_a)
        hidden = tf.reshape(h0_input, tf.pack([-1, h0_len, 1, h0_dims]))
        part1 = tf.nn.conv2d(hidden, U_a, [1, 1, 1, 1], "SAME")
        part1 = tf.squeeze(part1, [2])  # squeeze out the third dimension

        inputs = tf.transpose(target_input, perm=[1, 0, 2])
        input_ta = tensor_array_ops.TensorArray(tf.float32, size=1, dynamic_size=True)
        input_ta = input_ta.unpack(inputs)

        def decoder_cond(time, state, output_ta_t, h0_tracker):
            return tf.less(time, max_sequence_length)

        def decoder_body_builder(feedback=False):
            def decoder_body(time, old_state, output_ta_t, h0_tracker):
                if feedback:
                    def from_previous():
                        prev_1 = tf.matmul(old_state, W_out) + b_out
                        return tf.gather(embeddings, tf.argmax(prev_1, 1))
                    x_t = tf.cond(tf.greater(time, 0), from_previous, lambda: input_ta.read(0))
                else:
                    x_t = input_ta.read(time)

                # attention
                part2 = tf.matmul(old_state, W_a) + b_a
                part2 = tf.expand_dims(part2, 1)
                john = part1 + part2
                e = tf.reduce_sum(v_a * tf.tanh(john), [2])
                alpha = tf.nn.softmax(e)
                alpha = tf.to_float(mask(h0_lengths)) * alpha
                alpha = alpha / tf.reduce_sum(alpha, [1], keep_dims=True)
                h0_tracker = h0_tracker.write(time, alpha)
                c = tf.reduce_sum(tf.expand_dims(alpha, 2) * tf.squeeze(hidden), [1])

                # GRU
                con = tf.concat(1, [x_t, old_state, c])
                z = tf.sigmoid(tf.matmul(con, W_z) + b_z)
                r = tf.sigmoid(tf.matmul(con, W_r) + b_r)
                con = tf.concat(1, [x_t, r*old_state, c])
                h = tf.tanh(tf.matmul(con, W_h) + b_h)
                new_state = (1-z)*h + z*old_state

                output_ta_t = output_ta_t.write(time, new_state)

                return (time + 1, new_state, output_ta_t, h0_tracker)
            return decoder_body


        output_ta = tensor_array_ops.TensorArray(tf.float32, size=1, dynamic_size=True)
        h0_tracker = tensor_array_ops.TensorArray(tf.float32, size=1, dynamic_size=True)
        time = tf.constant(0)
        loop_vars = [time, h0_state, output_ta, h0_tracker]

        _, state, output_ta, _ = tf.while_loop(decoder_cond,
                                            decoder_body_builder(),
                                            loop_vars,
                                            swap_memory=swap)
        _, valid_state, valid_output_ta, valid_h0_tracker = tf.while_loop(decoder_cond,
                                                        decoder_body_builder(feedback=True),
                                                        loop_vars,
                                                        swap_memory=swap)

        dec_state = state
        dec_out = tf.transpose(output_ta.pack(), perm=[1, 0, 2])
        valid_dec_out = tf.transpose(valid_output_ta.pack(), perm=[1, 0, 2])

        return dec_state, dec_out, valid_dec_out, valid_h0_tracker
