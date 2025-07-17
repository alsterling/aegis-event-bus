#!/usr/bin/env bash
set -e
mkdir -p mosquitto/certs
mkdir -p mosquitto/conf

# Root CA
# The //CN=... is the fix for Git Bash on Windows
openssl req -x509 -nodes -days 3650 \
  -newkey rsa:2048 \
  -keyout mosquitto/certs/ca.key \
  -out  mosquitto/certs/ca.crt \
  -subj "//CN=AegisDevCA"

# Server cert
# The //CN=... is the fix for Git Bash on Windows
openssl req -nodes -newkey rsa:2048 \
  -keyout mosquitto/certs/server.key \
  -out  mosquitto/certs/server.csr \
  -subj "//CN=mosquitto"

openssl x509 -req -days 3650 \
  -in  mosquitto/certs/server.csr \
  -CA  mosquitto/certs/ca.crt \
  -CAkey mosquitto/certs/ca.key -CAcreateserial \
  -out mosquitto/certs/server.crt

echo "TLS certs generated in mosquitto/certs/"