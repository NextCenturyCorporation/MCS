#!/bin/bash

python create_fake_ground_truth.py

python create_fake_test_metadata.py

python create_fake_submissions.py 5

python create_json_ingest.py

ingest.sh

