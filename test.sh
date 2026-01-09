#!/bin/bash
set -e

echo "Starting the docker environment..."
docker compose -f ./tests/resources/docker-compose.yml up -d keycloak

echo "Waiting for Keycloak to be ready..."
bash ./tests/resources/wait.sh
echo "Keycloak is ready!"

echo "Starting SirixDB server..."
docker compose -f ./tests/resources/docker-compose.yml up -d server

echo "Waiting for SirixDB server container to be running..."
sleep 5

# Check if container is running
if ! docker ps --filter "name=server" --format "{{.Names}}" | grep -q "server"; then
    echo "ERROR: SirixDB server container failed to start"
    docker compose -f ./tests/resources/docker-compose.yml logs server
    exit 1
fi

echo "Container is running. Giving SirixDB time to initialize..."
echo "Checking if server is responding on port 9443..."

# Wait for server to be responsive (try both HTTP and HTTPS)
for i in {1..30}; do 
    # Try HTTPS first (more common for port 9443)
    if curl -k -s -o /dev/null -w "%{http_code}" https://localhost:9443 2>/dev/null | grep -q "^[234]"; then 
        echo "SirixDB is responding on HTTPS!"
        break
    fi
    # Try HTTP as fallback
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:9443 2>/dev/null | grep -q "^[234]"; then 
        echo "SirixDB is responding on HTTP!"
        break
    fi
    
    if [ $((i % 5)) -eq 0 ]; then
        echo "Still waiting for response... (attempt $i/30)"
    fi
    
    sleep 2
done

# Give it a few more seconds to stabilize
echo "Waiting 10 more seconds for services to stabilize..."
sleep 10

echo "SirixDB setup complete!"
docker ps --filter "name=resources" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
