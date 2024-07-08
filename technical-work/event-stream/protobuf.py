#!/usr/bin/env python3
from kafka import KafkaProducer

import sys
sys.path.append("/Users/victorialim/Documents/work_projects/220927_file-formats-polaris/protobuf/kttm/")
import kttm_pb2


def main():

    producer = KafkaProducer(bootstrap_servers="pkc-4nym6.us-east-1.aws.confluent.cloud:9092",
        security_protocol="SASL_SSL",
        sasl_mechanism="PLAIN",
        sasl_plain_username="OUH7L6K26IQOVQZO",
        sasl_plain_password="xxx")


    # Define location of schema file and a sample payload request
    payload = {"timestamp":"2025-01-26T00:00:00.212Z","city":"Christchurch","session":"S97953932","session_length":337}

    # Initialize the KTTM message
    kttm = kttm_pb2.SomeMessage(timestamp=payload["timestamp"],
                         city=payload["city"],
                         session=payload["session"],
                         session_length=payload["session_length"])

    producer.send("victoria-inline-protobuf2", kttm.SerializeToString())
    producer.flush()

if __name__ == "__main__":
    main()
