import os
import shutil
import random
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample

SECONDS_BEFOREAFTER = 3
BG_FILES = ['birds.wav', 'alerts.wav', 'traffic.wav']
BG_VOLS = {
    'birds.wav': 1.8,
    'alerts.wav': 0.1,
    'traffic.wav': 1.8
}

data_dir = os.fsencode("../../audio")

for file in BG_FILES:
    basename = os.path.splitext(file)[0]
    if not os.path.exists(basename):
        os.makedirs(basename)

for num in os.listdir(data_dir):
    if os.fsdecode(num)[0] == '.':
        continue

    if not os.fsdecode(num).startswith("veri_set_"):
        continue

    for fg_name in os.listdir(os.path.join(data_dir, num)):
        if os.fsdecode(fg_name)[0] == '.':
            continue

        _fg_name = os.fsdecode(fg_name)
        _num = os.fsdecode(num)

        for file in BG_FILES:
            basename = os.path.splitext(file)[0]
            if not os.path.exists(f"{basename}/{_num}"):
                os.makedirs(f"{basename}/{_num}")

            if not _fg_name.lower().endswith(".wav"):
                print(f"Copy '{_fg_name}'")
                shutil.copyfile(os.path.join(data_dir, num, fg_name), f"{basename}/{_num}/{_fg_name}")

        if not _fg_name.lower().endswith(".wav"):
            continue

        print(_fg_name + ':')

        f_rate, f_data = wavfile.read(os.path.join(data_dir, num, fg_name))
        out_dtype = f_data.dtype

        for file in BG_FILES:
            print(f"- {file}")
            basename = os.path.splitext(file)[0]

            b_rate, b_data = wavfile.read(file)

            # Work in floating point
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

            # Randomly position foreground sound on background track
            samples_beforeafter = int(SECONDS_BEFOREAFTER * f_rate + 0.5)
            b_samplelen = len(f_data) + 2*samples_beforeafter

            b_origsamplelen = int(b_samplelen * (b_rate/f_rate))
            b_offset = random.randint(0, len(b_data) - b_origsamplelen)
            b_data = b_data[b_offset:b_offset+b_origsamplelen]

            # Resample background to foreground rate
            b_data = resample(b_data, b_samplelen)

            pad_len = len(b_data) - len(f_data)

            f_data_len = len(f_data)
            out_data = np.pad(f_data, (pad_len//2, pad_len//2 + pad_len%2), 'constant', constant_values=0)

            # Sum foreground and background tracks
            out_data = out_data*1 + b_data*BG_VOLS[file]
            out_data = np.clip(out_data, -1, 1)

            # Save in same type as input
            out_data = (out_data + 1) / 2 * (f_max - f_min) + f_min
            out_data = out_data.astype(out_dtype)

            wavfile.write(f"{basename}/{_num}/{_fg_name}", f_rate, out_data)
