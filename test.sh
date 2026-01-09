echo "starting the docker environment"
docker compose -f ./tests/resources/docker-compose.yml up -d keycloak
echo "waiting for keycloak to be ready..."
bash ./tests/resources/wait.sh
docker compose -f ./tests/resources/docker-compose.yml up -d server
echo "waiting for sirix server to be ready..."
bash -c 'for i in {1..30}; do if curl -k -s -f https://localhost:9443 > /dev/null 2>&1; then echo "SirixDB is ready"; break; fi; echo "Waiting for SirixDB..."; sleep 2; done'
