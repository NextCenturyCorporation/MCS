# MCS

This is code that may be useful for people on the Machine Common Sense
program.

## 

 1. Make sure you have docker installed (Mac - brew install docker)
 2. Make sure you have wget installed (Mac - brew install wget)
 3. Make sure you have git installed (Mac - brew install git)
 4. Check out the project here:  https://github.com/NextCenturyCorporation/MCS
 5. cd into the project and into the subfolder ‘mcs_docker_setup’
 6. sh install_from_scratch.sh
 7. Next install python and pip (I installed python3/pip3 on mac). 
 8. Install python elasticsearch client ('pip install elasticsearch', or ‘pip3 install elasticsearch’ if using a mac)
 9. Then go to the ingest_results folder in the MCS project
10. Copy the ground_truth.txt file (https://development-environment-setup.s3.amazonaws.com/ground_truth.txt) into the ingest_results folder
11. Unzip the submissions.zip (https://development-environment-setup.s3.amazonaws.com/submissions.zip) file into the ingest_results folder (Note:  this will unzip the first 6 submission files we received, if you are adding additional submissions, please zip up the contents of the folder only, and not the folder itself.  Also your submission file must start with the word submission) 
12. Now run with python the create_json_ingest.py (if you installed python3 on mac, the command is python3 create_json_ingest.py)
13. You should then be able to navigate to:  http://localhost:4199/?dashboard=-#%E2%9F%A6%E2%9F%A7

*** Note, if you are adding additional submissions, add your submission zip to the ingest results folder and run step 12 again.

## Ingest Results

The code in this directory creates placeholders / examples of ground
truth and submissions.  It is useful to see what a submission should
look like and allows us to practice ingesting the data for scoring and
visualizations.  The ground truth information, like the submission
data, is made up.

## Masks

The code in this directory makes the mask information for training
data consistent.


## Apache 2 Open Source License

Code in this repository is made available by [Next Century
Corporation][1] under the [Apache 2 Open Source License][2].  You may
freely download, use, and modify, in whole or in part, the source code
or release packages. Any restrictions or attribution requirements are
spelled out in the license file.  For more information about the
Apache license, please visit the [The Apache Software Foundation’s
License FAQ][3].

[1]: http://www.nextcentury.com
[2]: http://www.apache.org/licenses/LICENSE-2.0.txt
[3]: http://www.apache.org/foundation/license-faq.html
