#!/bin/bash

python3 create_fake_ground_truth.py

python3 create_fake_test_metadata.py

python3 create_fake_submissions.py --num 5

python3 create_json_ingest.py

ingest.sh

