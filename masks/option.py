import time
import argparse
import os


def make(parser):
    """Build the opt namespace used for training

    parser: parser object used to build opt
    """

    parser.add_argument("--dir", default=".", help="Directory that has the data in it.")

    opt = parser.parse_args()

    return opt
