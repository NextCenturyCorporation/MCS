This will help you setup the MCS Structure

1.  Download Neon files located here:  https://nextcenturycorporation-my.sharepoint.com/personal/aamduka_hq_nextcentury_com/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Faamduka%5Fhq%5Fnextcentury%5Fcom%2FDocuments%2FAttachments%2Fneon%2Etar%2Egz&parent=%2Fpersonal%2Faamduka%5Fhq%5Fnextcentury%5Fcom%2FDocuments%2FAttachments&originalPath=aHR0cHM6Ly9uZXh0Y2VudHVyeWNvcnBvcmF0aW9uLW15LnNoYXJlcG9pbnQuY29tLzp1Oi9nL3BlcnNvbmFsL2FhbWR1a2FfaHFfbmV4dGNlbnR1cnlfY29tL0VhR01IYVVKTEtCQWlMOW8zaHlmSEg4QmhLVGFaVzdKSS1MaE1ZdlVRTlI4MGc_cnRpbWU9YTNEY0pyMW0xMGc  (It is suppose to be in owncloud as well but can't find the link for that)
2. Unzip/tar/gz the neon.tar.gz file (Note it might require you to untar the file twice)
3. Run install.sh in the Neon Directory
4. In the Neon directory after that completes run the command "docker-compose down"
5. Copy the "analysis-ui" and "node-graphql" folders into the Neon directory
6. Copy the docker-compose.yml file into the Neon directory
7. In the Neon directory run the command "docker build -t node-graphql node-graphql/."
8. In the Neon directory run the command "docker build -t analysis-ui analysis-ui/."
9. Run the command "docker-compose up -d"
10.  After that run the command "docker ps -a" to make sure all of the containers are up and running.
11.  Follow the README.md located in "ingest_results" in the MCS git repository, you should be able to run "python3 create_json_ingest.py" at the end (or your python of choice) to ingest results in ElasticSearch.  (Note the new docker-compose.yml file does not start up the Neon data load that imports the earthquake data.)

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