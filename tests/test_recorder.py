import unittest
import pathlib
import PIL
import cv2

from machine_common_sense.recorder import VideoRecorder


class TestVideoRecorder(unittest.TestCase):

    test_video_file = pathlib.Path('test.mp4')
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
        self.assertEqual(
            int(self.recorder.writer.get(
                cv2.CAP_PROP_FRAME_WIDTH)), 50)
        self.assertEqual(
            self.recorder.writer.get(
                cv2.CAP_PROP_FRAME_HEIGHT), 100)

    def test_finish(self):
        self.recorder.finish()
        self.assertFalse(self.recorder.active)
        self.assertTrue(self.recorder.frame_queue.empty())


if __name__ == '__main__':
    unittest.main()
