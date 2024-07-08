#!/bin/sh
# Usage:    ./confluent-cli.sh TOPIC-NAME FORMAT SCHEMA-FILE
# Example:  ./confluent-cli.sh victoria-avro-registry avro kttm.avro.schema
confluent kafka topic produce $1 --value-format $2 --schema $3
