#!/usr/bin/env python
#
# author: Mathieu Bernard <mathieu.a.bernard@inria.fr>
"""Evaluation script for the Intuitive Physics Challenge

Execute the script as follow::

    ./score.py input_dir output_dir

The `input_dir` MUST HAVE the two subdirectories `res` and `ref` and
the files `res/answer.txt` and `ref/answer.txt`.

The `output_dir` MUST BE an existing directory. The file
`output_dir/scores.txt` will be created (or overwritted if existing;)

"""

import argparse
import collections
import os

import numpy as np
from sklearn.metrics import roc_auc_score


def _score_relative(submitted, reference):
    """Computes the relative error rate

    Equation 1 of https://arxiv.org/pdf/1803.07616.pdf

    """
    N = len(submitted)
    score = 0

    for scene in reference.keys():
        sub, ref = submitted[scene], reference[scene]
        pos, imp = 0, 0
        for k in ('1', '2', '3', '4'):
            if ref[k] == 1:  # possible movie
                pos += sub[k]
            else:  # impossible movie
                imp += sub[k]

        if pos < imp:  # increment the relative error score
            score += 1

    # cast to float in case we are running python2
    return float(score) / float(N)


def _score_absolute(submitted, reference):
    """Computes the absolute error rate

    Equation 2 of https://arxiv.org/pdf/1803.07616.pdf

    """
    y_true = np.asarray([
        y for k, v in sorted(reference.items())
        for _, y in sorted(v.items())], dtype=np.float32)

    y_score = np.asarray([
        y for k, v in sorted(submitted.items())
        for _, y in sorted(v.items())], dtype=np.float32)

    return 1.0 - roc_auc_score(y_true, y_score)


def score_per_block(submitted, reference):
    sub_occluded = {k: v for k, v in submitted.items() if 'occluded' in k}
    sub_visible = {k: v for k, v in submitted.items() if 'visible' in k}

    ref_occluded = {k: v for k, v in reference.items() if 'occluded' in k}
    ref_visible = {k: v for k, v in reference.items() if 'visible' in k}

    return {
        'visible': {
            'relative': _score_relative(sub_visible, ref_visible),
            'absolute': _score_absolute(sub_visible, ref_visible),
        },
        'occluded': {
            'relative': _score_relative(sub_occluded, ref_occluded),
            'absolute': _score_absolute(sub_occluded, ref_occluded),
        },
        'all': {
            'relative': _score_relative(submitted, reference),
            'absolute': _score_absolute(submitted, reference),
        }}


def score(submitted, reference):
    """Computes the evaluation scores

    The scores are computed for all scenes, visible scenes and
    occluded scenes. For each category the absolute and relative error
    rate are evaluated and returned as a dictionary.

    """
    assert sorted(submitted.keys()) == sorted(reference.keys())

    return {block: score_per_block(
        {k: v for k, v in submitted.items() if block in k},
        {k: v for k, v in reference.items() if block in k})
            for block in ('O1', 'O2', 'O3')}


def load_answer(path):
    """Returns the content of `path`/answer.txt as a dict

    Returns
    -------
    answer : dict
        The output dict is structured as follow::

            {scene: {1: p_1, 2: p_2, 3: p_3, 4: p_4}}

        where p_i is the plausibility score for the associated movie.

    Raises
    ------
    ValueError
        If `path`/answer.txt does not exist
    AssertionError
        If the answers file is badly formatted

    """
    if not os.path.isdir(path):
        raise ValueError('{} does not exist'.format(path))

    answer_file = os.path.join(path, 'answer.txt')
    if not os.path.isfile(answer_file):
        raise ValueError('{} does not exist'.format(answer_file))

    answer = collections.defaultdict(dict)
    for line in open(answer_file, 'r'):
        split_line = line.split()
        assert len(split_line) == 2

        plausibility = float(split_line[1])
        assert 0 <= plausibility <= 1

        header = split_line[0].split('/')
        scene_id = '/'.join(header[:-1])
        movie_id = header[-1]
        assert movie_id in ('1', '2', '3', '4')

        answer[scene_id][movie_id] = plausibility

    for v in answer.values():
        assert sorted(v.keys()) == ['1', '2', '3', '4']

    return answer


def build_html(submitted):
    header = '<!DOCTYPE html>\n<html>\n<body>\n\n<p>\n'
    footer = '</p></body></html>\n'

    html = ''
    for k, v in sorted(submitted.items()):
        for w, x in sorted(v.items()):
            html += '{}_{}: {}<br>\n'.format(k, w, x)

    return header + html + footer


def parse_arguments():
    """Parses command-line arguments"""
    parser = argparse.ArgumentParser(
        description='scoring program for the IntPhys challenge')
    parser.add_argument(
        'input_dir',
        help='directory containing reference and submission data')
    parser.add_argument(
        'output_dir',
        help='where the scores.txt file is written by the scoring program')

    return parser.parse_args()


def main():
    """Entry point of the IntPhys evaluation program"""
    args = parse_arguments()

    # load the submitted and reference data
    input_dir = args.input_dir
    submitted = load_answer(os.path.join(input_dir, 'res'))
    reference = load_answer(os.path.join(input_dir, 'ref'))

    output_dir = args.output_dir
    if not os.path.isdir(output_dir):
        raise ValueError('{} does not exist'.format(output_dir))

    # build the html page with detailed results
    html_file = os.path.join(output_dir, 'scores.html')
    with open(html_file, 'w') as fout:
        fout.write(build_html(submitted))

    # compute the scores
    scores = score(submitted, reference)

    # write the final scores.txt file
    scores_file = os.path.join(output_dir, 'scores.txt')
    with open(scores_file, 'w') as fout:
        for k, v in sorted(scores.items()):
            for w, x in v.items():
                for y, z in x.items():
                    fout.write('{}_{}_{}: {}\n'.format(k, w, y, z))


if __name__ == '__main__':
    main()
