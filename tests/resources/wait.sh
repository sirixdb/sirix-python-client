bash -c 'while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' http://keycloak:8080/realms/master)" != "200" ]]; do sleep 5; done'
