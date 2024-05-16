import socket
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

# import temp_pb2 as pb
# import generated.message_pb2 as pb
from generated import message_pb2 as pb
# import message_pb2 as pb
import os
# Получаем URL подключения из переменной окружения
# For server listening
SERVER_HOST = os.getenv('SERVER_HOST')
SERVER_PORT = os.getenv('SERVER_PORT')
# For connecting to influxdb
INFLUXDB_URL = os.getenv('INFLUXDB_URL')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((SERVER_HOST, int(SERVER_PORT)))
    # server.bind(('localhost', 3000))
    server.listen()
    print(f'Server listening on "{SERVER_HOST}:{SERVER_PORT}"...')

    connection, address = server.accept()
    with connection:
        print(f'New connection accepted from "{address}"...')
        while True:
            request = pb.MessageEvent()
            request.ParseFromString(connection.recv(1024))

            # print(f' device_id: "{request.device_id}" event_id: "{request.event_id}" humidity: "{request.humidity}" temp_cel: "{request.temp_cel}" co2: "{request.co2}"')

            try:
                # Write data to InfluxDB
                client = influxdb_client.InfluxDBClient(
                    url=INFLUXDB_URL,
                    token=INFLUXDB_TOKEN,
                    org=INFLUXDB_ORG
                )
                write_api = client.write_api(write_options=SYNCHRONOUS)

                p = influxdb_client.Point("my_measurement").tag(f"Device id", request.device_id).field("event_id", request.event_id).field("humidity", request.humidity).field("temp_cel", request.temp_cel).field("co2", request.co2)
                write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=p)

                # Query data from InfluxDB
                query_api = client.query_api()
                # query = f'from(bucket: "{INFLUXDB_BUCKET}") \
                #              |> range(start: -10m) \
                #              |> filter(fn: (r) => r["_measurement"] == "my_measurement") \
                #              |> filter(fn: (r) => r["_field"] == "event_id")'
                # result = query_api.query(org=INFLUXDB_ORG, query=query)
                # for table in result:
                #     for record in table.records:
                #         print("QUERY_RESULT: ",(record.get_field(), record.get_value()))

                # query = f'''
                # from(bucket: "{INFLUXDB_BUCKET}")
                #     |> filter(fn: (r) => r["_measurement"] == "my_measurement")
                #     |> last()
                # '''
                # result = query_api.query(org=INFLUXDB_ORG, query=query)
                # a = 0
                # for table in result:
                #     for record in table.records:
                #         print(f"a is {a} QUERY_RESULT: ", (record.get_field(), record.get_value()))

            except Exception as e:
                print(f"Ошибка: {e}")
                continue