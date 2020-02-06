#!/bin/bash

# Echo commands
set -x

# Stop on error
set -e

# 1.  Make sure you have docker installed or this won't work, built node-graphql container
docker build --tag node-graphql node-graphql/.

# 2.  Build Analysis UI Container
docker build --tag analysis-ui analysis-ui/.

# 3.  Download Neon file from S3:
NEON_FILE=neon-jan-2020.tar.gz
if [ ! -f $NEON_FILE ]; then 
    wget https://s3.amazonaws.com/www.machinecommonsense.com/$NEON_FILE
fi

# 4. Unzip/tar/gz the neon.tar.gz file (Note it might require you to untar the file twice)
tar xfz $NEON_FILE
NEON_DIR=neon-jan-2020/
cd $NEON_DIR

# 5. Copy javascript config files
cp -r ../analysis-ui/public/configs configs

# 5. Copy the docker-compose.yml file into the Neon directory
# rm docker-compose.yml
cp ../docker-compose-dev.yml docker-compose.yml

# 6. Run the install file
# These next steps are done by install.sh
cp ../install.sh .
./install.sh

# 7.  After that run the command "docker ps -a" to make sure all of the containers are up and running.
docker ps -a

# 8.  Follow the README.md located in "ingest_results" in the MCS git
# repository, you should be able to run "python3
# create_json_ingest.py" at the end (or your python of choice) to
# ingest results in ElasticSearch.  (Note the new docker-compose.yml
# file does not start up the Neon data load that imports the
# earthquake data.)

# Wait for the ES to come up
sleep 30
#cd ../../ingest_results
#python3 create_json_ingest.py

set +x
set +e
