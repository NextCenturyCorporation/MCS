
# Ingestion Routines

The code in this directory reads in data from a submission (in
answer.txt and other files) to load ElasticSearch (ES) with data that
can be searched, sorted, and filtered.

To help with the development of this, it also creates fake submissions
and other data (ground_truth and test metadata) that will be used
during the ingestion.

## Steps

1. Run create_fake_ground_truth.py.  This will produce
   ground_truth.txt that represents what the 'right' answers are.
   This is the same format at the answer.txt file, with integer values
   rather than real values.

1. Run create_fake_test_metadata.py.  This will produce a
   metadata.json that represents the information that IntPhys has
   regarding the tests; namely, what the objects are, what is being
   done wrong, etc.

1. Run create_fake_submissions.py.  This will produce several .zip
   files that represent submissions from performer.  Pass in '--num X'
   to produce X of them; defaults to 1. 

1. Run create_json_ingest.py.  This will pull in the .zip files, the metadata,
   and the ground truth files and push them in to ES.
   


