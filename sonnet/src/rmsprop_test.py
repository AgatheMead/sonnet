# Copyright 2019 The Sonnet Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or  implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

"""Tests for sonnet.v2.src.rmsprop."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import parameterized
from sonnet.src import rmsprop
from sonnet.src import test_utils
import tensorflow as tf


# TODO(petebu) Add tests for tf.function with/without autograph.


class RMSPropTest(test_utils.TestCase, parameterized.TestCase):

  @parameterized.parameters(rmsprop.RMSProp, rmsprop.FastRMSProp)
  def testDense(self, opt_class):
    parameters = [tf.Variable([1., 2.]), tf.Variable([3., 4.])]
    updates = [tf.constant([5., 5.]), tf.constant([3., 3.])]
    optimizer = opt_class(learning_rate=0.1)
    # Step 1 of RMSProp
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.683772, 1.683772], [2.683772, 3.683772]],
                        [x.numpy() for x in parameters])
    # Step 2 of RMSProp
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.454357, 1.454357], [2.454357, 3.454357]],
                        [x.numpy() for x in parameters])
    # Step 3 of RMSProp
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.262262, 1.262262], [2.262262, 3.262262]],
                        [x.numpy() for x in parameters])

  @parameterized.parameters(rmsprop.RMSProp, rmsprop.FastRMSProp)
  def testDenseCentered(self, opt_class):
    parameters = [tf.Variable([1., 2.]), tf.Variable([3., 4.])]
    updates = [tf.constant([5., 5.]), tf.constant([3., 3.])]
    optimizer = opt_class(learning_rate=0.1, centered=True)
    # Step 1 of RMSProp
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.666667, 1.666667], [2.666667, 3.666667]],
                        [x.numpy() for x in parameters])
    # Step 2 of RMSProp
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.41176, 1.41176], [2.41176, 3.41176]],
                        [x.numpy() for x in parameters])
    # Step 3 of RMSProp
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.186776, 1.186776], [2.186776, 3.186776]],
                        [x.numpy() for x in parameters])

  @parameterized.parameters(rmsprop.RMSProp, rmsprop.FastRMSProp)
  def testSparse(self, opt_class):
    if self.primary_device in ("GPU", "TPU"):
      self.skipTest("IndexedSlices not supported on {}.".format(
          self.primary_device))

    parameters = [tf.Variable([[1.], [2.]]), tf.Variable([[3.], [4.]])]
    updates = [tf.IndexedSlices(tf.constant([0.1], shape=[1, 1]),
                                tf.constant([0]), tf.constant([2, 1])),
               tf.IndexedSlices(tf.constant([0.01], shape=[1, 1]),
                                tf.constant([1]), tf.constant([2, 1]))]
    optimizer = opt_class(learning_rate=3.)
    # Step 1 of RMSProp
    optimizer.apply(updates, parameters)
    self.assertAllClose([[-8.486831], [2.0]], parameters[0].numpy())
    self.assertAllClose([[3.0], [-5.486784]], parameters[1].numpy())
    # Step 2 of RMSProp
    optimizer.apply(updates, parameters)
    self.assertAllClose([[-15.369301], [2.0]], parameters[0].numpy())
    self.assertAllClose([[3.0], [-12.369237]], parameters[1].numpy())
    # Step 3 of RMSProp
    optimizer.apply(updates, parameters)
    self.assertAllClose([[-21.132141], [2.0]], parameters[0].numpy())
    self.assertAllClose([[3.0], [-18.132067]], parameters[1].numpy())

  @parameterized.parameters(rmsprop.RMSProp, rmsprop.FastRMSProp)
  def testSparseCentered(self, opt_class):
    if self.primary_device in ("GPU", "TPU"):
      self.skipTest("IndexedSlices not supported on {}.".format(
          self.primary_device))

    parameters = [tf.Variable([[1.], [2.]]), tf.Variable([[3.], [4.]])]
    updates = [tf.IndexedSlices(tf.constant([0.1], shape=[1, 1]),
                                tf.constant([0]), tf.constant([2, 1])),
               tf.IndexedSlices(tf.constant([0.01], shape=[1, 1]),
                                tf.constant([1]), tf.constant([2, 1]))]
    optimizer = opt_class(learning_rate=3., centered=True)
    # Step 1 of RMSProp
    optimizer.apply(updates, parameters)
    self.assertAllClose([[-8.999999], [2.0]], parameters[0].numpy())
    self.assertAllClose([[3.0], [-5.999944]], parameters[1].numpy())
    # Step 2 of RMSProp
    optimizer.apply(updates, parameters)
    self.assertAllClose([[-16.64719], [2.0]], parameters[0].numpy())
    self.assertAllClose([[3.0], [-13.647109]], parameters[1].numpy())
    # Step 3 of RMSProp
    optimizer.apply(updates, parameters)
    self.assertAllClose([[-23.396709], [2.0]], parameters[0].numpy())
    self.assertAllClose([[3.0], [-20.39661]], parameters[1].numpy())

  @parameterized.parameters(rmsprop.RMSProp, rmsprop.FastRMSProp)
  def testNoneUpdate(self, opt_class):
    parameters = [tf.Variable([1., 2.])]
    updates = [None]
    optimizer = opt_class(learning_rate=0.1)
    optimizer.apply(updates, parameters)
    self.assertAllClose([[1., 2.]], [x.numpy() for x in parameters])

  @parameterized.parameters(rmsprop.RMSProp, rmsprop.FastRMSProp)
  def testVariableHyperParams(self, opt_class):
    parameters = [tf.Variable([1., 2.]), tf.Variable([3., 4.])]
    updates = [tf.constant([5., 5.]), tf.constant([3., 3.])]
    learning_rate = tf.Variable(0.1)
    optimizer = opt_class(learning_rate=learning_rate)
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.683772, 1.683772], [2.683772, 3.683772]],
                        [x.numpy() for x in parameters])
    learning_rate.assign(0.01)
    self.assertAlmostEqual(0.01, optimizer.learning_rate.numpy())
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.660831, 1.660831], [2.660831, 3.660831]],
                        [x.numpy() for x in parameters])

  @parameterized.parameters(rmsprop.RMSProp, rmsprop.FastRMSProp)
  def testHyperParamDTypeConversion(self, opt_class):
    parameters = [tf.Variable([1., 2.]), tf.Variable([3., 4.])]
    updates = [tf.constant([5., 5.]), tf.constant([3., 3.])]
    dtype = tf.float32 if self.primary_device == "TPU" else tf.float64
    learning_rate = tf.Variable(0.1, dtype=dtype)
    decay = tf.Variable(0.9, dtype=dtype)
    momentum = tf.Variable(0.0, dtype=dtype)
    epsilon = tf.Variable(1e-7, dtype=dtype)
    optimizer = opt_class(learning_rate=learning_rate, decay=decay,
                          momentum=momentum, epsilon=epsilon)
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.683772, 1.683772], [2.683772, 3.683772]],
                        [x.numpy() for x in parameters])

  @parameterized.parameters(rmsprop.RMSProp, rmsprop.FastRMSProp)
  def testDifferentLengthUpdatesParams(self, opt_class):
    parameters = [tf.Variable([1., 2.]), tf.Variable([3., 4.])]
    updates = [tf.constant([5., 5.])]
    optimizer = opt_class(learning_rate=0.1)
    with self.assertRaisesRegexp(
        ValueError, "`updates` and `parameters` must be the same length."):
      optimizer.apply(updates, parameters)

  @parameterized.parameters(rmsprop.RMSProp, rmsprop.FastRMSProp)
  def testEmptyParams(self, opt_class):
    optimizer = opt_class(learning_rate=0.1)
    with self.assertRaisesRegexp(ValueError, "`parameters` cannot be empty."):
      optimizer.apply([], [])

  @parameterized.parameters(rmsprop.RMSProp, rmsprop.FastRMSProp)
  def testInconsistentDTypes(self, opt_class):
    parameters = [tf.Variable([1., 2.], name="param0")]
    updates = [tf.constant([5, 5])]
    optimizer = opt_class(learning_rate=0.1)
    with self.assertRaisesRegexp(
        ValueError, "DType of .* is not equal to that of parameter .*param0.*"):
      optimizer.apply(updates, parameters)

  @parameterized.parameters(rmsprop.RMSProp, rmsprop.FastRMSProp)
  def testMovingVariablesColocatedWithOriginal(self, opt_class):
    optimizer = opt_class(learning_rate=0.1)
    with tf.device("CPU:0"):
      var = tf.Variable(1.0)
    optimizer.apply([tf.constant(0.1)], [var])
    self.assertEqual(optimizer.mom[0].device, var.device)
    self.assertEqual(optimizer.ms[0].device, var.device)

  @parameterized.parameters(rmsprop.RMSProp, rmsprop.FastRMSProp)
  def testUnsuppportedStrategyError(self, opt_class):
    strategy = tf.distribute.MirroredStrategy()
    with strategy.scope():
      var = tf.Variable(1.0)
      optimizer = opt_class(learning_rate=0.1)
    step = lambda: optimizer.apply([tf.constant(0.1)], [var])
    with self.assertRaisesRegexp(
        ValueError,
        "Sonnet optimizers are not compatible with `MirroredStrategy`"):
      strategy.experimental_run_v2(step)

if __name__ == "__main__":
  # tf.enable_v2_behavior()
  tf.test.main()
