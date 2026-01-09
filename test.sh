#!/bin/bash
set -e

echo "Starting the docker environment..."
docker compose -f ./tests/resources/docker-compose.yml up -d keycloak

echo "Waiting for Keycloak to be ready..."
bash ./tests/resources/wait.sh
echo "Keycloak is ready!"

echo "Starting SirixDB server..."
docker compose -f ./tests/resources/docker-compose.yml up -d server

echo "Waiting for SirixDB server to be ready..."
for i in {1..30}; do 
    if curl -s -f http://localhost:9443 > /dev/null 2>&1; then 
        echo "SirixDB is ready!"
        exit 0
    fi
    
    # Show container status every 5 iterations
    if [ $((i % 5)) -eq 0 ]; then
        echo "Still waiting... (attempt $i/30)"
        docker ps --filter "name=server" --format "table {{.Names}}\t{{.Status}}"
    else
        echo "Waiting for SirixDB... (attempt $i/30)"
    fi
    
    sleep 2
done

echo "ERROR: SirixDB failed to become ready after 60 seconds"
echo "Container logs:"
docker compose -f ./tests/resources/docker-compose.yml logs server
exit 1
