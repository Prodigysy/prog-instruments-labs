import asyncio
import random
import time

from aiofiles import open as aio_open


async def download_file(file_url: str, file_name: str) -> str:
    """
    Эмулирует загрузку файла с задержкой и сохраняет данные в файл.

    :param file_url: URL для загрузки файла.
    :param file_name: Имя файла, в который будет записан результат.
    :return: Имя файла, в который были сохранены данные.
    """
    print(f"Загрузка файла с {file_url} начинается...")
    delay = random.uniform(2, 5)  # Задержка от 2 до 5 секунд
    await asyncio.sleep(delay)  # Эмуляция загрузки
    async with aio_open(file_name, mode='w') as f:
        await f.write(
            f"Загруженные данные с {file_url}. "
            f"Задержка: {delay:.2f} секунд.\n")
    print(f"Файл {file_name} загружен за {delay:.2f} секунд.")
    return file_name


async def fetch_data_from_api(api_url: str) -> str:
    """
    Эмулирует запрос к API с задержкой.

    :param api_url: URL для запроса к API.
    :return: Результат запроса в виде строки.
    """
    print(f"Запрос к API {api_url} начинается...")
    delay = random.uniform(1, 3)  # Задержка от 1 до 3 секунд
    await asyncio.sleep(delay)  # Эмуляция задержки
    print(f"Ответ от API {api_url} получен за {delay:.2f} секунд.")
    return f"Данные с {api_url}"


async def analyze_data(file_name: str) -> str:
    """
    Эмулирует асинхронный анализ данных из файла.

    :param file_name: Имя файла, данные из которого нужно проанализировать.
    :return: Результат анализа в виде строки.
    """
    print(f"Начинается анализ данных из {file_name}...")
    delay = random.uniform(1, 4)  # Задержка от 1 до 4 секунд
    await asyncio.sleep(delay)  # Эмуляция анализа данных
    print(f"Анализ данных из {file_name} завершен за {delay:.2f} секунд.")
    return f"Результаты анализа {file_name}"


async def main() -> None:
    """
    Главная асинхронная функция для выполнения всех задач: загрузки файлов,
    запросов к API и анализа данных.
    """
    start_time = time.time()

    # Список URL для загрузки файлов и API для запросов
    file_urls = [
        'https://example.com/file1',
        'https://example.com/file2',
        'https://example.com/file3'
    ]

    api_urls = [
        'https://api.example.com/data1',
        'https://api.example.com/data2',
        'https://api.example.com/data3'
    ]

    file_download_tasks = [
        download_file(file_urls[i], f'file_{i+1}.txt') for i in range(3)
    ]
    api_fetch_tasks = [
        fetch_data_from_api(api_urls[i]) for i in range(3)
    ]
    file_analysis_tasks = [
        analyze_data(f'file_{i+1}.txt') for i in range(3)
    ]

    all_tasks = file_download_tasks + api_fetch_tasks + file_analysis_tasks

    completed_tasks = await asyncio.gather(*all_tasks)

    print("\nВсе задачи завершены:")
    for result in completed_tasks:
        print(result)

    end_time = time.time()
    print(f"\nВремя выполнения: {end_time - start_time:.2f} секунд.")

if __name__ == "__main__":
    asyncio.run(main())
