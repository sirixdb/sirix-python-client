#!/bin/bash
# Wait for Keycloak master realm to be ready
echo "Checking Keycloak master realm..."
bash -c 'while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' localhost:8080/realms/master)" != "200" ]]; do sleep 5; echo "Waiting for Keycloak master realm..."; done'
echo "Master realm ready!"

# Wait for the sirixdb realm to be available
echo "Checking Keycloak sirixdb realm..."
bash -c 'while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' localhost:8080/realms/sirixdb)" != "200" ]]; do sleep 2; echo "Waiting for sirixdb realm..."; done'
echo "Sirixdb realm ready!"
