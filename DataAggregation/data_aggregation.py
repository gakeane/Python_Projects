"""
This script tests an approach for performing aggregation operations (i.e. max, min) on large datasets
In this case the datasets are too large to read into memory at once

We assume that the data is stored in a csv file
This corresponds to data stored in a relational database which will also be in tabular form
"""

import time
import psutil

import numpy as np
import pandas as pd
import multiprocessing as mp


CSV_FILE_NAME = ""
CHUNK_SIZE = 4 * 10e6

def read_csv_chunk():
    """
    The pandas module includes methods for reading from csv files
    These methods allow us to read in just a chunk of the file

    Note that it is not necessarily better to use a small chunk size
    We need to try different chunk sizes and see which gives the best performance
    In this case we are going to read in 40 million lines (4 x 10e7)
    """

    # This returns an iterator object which will return the file in chunks
    data_chunk_reader = pd.read_csv(CSV_FILE_NAME, chunksize=CHUNK_SIZE)


read_csv_chunk()
