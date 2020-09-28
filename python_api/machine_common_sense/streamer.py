import time
import pathlib
import threading
import queue

import cv2
import numpy as np


class VideoStreamWriter():
    '''Threaded video writer'''

    def __init__(self,
                 vid_path: pathlib.Path,
                 width: int,
                 height: int,
                 fps: int,
                 fourcc: str = 'mp4v',
                 timeout: float = 1.0):
        '''
        Args:
          vid_path (pathlib.path): the output video file path
          width (int): video width dimension
          height (int): video height dimension
          fps (int): video frame rate per second
          fourcc (str): opencv fourcc value
          timeout (float): thread sleep timeout

        '''

        self.Q = None
        self.thread = None
        self.started = False
        self.timeout = timeout
        self.writer = cv2.VideoWriter(str(vid_path),
                                      cv2.VideoWriter_fourcc(*fourcc),
                                      fps,
                                      (width, height),
                                      True)

    def start(self) -> None:
        '''Create the writer thread and wait for frames.'''
        self.active = True
        self.Q = queue.Queue()
        self.thread = threading.Thread(target=self._write, args=())
        self.thread.daemon = True
        self.thread.start()

    def add(self, frame: np.ndarray) -> None:
        '''Adds the numpy array video frame to the output queue.

        Requires that the videowriter start function was called
        otherwise the frame is ignored.

        For a Pillow image, use np.asarray(img).

        An OpenCV image is already of time numpy.ndarray.

        args:
          frame: np.ndarray, video frame to be written
        '''

        # TODO address channel (RGB vs BGR) problem
        # assume RGB and make note of it in the docs
        if self.active:
            self.Q.put(frame)

    def _write(self) -> None:
        '''Loop forever waiting for frames to enter the queue.'''
        while True:
            if not self.active:
                return

            if not self.Q.empty():
                frame = self.Q.get()
                self.writer.write(frame)
            else:
                time.sleep(self.timeout)

    def flush(self) -> None:
        '''Write the remaining video frames in the the queue.'''
        while not self.Q.empty():
            frame = self.Q.get()
            self.writer.write(frame)

    def finish(self) -> None:
        '''Stop and flush.'''
        self.active = False
        self.thread.join()
        self.flush()
        self.writer.release()
