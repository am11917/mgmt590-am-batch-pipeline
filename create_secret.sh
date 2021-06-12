#!/bin/bash

# Make a copy of our secrets template
cp secret_template.json secret.json
cp secret_template_db.json secret_db.json

# Encode our GCS creds
GCS_ENCODED=$(cat $GOOGLE_APPLICATION_CREDENTIALS | base64 -w 0)

# Substitute those creds into our secrets file
sed -i -e 's|'REPLACE_GCS_CREDS'|'"$GCS_ENCODED"'|g' secret.json
sed -i -e 's|'REPLACE_STORAGE_BUCKET'|'"$STORAGE_BUCKET"'|g' secret.json

# Encode our SSL certs
SSLROOTCERT_ENCODED=$(cat $PG_SSLROOTCERT | base64 -w 0)
SSLCERT_ENCODED=$(cat $PG_SSLCERT | base64 -w 0)
SSLKEY_ENCODED=$(cat $PG_SSLKEY | base64 -w 0)

# Substitute those creds into our secrets file
sed -i -e 's|'REPLACE_PG_HOST'|'"$PG_HOST"'|g' secret_db.json
sed -i -e 's|'REPLACE_PG_PASSWORD'|'"$PG_PASSWORD"'|g' secret_db.json
sed -i -e 's|'REPLACE_PG_DBNAME'|'"$PG_DBNAME"'|g' secret_db.json
sed -i -e 's|'REPLACE_PG_USER'|'"$PG_USER"'|g' secret_db.json
sed -i -e 's|'REPLACE_PG_SSLROOTCERT'|'"$SSLROOTCERT_ENCODED"'|g' secret_db.json
sed -i -e 's|'REPLACE_PG_SSLCERT'|'"$SSLCERT_ENCODED"'|g' secret_db.json
sed -i -e 's|'REPLACE_PG_SSLKEY'|'"$SSLKEY_ENCODED"'|g' secret_db.json

# Create our secrets
pachctl create secret -f secret.json
pachctl create secret -f secret_db.json
