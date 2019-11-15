#!/bin/bash

# Echo commands
set -x

# Stop on error
set -e

# 1.  Download Neon file from S3: 
wget https://s3.amazonaws.com/www.machinecommonsense.com/neon-2019-11-04-thomas.tgz

# 2. Unzip/tar/gz the neon.tar.gz file (Note it might require you to untar the file twice)
tar xfz neon-2019-11-04-thomas.tgz
NEON_DIR=neon-2019-11-04-thomas/
cd $NEON_DIR

# 3. Run install.sh in the Neon Directory
#      -->   Actually, don't do this now, do it later after copying / building 
# ./install.sh

# 4. In the Neon directory after that completes run the command "docker-compose down"
docker-compose down

# 5. Copy the "analysis-ui" and "node-graphql" folders into the Neon directory
cp -r ../analysis-ui .
cp -r ../node-graphql .

# 6. Copy the docker-compose.yml file into the Neon directory
cp ../docker-compose.yml .

# --------------------------------------------------
# These next steps are done by install.sh
cp ../install.sh .
./install.sh
# 7. In the Neon directory run the command "docker build -t node-graphql node-graphql/."
# docker build -t node-graphql node-graphql/.

# 8. In the Neon directory run the command "docker build -t analysis-ui analysis-ui/."
# docker build -t analysis-ui analysis-ui/.

# 9. Run the command "docker-compose up -d"
# docker-compose up -d
# -------------------------------------------------- 

# 10.  After that run the command "docker ps -a" to make sure all of the containers are up and running.
docker ps -a

# 11.  Follow the README.md located in "ingest_results" in the MCS git
# repository, you should be able to run "python3
# create_json_ingest.py" at the end (or your python of choice) to
# ingest results in ElasticSearch.  (Note the new docker-compose.yml
# file does not start up the Neon data load that imports the
# earthquake data.)

# Wait for the ES to come up
sleep 30
cd ../../ingest_results
python3 create_json_ingest.py

set +x
set +e
