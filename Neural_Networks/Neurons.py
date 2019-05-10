"""
This file contains implementations for different types of neurons
Neurons have a standard implementation

Each Neuron consists of a forward and backward pass so that they can be used with the back propagation algorithm
"""

import numpy as np


class Preceptron(object):
    """
    This is the simplist class of Neuron.
    Here we take the dot product of the inputs and the weights

    If the dot product is greater than bias then the neuron outputs a 1
    If the dot product is less then the bias then the neuron outputs a 0
    """

    def __init__(self, size, weights=None, bias=None):
        """
        We can initalise the weights and the bias with saved values
        otherwise the weights are given a random value between 1 and -1

        size    (int):         This is the number of inputs to the neuron
        weights (numpy array): If specified the weights will be initialised these values
        bias    (numpy array): If specified the bias will be initialised to this value
        """

        self._size = size
        self._weights = weights
        self._bias = bias

        # randomly initalise weights if not declared
        if not self._weights:
            self._weights = np.random.uniform(-1.0, 1.0, self._size)

        # randomly initalise bias if not declared
        if not self._bias:
            self._bias = np.random.uniform(-1.0, 1.0, 1)

        # confirm that the shape of the wights vector is correct
        assert len(self._weights.shape) == 1
        assert self._weights.size == self._size


    def get_output(self, inputs):
        """ Calculates the output of the perceptron neuron given the inputs

        inputs (numpy array): The inputs to the neuron must be the same size as the weights
        """

        # check the dimensions of the neurons are correct
        assert len(inputs.shape) == 1
        assert inputs.size == self._size

        dot_product = np.dot(inputs, self._weights)

        if dot_product < self._bias:
            return np.array([0.0])
        else:
            return np.array([1.0])


x = Preceptron(4)
print x.get_output(np.random.uniform(0, 10, 4))
