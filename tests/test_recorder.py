import json
import pathlib
import random
import unittest
from typing import Tuple

import PIL

from machine_common_sense.recorder import (BaseRecorder, ImageRecorder,
                                           JsonRecorder, VideoRecorder)


class ConcreteBaseRecorder(BaseRecorder):
    '''Test implementation of the BaseRecorder'''

    def _write(self):
        raise NotImplementedError


class TestBaseRecorder(unittest.TestCase):

    def setUp(self):
        self.recorder = ConcreteBaseRecorder()
        self.recorder.start()

    def tearDown(self):
        self.recorder.finish()

    def test_recording(self):
        '''Recorder automatically starts (i.e. becomes recording)'''
        self.assertTrue(self.recorder.recording)

    def test_thread(self):
        '''Thread should start automatically'''
        self.assertTrue(self.recorder._thread.is_alive())

    def test_queue_empty(self):
        '''No frames sitting in the queue'''
        self.assertTrue(self.recorder._queue.empty())

    def test_num_recorded(self):
        '''No frames have been written yet'''
        self.assertEqual(self.recorder.num_recorded, 0)

    def test_flush(self):
        '''Flushing an empty recorder queue should not be a problem'''
        self.recorder.flush()
        self.assertTrue(self.recorder._queue.empty())

    def test_empty_finish(self):
        '''wrap up the recorder without writing anything'''
        self.recorder.finish()
        self.assertFalse(self.recorder.recording)
        self.assertTrue(self.recorder._queue.empty())
        self.assertEqual(self.recorder.num_recorded, 0)


class TestJsonRecorder(unittest.TestCase):
    json_prefix = "test_json_"
    test_json_file = pathlib.Path("tests/test_json_{:04d}.json")

    def setUp(self):
        self.recorder = JsonRecorder(self.test_json_file)

    def tearDown(self):
        '''Delete all unit test output images'''
        for p in pathlib.Path('tests').glob('test_json_*'):
            p.unlink()

    def test_data(self, val=4):
        return {"test1": "t1", "obj": {"o1": "o2"},
                "arr": [1, 2, 3], "val": val}

    def test_write(self):
        output_file = pathlib.Path("tests/test_json_0000.json")
        data = self.test_data()
        self.recorder.add(data)
        self.recorder.finish()
        self.assertFalse(self.recorder.recording)
        self.assertEqual(self.recorder.num_recorded, 1)
        self.assertTrue(self.recorder._queue.empty())
        self.assertTrue(output_file.is_file())
        self.assertTrue(output_file.parent.is_dir())
        with open(output_file, 'r') as json_file:
            actual = json.load(json_file)
        self.assertEqual(actual, data)

    def test_multiple_write(self):
        output_file1 = pathlib.Path("tests/test_json_0000.json")
        output_file2 = pathlib.Path("tests/test_json_0001.json")
        output_file3 = pathlib.Path("tests/test_json_0002.json")
        data1 = self.test_data(1)
        data2 = self.test_data(2)
        data3 = self.test_data(3)
        self.recorder.add(data1)
        self.recorder.add(data2)
        self.recorder.add(data3)
        self.recorder.finish()
        self.assertFalse(self.recorder.recording)
        self.assertEqual(self.recorder.num_recorded, 3)
        self.assertTrue(self.recorder._queue.empty())
        self.assertTrue(output_file1.is_file())
        self.assertTrue(output_file1.parent.is_dir())
        with open(output_file1, 'r') as json_file:
            actual = json.load(json_file)
        self.assertEqual(actual, data1)
        with open(output_file2, 'r') as json_file:
            actual = json.load(json_file)
        self.assertEqual(actual, data2)
        with open(output_file3, 'r') as json_file:
            actual = json.load(json_file)
        self.assertEqual(actual, data3)

    def test_missing_folder(self):
        '''ImageRecorder requires existing path'''
        bad_recorder = JsonRecorder(
            pathlib.Path("missing/test_json_{:04d}.json"))
        bad_recorder.add(self.test_data())
        with self.assertRaises(FileNotFoundError):
            bad_recorder.finish()

    def test_add_after_finish(self):
        output_file = pathlib.Path("tests/test_json_0000.json")
        self.recorder.add(self.test_data())
        self.recorder.finish()
        self.assertFalse(self.recorder.recording)
        self.assertEqual(self.recorder.num_recorded, 1)
        self.assertTrue(self.recorder._queue.empty())
        self.assertTrue(output_file.is_file())
        self.assertTrue(output_file.parent.is_dir())
        self.recorder.add(self.test_data())
        self.assertTrue(self.recorder._queue.empty())


