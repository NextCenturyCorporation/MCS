#!/bin/bash

# Take the json data and put it in elastic search

# Assume that ES is running on port 9200
HOST="http://localhost:9200"

# If we are running a docker container, then use this
# HOST="http://elasticsearch:9200"

DATA_SET="mcs_eval"

until curl -s ${HOST} > /dev/null
do
  sleep .5
done

curl -X DELETE -s ${HOST}/${DATA_SET}
curl -H 'Content-Type: application/json' \
     -XPUT -s \
     -d @/${DATA_SET}_mapping.json \
     ${HOST}/${DATA_SET}

npx elasticdump --input=${DATA_SET}.json --output=${HOST}
