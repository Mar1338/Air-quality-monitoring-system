import asyncio
import random
# import temp_pb2 as pb
# import generated.message_pb2 as pb
from generated import message_pb2 as pb
import os
# import message_pb2 as pb
# Получаем URL подключения из переменной окружения
SERVER_HOST = os.getenv('SERVER_HOST')
SERVER_PORT = os.getenv('SERVER_PORT')


async def send_to_server(writer: asyncio.StreamWriter):
    eventid = 0
    while True:

        # Заполняем даныне
        e = pb.MessageEvent()
        e.device_id = 1
        # e.eventId = random.randint(0, 100)
        e.event_id = eventid
        eventid += 1
        e.temp_cel = float(random.randint(25, 30))
        e.humidity = float(random.randint(50, 80))
        e.co2 = float(random.randint(6000, 8000))

        data = e.SerializeToString()  # Сериализация TempEvent в байты

        try:
            writer.write(data) # Отправляем данные
            await writer.drain()
        except Exception as e:
            print(f"Ошибка при отправке данных: {e}")
            break  # Завершаем цикл и функцию при возникновении ошибки

        await asyncio.sleep(1) # Sleep 1 s


async def main():
    addr = (SERVER_HOST, SERVER_PORT)  # Адрес и порт сервера
    # addr = ('localhost', 3000)
    try:
        print(f"Попытка подключения к серверу: {addr}")
        reader, writer = await asyncio.open_connection(*addr)
    except Exception as e:
        print(f"Ошибка при подключении к серверу: {e}")
        return  # Завершить выполнение функции, если подключение не удалось

    # Запускаем асинхронные задачи с помощью asyncio.gather(). Можно с помощью asyncio.create_task() отдельно каждую задачу и потом await
    await asyncio.gather(
        send_to_server(writer=writer),
        # read_from_server(reader=reader))
        )

    print('Close the connection')
    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main()) # Используем asyncio.run() как точку входа для запуска асинхронного кода. # является блокирующей функцией, что означает, что она блокирует поток, из которого была вызвана, до тех пор, пока асинхронная корутина не будет завершена.
