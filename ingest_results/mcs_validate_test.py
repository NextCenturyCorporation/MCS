import unittest
import os
from mcs_validate import MCSEval1Validator
from pathlib import Path


class MyTestCase(unittest.TestCase):
    """
    Run some unit tests to make sure that we are parsing / testing the validator correctly.

    Note that since this is using unittest, that the working directory is a subdirectory that
    this file exists in, so you have to go up a directory to find the submissions
    """

    def test_voe(self):
        v = MCSEval1Validator()
        output = v.parse_voe(Path("../submissions/voe_O3_0301_4.txt"))
        self.assertEqual(output, True)

    def test_voe(self):
        v = MCSEval1Validator()
        output = v.parse_voe(Path("../submissions/voe_wrong_num.txt"))
        self.assertEqual(output, False)

    def test_location(self):
        v = MCSEval1Validator()
        output = v.parse_location(Path("../submissions/location.txt"))
        self.assertEqual(output, True)

    def test_location_mask_out_of_range(self):
        v = MCSEval1Validator()
        output = v.parse_location(Path("../submissions/location_mask_out_of_range.txt"))
        self.assertEqual(output, False)

    def test_read_description(self):
        v = MCSEval1Validator()
        output = v.parse_description(Path("../submissions/description.json"))
        self.assertEqual(output, True)

    def test_description_no_performer(self):
        v = MCSEval1Validator()
        output = v.parse_description(Path("../submissions/description_no_performer.json"))
        self.assertEqual(output, False)

    def test_description_bad_json(self):
        v = MCSEval1Validator()
        output = v.parse_description(Path("../submissions/description_bad_json.json"))
        self.assertEqual(output, False)

    def test_nosuchfile(self):
        v = MCSEval1Validator()
        output = v.validate("../submissions/blah")
        self.assertEqual(output, False)

    def test_emptyfile(self):
        v = MCSEval1Validator()
        output = v.validate("")
        self.assertEqual(output, False)

    def test_doesntendwithzip(self):
        v = MCSEval1Validator()
        output = v.validate("../submissions/submission_invalid_not_zip_ending")
        self.assertEqual(output, False)

    def test_invalidzip(self):
        v = MCSEval1Validator()
        output = v.validate("../submissions/submission_bad_zip.zip")
        self.assertEqual(output, False)

    def test_passes(self):
        v = MCSEval1Validator()
        output = v.validate("../submissions/submission_valid.zip")
        self.assertEqual(output, True)


if __name__ == '__main__':
    unittest.main()
