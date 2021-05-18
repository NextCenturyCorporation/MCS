import unittest
import pathlib
import PIL
import random

from typing import Tuple

from machine_common_sense.recorder import VideoRecorder
from machine_common_sense.recorder import ImageRecorder


class TestImageRecorder(unittest.TestCase):
    test_image_file = pathlib.Path("tests/test{:04d}.jpg")

    def setUp(self):
        self.recorder = ImageRecorder(self.test_image_file)

    def tearDown(self):
        for p in pathlib.Path('tests').glob('test*.jpg'):
            p.unlink()

    def random_color(self) -> Tuple:
        '''Create a random 8-bit RGB tuple'''
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return (r, g, b)

    def test_write(self):
        size = (50, 100)
        img = PIL.Image.new("RGB", size, self.random_color())
        self.recorder.add(img)
        self.recorder.flush()
        self.recorder.finish()

    def test_multiple_write(self):
        size = (50, 100)
        img = PIL.Image.new("RGB", size, self.random_color())
        self.recorder.add(img)
        img = PIL.Image.new("RGB", size, (255, 0, 0))  # self.random_color())
        self.recorder.add(img)
        img = PIL.Image.new("RGB", size, (0, 255, 0))  # self.random_color())
        self.recorder.add(img)
        self.recorder.flush()
        self.recorder.finish()

    # what happens if the path doesn't exist


class TestVideoRecorder(unittest.TestCase):

    test_video_file = pathlib.Path('tests/test.mp4')
    fps = 30

    def setUp(self):
        self.recorder = VideoRecorder(
            vid_path=self.test_video_file,
            fps=self.fps
        )

    def tearDown(self):
        if self.test_video_file.exists():
            self.test_video_file.unlink()

    def test_active(self):
        '''Recorder automatically starts (i.e. becomes active)'''
        self.assertTrue(self.recorder.active)

    def test_thread(self):
        '''Thread should start automatically'''
        self.assertTrue(self.recorder.thread.is_alive())

    def test_video_path(self):
        self.assertEqual(self.recorder.path, self.test_video_file)

    def test_fps(self):
        self.assertEqual(self.recorder.fps, self.fps)

    def test_default_fourcc(self):
        self.assertEqual(self.recorder.fourcc, 'mp4v')

    def test_queue_empty(self):
        '''No frames sitting in the queue'''
        self.assertTrue(self.recorder.frame_queue.empty())

    def test_frames_written(self):
        '''No frames have been written yet'''
        self.assertEqual(self.recorder._frames_written, 0)

    def test_video_writer_none(self):
        '''The actual writer is None until the first frame'''
        self.assertIsNone(self.recorder.writer)

    def test_flush(self):
        '''Flushing an empty recorder queue should not be a problem'''
        self.recorder.flush()
        self.assertTrue(self.recorder.frame_queue.empty())

    def test_add(self):
        size = (50, 100)
        img = PIL.Image.new("RGB", size)
        self.recorder.add(img)
        self.assertFalse(self.recorder.frame_queue.empty())
        self.assertIsNotNone(self.recorder.writer)

    def test_add_flush(self):
        size = (50, 100)
        img = PIL.Image.new("RGB", size)
        self.recorder.add(img)
        self.recorder.add(img)
        self.recorder.add(img)
        self.assertFalse(self.recorder.frame_queue.empty())
        self.recorder.flush()
        self.assertEqual(self.recorder._frames_written, 3)

    def test_finish(self):
        nframes = 100
        size = (50, 100)
        img = PIL.Image.new("RGB", size)
        for _ in range(nframes):
            self.recorder.add(img)
        self.recorder.finish()
        self.assertFalse(self.recorder.active)
        self.assertTrue(self.recorder.frame_queue.empty())
        self.assertEqual(self.recorder._frames_written, nframes)

    def test_empty_finish(self):
        nframes = 0
        # wrap up the recorder without writing any frames
        self.recorder.finish()
        self.assertFalse(self.recorder.active)
        self.assertIsNone(self.recorder.writer)
        self.assertTrue(self.recorder.frame_queue.empty())
        self.assertEqual(self.recorder._frames_written, nframes)

    def test_wrong_size_frame(self):
        # the first frame established the video recorder size
        size = (50, 100)
        img = PIL.Image.new("RGB", size)
        self.recorder.add(img)

        # any different sized frame will cause a ValueError exception
        wrong_size = (100, 100)
        wrong_size_img = PIL.Image.new("RGB", wrong_size, color='red')
        self.assertRaises(ValueError, self.recorder.add, wrong_size_img)

        self.recorder.finish()
        self.assertFalse(self.recorder.active)
        self.assertTrue(self.recorder.frame_queue.empty())
        self.assertEqual(self.recorder._frames_written, 1)


if __name__ == '__main__':
    unittest.main()
