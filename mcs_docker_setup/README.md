# These installation instructions are for the Eval Platform for Eval1 at this time.

 1. Make sure you have docker installed (Mac - brew install docker)
 2. Make sure you also have docker-compose installed (comes included in Mac install)
 3. Make sure you have wget installed (Mac - brew install wget)
 4. Make sure you have git installed (Mac - brew install git)
 5. Check out the project here:  https://github.com/NextCenturyCorporation/MCS
 6. cd into the project and into the subfolder ‘mcs_docker_setup’
 7. sh install_from_scratch.sh
 8. Next install python and pip (I installed python3/pip3 on mac). 
 9. Install python elasticsearch client ('pip install elasticsearch', or ‘pip3 install elasticsearch’ if using a mac)
10. Then go to the ingest_results folder in the MCS project
11. Copy the ground_truth.txt file (https://development-environment-setup.s3.amazonaws.com/ground_truth.txt) into the ingest_results folder
12. Unzip the submissions.zip (https://development-environment-setup.s3.amazonaws.com/submissions.zip) file into the ingest_results folder (Note:  this will unzip the first 6 submission files we received, if you are adding additional submissions, please zip up the contents of the folder only, and not the folder itself.  Also your submission file must start with the word submission) 
13. Now run with python the create_json_ingest.py (if you installed python3 on mac, the command is python3 create_json_ingest.py)
14. You should then be able to navigate to:  http://localhost:4199/?dashboard=-#%E2%9F%A6%E2%9F%A7

*** Note, if you are adding additional submissions, add your submission zip to the ingest results folder and run step 12 again.

# After Setup

After those steps, you should have the follow available to you:

Kibana - http://localhost:5601/app/kibana#/management/kibana/index?_g=()
 - Here you can see that there is now an index for "msc_eval" along with discovering the data in ElasticSearch

GraphQL - http://localhost:9100/graphql
 - This will let you write queries and test to see what the back end returns.  If you want ALL the data your query would look like this:

    {
        msc_eval {
            block
            complexity
            ground_truth
            num_objects
            occluder
            performer
            plausibility
            scene
            submission
            test
            url_string
            voe_signal
        }
    }

    or

    {
        getEvalAnalysis (test: "0001", block:"O1",     submission:"submission_0", performer:"TA1_group_test") {
            block
            complexity
            ground_truth
            num_objects
            occluder
            performer
            plausibility
            scene
            submission
            test
            url_string
            voe_signal
        }
    }

Neon - http://localhost:4199/?dashboard=-#%E2%9F%A6%E2%9F%A7
 - Neon view of all the data in ElasticSearch

Analysis-UI - http://localhost:3000/
 - Page to view the individual Results