class TestImageRecorder(unittest.TestCase):
    image_prefix = "test_image_"
    test_image_file = pathlib.Path("tests/test_image_{:04d}.jpg")

    def setUp(self):
        self.recorder = ImageRecorder(self.test_image_file)

    def tearDown(self):
        '''Delete all unit test output images'''
        for p in pathlib.Path('tests').glob('test_image_*'):
            p.unlink()

    def random_color(self) -> Tuple:
        '''Create a random 8-bit RGB tuple'''
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return (r, g, b)

    def test_write(self):
        output_file = pathlib.Path("tests/test_image_0000.jpg")
        size = (50, 100)
        img = PIL.Image.new("RGB", size, self.random_color())
        self.recorder.add(img)
        self.recorder.finish()
        self.assertFalse(self.recorder.recording)
        self.assertEqual(self.recorder.num_recorded, 1)
        self.assertTrue(self.recorder._queue.empty())
        self.assertTrue(output_file.is_file())
        self.assertTrue(output_file.parent.is_dir())

    def test_write_png(self):
        '''ImageRecorder can save image sequences in png format'''
        png_format = pathlib.Path("tests/test_image_{:04d}.png")
        png_recorder = ImageRecorder(png_format)
        output_file = pathlib.Path("tests/test_image_0000.png")
        size = (50, 100)
        img = PIL.Image.new("RGB", size, self.random_color())
        png_recorder.add(img)
        png_recorder.finish()
        self.assertFalse(png_recorder.recording)
        self.assertEqual(png_recorder.num_recorded, 1)
        self.assertTrue(png_recorder._queue.empty())
        self.assertTrue(output_file.is_file())
        self.assertTrue(output_file.parent.is_dir())

    def test_multiple_write(self):
        output_file = pathlib.Path("tests/test_image_0000.jpg")
        size = (50, 100)
        img = PIL.Image.new("RGB", size, self.random_color())
        self.recorder.add(img)
        img = PIL.Image.new("RGB", size, self.random_color())
        self.recorder.add(img)
        img = PIL.Image.new("RGB", size, self.random_color())
        self.recorder.add(img)
        self.recorder.finish()
        self.assertFalse(self.recorder.recording)
        self.assertEqual(self.recorder.num_recorded, 3)
        self.assertTrue(self.recorder._queue.empty())
        self.assertTrue(output_file.is_file())
        self.assertTrue(output_file.parent.is_dir())

    def test_multiple_write_different_sizes(self):
        '''ImageRecorder can write different size images'''
        first_file = pathlib.Path("tests/test_image_0000.jpg")
        second_file = pathlib.Path("tests/test_image_0001.jpg")
        size = (50, 100)
        other_size = (100, 100)
        img = PIL.Image.new("RGB", size, self.random_color())
        self.recorder.add(img)
        img = PIL.Image.new("RGB", other_size, self.random_color())
        self.recorder.add(img)
        self.recorder.finish()
        self.assertFalse(self.recorder.recording)
        self.assertEqual(self.recorder.num_recorded, 2)
        self.assertTrue(self.recorder._queue.empty())
        self.assertTrue(first_file.is_file())
        self.assertTrue(second_file.is_file())

    def test_missing_folder(self):
        '''ImageRecorder requires existing path'''
        bad_recorder = ImageRecorder(
            pathlib.Path("missing/test_image_{:04d}.jpg"))
        size = (50, 100)
        img = PIL.Image.new("RGB", size, self.random_color())
        bad_recorder.add(img)
        with self.assertRaises(FileNotFoundError):
            bad_recorder.finish()

    def test_add_after_finish(self):
        output_file = pathlib.Path("tests/test_image_0000.jpg")
        size = (50, 100)
        img = PIL.Image.new("RGB", size, self.random_color())
        self.recorder.add(img)
        self.recorder.finish()
        self.assertFalse(self.recorder.recording)
        self.assertEqual(self.recorder.num_recorded, 1)
        self.assertTrue(self.recorder._queue.empty())
        self.assertTrue(output_file.is_file())
        self.assertTrue(output_file.parent.is_dir())
        self.recorder.add(img)
        self.assertTrue(self.recorder._queue.empty())


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

    def test_video_path(self):
        self.assertEqual(self.recorder.path, self.test_video_file)

    def test_fps(self):
        self.assertEqual(self.recorder.fps, self.fps)

    def test_default_fourcc(self):
        self.assertEqual(self.recorder.fourcc, 'mp4v')

    def test_video_writer_none(self):
        '''The actual writer is None until the first frame'''
        self.assertIsNone(self.recorder.writer)

    def test_add(self):
        size = (50, 100)
        img = PIL.Image.new("RGB", size)
        self.recorder.add(img)
        self.assertFalse(self.recorder._queue.empty())
        self.assertIsNotNone(self.recorder.writer)

    def test_add_flush(self):
        size = (50, 100)
        img = PIL.Image.new("RGB", size)
        self.recorder.add(img)
        self.recorder.add(img)
        self.recorder.add(img)
        self.assertFalse(self.recorder._queue.empty())
        self.recorder.flush()
        self.assertEqual(self.recorder.num_recorded, 3)
        self.assertTrue(self.recorder.recording)
        self.assertTrue(self.recorder._queue.empty())

    def test_finish(self):
        nframes = 100
        size = (50, 100)
        img = PIL.Image.new("RGB", size)
        for _ in range(nframes):
            self.recorder.add(img)
        self.recorder.finish()
        self.assertFalse(self.recorder.recording)
        self.assertTrue(self.recorder._queue.empty())
        self.assertEqual(self.recorder.num_recorded, nframes)

    def test_wrong_size_frame(self):
        # the first frame established the video recorder size
        size = (50, 100)
        img = PIL.Image.new("RGB", size)
        self.recorder.add(img)

        # any different sized frame will cause a ValueError exception
        wrong_size = (100, 100)
        wrong_size_img = PIL.Image.new("RGB", wrong_size, color='red')
        with self.assertRaises(ValueError):
            self.recorder.add(wrong_size_img)

        self.recorder.finish()
        self.assertFalse(self.recorder.recording)
        self.assertTrue(self.recorder._queue.empty())
        self.assertEqual(self.recorder.num_recorded, 1)


if __name__ == '__main__':
    unittest.main()
