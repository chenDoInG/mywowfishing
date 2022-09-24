import pyaudio
import math
import struct
import wave
import time
import os
from collections import deque
from datetime import datetime

Threshold = 70

SHORT_NORMALIZE = (1.0 / 32768.0)
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
swidth = 2

TIMEOUT_LENGTH = 1
PREPEND_LENGTH = 1

f_name_directory = r'records'


class Recorder:

    @staticmethod
    def rms(frame):
        count = len(frame) / swidth
        fmt = "%dh" % count
        shorts = struct.unpack(fmt, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)

        return rms * 1000

    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  output=True,
                                  frames_per_buffer=chunk)
        self.prev_audio = deque(maxlen=PREPEND_LENGTH * RATE // chunk)

    def record(self):
        print('Noise detected, recording beginning')
        rec = [b''.join(self.prev_audio)]
        current = time.time()
        end = time.time() + TIMEOUT_LENGTH

        while current <= end:

            try:
                data = self.stream.read(chunk, exception_on_overflow=False)
                if self.rms(data) >= Threshold:
                    end = time.time() + TIMEOUT_LENGTH
                current = time.time()
                rec.append(data)
            except Exception as e:
                print('record sound error!', e)
                return False
        # self.write(b''.join(rec))
        return True

    def write(self, recording):
        n_files = len(os.listdir(f_name_directory))

        filename = os.path.join(f_name_directory, '{}.wav'.format(n_files))

        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(recording)
        wf.close()
        print('Written to file: {}'.format(filename))
        print('Returning to listening')

    def listen(self, timeout=15):
        print('Listening beginning')
        stat_time = datetime.now()
        while (datetime.now() - stat_time).seconds < timeout:
            samples = self.stream.read(chunk, exception_on_overflow=False)
            self.prev_audio.append(samples)
            rms_val = self.rms(samples)
            if rms_val > Threshold:
                return self.record()


if __name__ == '__main__':
    record = Recorder()
    while True:
        record.listen()
