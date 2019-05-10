"""
This module includes functions which implement mathemtical operations that are
useful for the study and implementation of Neural Networks

Each function includes a detailed descript of what the function does, how to call the function
and what it's inputs and outputs are
"""

import numpy as np


def sigmoid(x):
    """ Calculates the sigmoid function for a given value

    x:      (numpy array): If passed a vector will calculate the sigmoid for each element of the vector
    return: (numpy array)
    """

    return np.array(1 / (1 + np.exp(-np.array(x))));
