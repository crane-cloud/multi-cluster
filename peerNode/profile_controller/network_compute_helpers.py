import numpy as np
from scipy import stats


# 90, 95 and 99
def get_percentiles(array_values,nth):
    return np.percentile(array_values,nth)

def get_modal(array_values):
    array = np.array(array_values)
    mode = stats.mode(array,keepdims=True)
    print("Modal mark is: ", mode.mode[0])

def get_average(array_values):
    array = np.array(array_values)
    # print("Average mark is: ", np.average(array))
    return np.average(array)
