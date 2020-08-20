import numpy as np
import pickle

with open('test.txt', 'rb') as f:

    packed = pickle.load(f)
    
    X = packed[0]
    Ye = packed[1]
    Zs = packed[2]
    Zp = packed[3]
    
print('test')