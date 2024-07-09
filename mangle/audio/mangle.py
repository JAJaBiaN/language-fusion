import random
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample

SECONDS_BEFOREAFTER = 3

f_rate, f_data = wavfile.read('recordings_0_george_0.wav')
b_rate, b_data = wavfile.read('birds.wav')

# Work in floating point
out_dtype = f_data.dtype

if f_data.dtype.kind != 'f':
    f_min = np.iinfo(f_data.dtype).min
    f_max = np.iinfo(f_data.dtype).max
    f_data = f_data.astype(np.float64)
    f_data = (f_data - f_min) / (f_max - f_min) * 2 - 1

if b_data.dtype.kind != 'f':
    b_min = np.iinfo(b_data.dtype).min
    b_max = np.iinfo(b_data.dtype).max
    b_data = b_data.astype(np.float64)
    b_data = (b_data - b_min) / (b_max - b_min) * 2 - 1

# Ensure both are mono
if f_data.ndim > 1:
    f_data = f_data.sum(axis=1) / 2
if b_data.ndim > 1:
    b_data = b_data.sum(axis=1) / 2

# Resample background to foreground rate
b_data = resample(b_data, int(f_rate/b_rate*len(b_data)))

# Randomly position foreground sound on background track
samples_beforeafter = int(SECONDS_BEFOREAFTER * f_rate + 0.5)

pad_len = len(b_data) - len(f_data)
pad_offset = random.randint(samples_beforeafter, pad_len-samples_beforeafter)

f_data_len = len(f_data)
f_data = np.pad(f_data, (pad_offset, (pad_len-pad_offset)), 'constant', constant_values=0)

# Sum foreground and background tracks
out_data = f_data*1 + b_data*2

# Trim down resulting track
start = pad_offset - samples_beforeafter
end = pad_offset + f_data_len + samples_beforeafter
out_data = out_data[start:end]

# Save in same type as input
out_data = (out_data + 1) / 2 * (f_max - f_min) + f_min
out_data = out_data.astype(out_dtype)

wavfile.write('recordings_0_george_0_out.wav', f_rate, out_data)
