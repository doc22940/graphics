#Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the fscore metric."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import parameterized
import numpy as np
import tensorflow as tf

from tensorflow_graphics.nn.metric import fscore
from tensorflow_graphics.util import test_case


def random_tensor(tensor_shape):
  return np.random.uniform(low=0.0, high=1.0, size=tensor_shape)


def random_tensor_shape():
  tensor_size = np.random.randint(5) + 1
  return np.random.randint(1, 10, size=(tensor_size)).tolist()


class FscoreTest(test_case.TestCase):

  @parameterized.parameters(
      # Precision = 0.5, Recall = 0.25.
      ((0, 1, 1, 1, 1), (1, 1, 0, 0, 0), 2 * (0.5 * 0.25) / (0.5 + 0.25)),
      # Precision = 1, Recall = 1.
      ((0, 0, 0, 1, 1, 1, 0, 1), (0, 0, 0, 1, 1, 1, 0, 1), 1),
      # Precision = 0, Recall = 0.
      ((0, 1, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0), 0))
  def test_evaluate_preset(self, ground_truth, predictions, expected_iou):
    tensor_shape = random_tensor_shape()

    ground_truth_labels = np.tile(ground_truth, tensor_shape + [1])
    predicted_labels = np.tile(predictions, tensor_shape + [1])
    expected = np.tile(expected_iou, tensor_shape)

    result = fscore.evaluate(ground_truth_labels, predicted_labels)

    self.assertAllClose(expected, result)

  @parameterized.parameters(
      # Exception is raised since not all the value are binary.
      (r"0.* 0\.7.* 0", (0., 0.7, 0), (0., 1.0, 0.0)),
      (r"0\.3.* 1.* 0.*", (0., 1.0, 0), (0.3, 1.0, 0.0)),
      # Exception is raised since the ground truth labels are all zeros.
      ("Condition x > y did not hold", (0., 0, 0, 0), (1., 1, 0, 0)))
  def test_evaluate_invalid_argument_exception_raised(self, error_msg,
                                                      ground_truth,
                                                      predictions):
    with self.assertRaisesRegexp((tf.errors.InvalidArgumentError, ValueError),
                                 error_msg):
      self.evaluate(fscore.evaluate(ground_truth, predictions))

  @parameterized.parameters(
      ("Not all batch dimensions are broadcast-compatible.", (1, 5, 3), (4, 3)),
      ("Not all batch dimensions are broadcast-compatible.", (3, 4), (2, 4, 5)),
  )
  def test_evaluate_shape_exception_raised(self, error_msg, *shape):
    """Tests that the shape exception is raised."""
    self.assert_exception_is_raised(fscore.evaluate, error_msg, shape)

  @parameterized.parameters(
      ((1, 5, 3), (2, 5, 1)),
      ((None, 2, 6), (4, 2, None)),
      ((3, 1, 1, 2), (3, 5, 8, 2)),
  )
  def test_evaluate_shape_exception_not_raised(self, *shapes):
    """Tests that the shape exceptions are not raised."""
    self.assert_exception_is_not_raised(fscore.evaluate, shapes)


if __name__ == "__main__":
  test_case.main()
