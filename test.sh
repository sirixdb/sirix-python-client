echo "starting the docker environment"
docker-compose -f ./tests/resources/docker-compose.yml up -d keycloak
./test_resources/wait.sh
sleep 15
docker-compose -f ./tests/resources/docker-compose.yml up -d server
sleep 5
