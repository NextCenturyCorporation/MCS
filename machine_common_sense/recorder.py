import time
import pathlib
import threading
import queue

import cv2
import PIL
import numpy as np


class VideoRecorder():
    '''Threaded video recorder'''

    def __init__(self,
                 vid_path: pathlib.Path,
                 width: int,
                 height: int,
                 fps: int,
                 fourcc: str = 'mp4v',
                 timeout: float = 1.0):
        '''Create the video recorder.

        Args:
            vid_path (pathlib.path): the output video file path
            width (int): video width dimension
            height (int): video height dimension
            fps (int): video frame rate per second
            fourcc (str): opencv fourcc value
            timeout (float): thread sleep timeout

        Returns:
            None
        '''

        self.Q = None
        self.thread = None
        self.started = False
        self.timeout = timeout
        self.path = vid_path
        self.writer = cv2.VideoWriter(str(vid_path),
                                      cv2.VideoWriter_fourcc(*fourcc),
                                      fps,
                                      (width, height),
                                      True)
        self.start()

    def start(self) -> None:
        '''Create the video recorder thread and start the frame queue.'''
        self.active = True
        self.Q = queue.Queue()
        self.thread = threading.Thread(target=self._write, args=())
        self.thread.daemon = True
        self.thread.start()

    def add(self, frame: PIL.Image.Image) -> None:
        '''Adds the video frame to the queue.

        Requires that the start function was called
        otherwise the frame is ignored.

        Args:
            frame (np.ndarray): RGB video frame to be written

        Returns:
            None
        '''
        if self.active:
            # convert BGR image to RGB for opencv
            cv_frame = np.array(frame.convert('RGB'))[:, :, ::-1]
            self.Q.put(cv_frame)

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
        '''Deactivate the recorder so that it does not accept more frames.

        Frames that remain in the buffer will be written and the recorder
        closed.
        '''
        self.active = False
        self.thread.join()
        self.flush()
        self.writer.release()

    @property
    def path(self):
        return self.vid_path
