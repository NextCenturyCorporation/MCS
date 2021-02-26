import os
import time
import pathlib
import shutil
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
            fourcc (str): opencv fourcc / codec string
            timeout (float): thread sleep timeout

        Returns:
            None
        '''

        self.frame_queue = None
        self.thread = None
        self.started = False
        self.timeout = timeout
        self._path = vid_path
        self._frames_written = 0
        self.writer = cv2.VideoWriter(str(vid_path),
                                      cv2.VideoWriter_fourcc(*fourcc),
                                      fps,
                                      (width, height),
                                      True)
        self.start()

    def start(self) -> None:
        '''Create the video recorder thread and start the frame queue.'''
        self.active = True
        self.frame_queue = queue.Queue()
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
            # convert BGR PIL image to RGB for opencv
            cv_frame = np.array(frame.convert('RGB'))[:, :, ::-1]
            self.frame_queue.put(cv_frame)

    def _write(self) -> None:
        '''Loop forever waiting for frames to enter the queue.'''
        while True:
            if not self.active:
                return
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                self.writer.write(frame)
                self._frames_written = self._frames_written + 1
            else:
                time.sleep(self.timeout)

    def flush(self) -> None:
        '''Write the remaining video frames in the the queue.'''
        while not self.frame_queue.empty():
            frame = self.frame_queue.get()
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

        if self._frames_written > 0:
            # convert video to use h264 codec for browser playing
            # which is not usable directly from opencv
            shutil.move(self._path, 'temp.mp4')
            os.system(
                f'ffmpeg -loglevel quiet -i temp.mp4'
                f' -vcodec libx264 -vf format=yuv420p {self._path}')
            os.remove('temp.mp4')
        else:
            # Remove the unused video file without any frames.
            os.remove(self._path)

    @property
    def path(self) -> pathlib.Path:
        return self._path
