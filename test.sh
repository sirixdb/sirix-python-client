echo "starting the docker environment"
docker-compose -f ./tests/resources/docker-compose.yml up -d keycloak
# bash ./tests/resources/wait.sh
sleep 30
docker-compose -f ./tests/resources/docker-compose.yml up -d server
sleep 30
