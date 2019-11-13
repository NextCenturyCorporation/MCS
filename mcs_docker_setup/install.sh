#neon installation on docker

docker build -t node-graphql node-graphql/.

docker build -t analysis-ui analysis-ui/.

echo 'loading neon-api image...'
docker load < neon-api.tar.gz

echo 'starting neon system container...'
docker-compose up -d
