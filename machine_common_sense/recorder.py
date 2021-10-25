import json
import logging
import pathlib
import queue
import threading
import time
from abc import ABC, abstractmethod
from typing import Any

import cv2
import numpy as np
import PIL

logger = logging.getLogger(__name__)


class BaseRecorder(ABC):
    '''BaseRecorder class provides common functionality for all recorders.

    The abstract class handles the thread writing and item storage queue.
    '''

    _queue = None
    _thread = None
    num_recorded = 0
    recording = False

    def __init__(self, timeout: float = 1.0):
        self.timeout = timeout

    def start(self):
        '''Start the recorder.

        Prepares the queue for item storage and starts the write thread.
        '''
        logger.debug("Starting recorder")
        self.recording = True
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self.write, args=())
        self._thread.daemon = True
        self._thread.start()

    def flush(self) -> None:
        '''Write every item currently in the queue'''
        while not self._queue.empty():
            logger.debug("Flushing recorder queue")
            item = self._queue.get()
            self._write(item)
            self.num_recorded = self.num_recorded + 1

    def finish(self) -> None:
        '''Flush and close the recorder thread

        Further recordings should use a new recorder instance.
        '''
        logger.debug("Closing recorder")
        self.recording = False
        self.flush()
        self._thread.join()

    def write(self) -> None:
        '''Thread loop waiting for frames to enter the queue.'''
        if not self.recording:
            logger.warning("Recorder inactive. Unable to start thread.")
            return

        while True:
            if not self.recording:
                logger.debug("Recorder going inactive")
                return
            if not self._queue.empty():
                item = self._queue.get()
                self._write(item)
                self.num_recorded = self.num_recorded + 1
                logger.debug(f"Recorder wrote {self.num_recorded} items")
            else:
                time.sleep(self.timeout)

    def add(self, item: Any) -> None:
        '''Adds an item to the queue

        Args:
            item (Any): Item to be stored in queue

        Return:
            None
        '''
        if self.recording:
            logger.debug("Adding item to recorder queue")
            self._queue.put(item)
            logger.debug(f"Queue size is approximately {self._queue.qsize()}")

    @abstractmethod
    def _write(self):
        '''Subclasses to provide writing specifics'''
        pass


class JsonRecorder(BaseRecorder):
    '''Threaded json recorder'''

    def __init__(self, json_template: pathlib.Path,
                 timeout: float = 1.0, sort_keys=True, indent=4):
        '''Create the json recorder.

        Args:
            json_template(pathlib.Path): Filename template
            timeout (float): How often in seconds to check the queue

        Returns:
            None
        '''
        self.path = json_template
        self.sort_keys = sort_keys
        self.indent = indent
        super().__init__(timeout)
        super().start()

    def _write(self, data: dict) -> None:
        '''Save the json to disk

        Args:
            data (dict): The data to record

        Returns:
            None
        '''
        json_file = str(self.path).format(self.num_recorded)
        logger.debug(f"Writing {json_file}")
        with open(json_file, 'w') as json_file:
            json.dump(
                data,
                json_file,
                sort_keys=self.sort_keys,
                indent=self.indent)


class ImageRecorder(BaseRecorder):
    '''Threaded image recorder

    '''

    def __init__(self,
                 img_template: pathlib.Path,
                 timeout: float = 1.0):
        '''Create the image recorder.

        Args:
            img_template(pathlib.Path): Filename template
            timeout (float): How often in seconds to check the queue

        Returns:
            None
        '''
        self.path = img_template
        super().__init__(timeout)
        super().start()

    def _write(self, image: PIL.Image.Image) -> None:
        '''Save the image to disk

        Args:
            image (Pil.Image.Image): The image to record

        Returns:
            None
        '''
        image_filename = str(self.path).format(self.num_recorded)
        logger.debug(f"Writing {image_filename}")
        image.save(image_filename)


class VideoRecorder(BaseRecorder):
    '''Threaded video recorder'''

    def __init__(self,
                 vid_path: pathlib.Path,
                 fps: int,
                 fourcc: str = 'mp4v',
                 timeout: float = 1.0):
        '''Create the video recorder.

        Args:
            vid_path (pathlib.path): the output video file path
            fps (int): video frame rate per second
            fourcc (str): opencv fourcc / codec string
            timeout (float): thread sleep timeout in seconds

        Returns:
            None
        '''
        self.path = vid_path
        self._frames_written = 0
        self.fourcc = fourcc
        self.fps = fps
        self.writer = None
        super().__init__(timeout)
        super().start()

    def add(self, frame: PIL.Image.Image) -> None:
        '''Adds the video frame to the queue.

        Requires that the start function was called
        otherwise the frame is ignored.

        Args:
            frame (PIL.Image.Image): RGB video frame to be written

        Returns:
            None

        Raises:
            ValueError: If frame is a different size from the initial
        '''

        if self.writer is None:
            self.width, self.height = frame.size
            logger.debug(
                f"Establishing video writer size"
                f"({self.width},{self.height}) from first frame")
            self.writer = cv2.VideoWriter(str(self.path),
                                          cv2.VideoWriter_fourcc(*self.fourcc),
                                          self.fps,
                                          (self.width, self.height),
                                          True)
        width, height = frame.size
        if (width, height) != (self.width, self.height):
            raise ValueError(f"Wrong size frame ({width}, {height}) for "
                             f"video writer ({self.width}, {self.height})")

        super().add(frame)

    def _write(self, frame: PIL.Image.Image) -> None:
        '''Write the frame to the video recording

        Args:
            frame (PIL.Image.Image): Image frame to be written

        Return:
            None
        '''
        # convert BGR PIL image to RGB for opencv video writer
        cv_frame = np.array(frame.convert('RGB'))[:, :, ::-1]
        logger.debug(f"Writing frame #{self.num_recorded} to {self.path}")
        self.writer.write(cv_frame)

    def finish(self) -> None:
        '''Deactivate the recorder so that it does not accept more frames.

        Frames that remain in the buffer will be written and the recorder
        closed.
        '''
        logger.debug("Closing video recorder")
        super().finish()
        if self.writer:
            self.writer.release()
