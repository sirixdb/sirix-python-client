echo "starting the docker environment"
docker-compose -f ./tests/resources/docker-compose.yml up -d keycloak
./test_resources/wait.sh
sleep 60
docker-compose -f ./tests/resources/docker-compose.yml up -d server
sleep 15
