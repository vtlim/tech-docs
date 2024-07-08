from kafka import KafkaProducer
import io
from avro.schema import Parse
from avro.io import DatumWriter, DatumReader, BinaryEncoder, BinaryDecoder

# Create a Kafka client ready to produce messages
producer = KafkaProducer(bootstrap_servers="pkc-4nym6.us-east-1.aws.confluent.cloud:9092",security_protocol="SASL_SSL",sasl_mechanism="PLAIN",
                         sasl_plain_username="OUH7L6K26IQOVQZO",
                         sasl_plain_password="xxx")

# Get the schema to use to serialize the message
schema = Parse(open("kttm.avsc", "rb").read())

myobject={"city":"qqqqqqqq","timestamp":"2023-01-30T02:47:05.474Z","session":"wwwwww","session_length":5000}
#myobject={"timestamp":"2023-01-20T02:47:05.474Z","city":"xxxxxxx","session":"yyyyyy","session_length":9000}

# serialize the message data using the schema
buf = io.BytesIO()
encoder = BinaryEncoder(buf)
writer = DatumWriter(writer_schema=schema)
writer.write(myobject, encoder)
buf.seek(0)
message_data = (buf.read())

# message key if needed
key = None

# headers if needed
headers = []

print(message_data)

reader = DatumReader(schema)
decoder = BinaryDecoder(io.BytesIO(message_data))
print(reader.read(decoder))

# Send the serialized message to the Kafka topic
producer.send("victoria-inline-avro-python",
              message_data,
              key,
              headers)
producer.flush()
