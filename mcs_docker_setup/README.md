This will help you setup the MCS Structure

1.  Download Neon files located here:  https://s3.amazonaws.com/www.machinecommonsense.com/neon-2019-11-04-thomas.tgz
2. Unzip the file
3. Run install.sh in the Neon Directory
4. Copy the "analysis-ui" and "node-graphql" folders into the Neon directory
5. Copy the docker-compose.yml file into the Neon directory
6. In the Neon directory run the command "docker build -t node-graphql node-graphql/."
7. In the Neon directory run the command "docker build -t analysis-ui analysis-ui/."
8. Copy the config.yaml file that is in the MCS/ingest_results directory into the Neon/resources directory
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