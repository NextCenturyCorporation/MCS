
Validation for Eval1 Submissions
----------

The code in this directory will read a submissions file and subject it
to a series of tests to see if it is valid.  Valid is defined on the
Confluence page:
https://nextcentury.atlassian.net/wiki/spaces/MCSC/pages/621477896/Evaluation+E1+Plan+IntPhys

To run:

    % python3 mcs_validate.py submissions/submission_valid.zip 

The code will do the following:
 -- verify that it is a valid zip file
 -- unzip it to a temp directory
 -- check the following files:
    -- answer.txt
    -- description.json
    -- location.txt
    -- a voe file.  
 -- clean up the temp directory

If there is something wrong with the submission file or one of the
contained files, then it will try to provide the reason.
