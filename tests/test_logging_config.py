import unittest

from machine_common_sense import LoggingConfig


class TestLoggingConfig(unittest.TestCase):
    def test_logging_config(self):
        cfg = LoggingConfig.get_configurable_logging_config(
            'INFO', ['l1', 'l2'], False, False, True, root_log_level='ERROR')
        root = cfg['root']
        loggers = cfg['loggers']
        handlers = cfg['handlers']
        self.assertEqual(root['level'], 'ERROR')
        self.assertEqual(len(loggers), 2)
        self.assertEqual(len(handlers), 1)
        self.assertIn("l1", loggers)
        self.assertIn("l2", loggers)
        self.assertEqual(loggers['l1']['level'], 'INFO')
        self.assertEqual(loggers['l2']['level'], 'INFO')
        self.assertEqual(len(loggers['l1']['handlers']), 1)
        self.assertEqual(len(loggers['l2']['handlers']), 1)
        self.assertEqual(len(root['handlers']), 1)
        self.assertEqual(loggers['l1']['handlers'], ['info-file'])
        self.assertEqual(loggers['l1']['handlers'], ['info-file'])
        self.assertEqual(root['handlers'], ['info-file'])

    def test_logging_config2(self):
        cfg = LoggingConfig.get_configurable_logging_config(
            'ERROR', 'l1', True, True, False)
        root = cfg['root']
        loggers = cfg['loggers']
        handlers = cfg['handlers']
        self.assertEqual(root['level'], 'WARN')
        self.assertEqual(len(loggers), 1)
        self.assertEqual(len(handlers), 2)
        self.assertIn("l1", loggers)
        self.assertEqual(loggers['l1']['level'], 'ERROR')
        self.assertEqual(len(loggers['l1']['handlers']), 2)
        self.assertEqual(len(root['handlers']), 2)
        self.assertIn('console', loggers['l1']['handlers'])
        self.assertIn('console', root['handlers'])
        self.assertIn('debug-file', loggers['l1']['handlers'])
        self.assertIn('debug-file', root['handlers'])


if __name__ == '__main__':
    unittest.main()
