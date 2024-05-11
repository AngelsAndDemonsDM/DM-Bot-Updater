import logging
import os
import shutil
import subprocess

import pyzipper
import requests
from requests.exceptions import RequestException


class Updater():
    def __init__(self) -> None:
        """
        Инициализация объекта класса Updater.
        """
        self._data_dirs: list = ["Data.DM-Bot"]

    @staticmethod
    def get_latest_release_url() -> str:
        api_url = "https://api.github.com/repos/AngelsAndDemonsDM/DM-Bot/releases/latest"
        response = requests.get(api_url)
        response.raise_for_status()
        
        release_info = response.json()
        return release_info['assets'][1]['browser_download_url'] 

    @staticmethod
    def check_file_in_directory(directory, filename) -> bool:
        """
        Проверяет наличие файла в указанной директории.

        Args:
            directory (str): Директория для поиска файла.
            filename (str): Имя файла для проверки.

        Returns:
            bool: True, если файл существует; False, если файла нет.
        """
        file_path = os.path.join(directory, filename)

        if os.path.exists(file_path):
            return True

        return False

    def get_version_local(self, directory: str = "DM-Bot", filename: str = "main.exe") -> str:
        """
        Получает версию программы из указанного файла.

        Args:
            directory (str): Директория, где находится файл.
            filename (str): Имя файла, из которого нужно получить версию.

        Returns:
            str: Версия программы, полученная из файла.
        """
        version = None

        if self.check_file_in_directory(directory, filename):
            result = subprocess.run([f"{directory}/{filename}", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()

        return version

    @staticmethod
    def get_version_server() -> str:
        """
        Получает версию программы с сервера.

        Returns:
            str: Версия программы, полученная с сервера.
        """
        api_url = "https://api.github.com/repos/AngelsAndDemonsDM/DM-Bot/releases/latest"
        response = requests.get(api_url)
        response.raise_for_status()

        release_info = response.json()
        return release_info['tag_name']

    @staticmethod
    def extract_key_from_zip(zip_file) -> bytes:
        """
        Извлекает ключ шифрования из архива.

        Args:
            zip_file (str): Путь к архиву.

        Returns:
            bytes: Ключ шифрования или None, если архив не зашифрован.
        """
        with open(zip_file, 'rb') as f:
            
            f.seek(-4, 2)
            key_length_bytes = f.read(4)
            key_length = int.from_bytes(key_length_bytes, byteorder='big', signed=False)
            
            if key_length == 0:
                return None
            
            f.seek(-(4 + key_length), 2)
            key = f.read(key_length)
        
        return key

    def compare_versions(self, version1: str, version2: str) -> int:
        """
        Сравнивает две версии и возвращает результат сравнения.

        Args:
            version1 (str): Первая версия для сравнения.
            version2 (str): Вторая версия для сравнения.

        Returns:
            int: 1, если version1 > version2; -1, если version1 < version2; 0, если version1 == version2.
        """
        if version1 is None and version2 is None:
            return 0
        
        if version1 is None:
            return -1
        
        if version2 is None:
            return 1
        
        parts1 = [int(part) for part in version1.split('.')]
        parts2 = [int(part) for part in version2.split('.')]
        
        len_diff = len(parts1) - len(parts2)
        if len_diff > 0:
            parts2 += [0] * len_diff
        elif len_diff < 0:
            parts1 += [0] * (-len_diff)
        
        for part1, part2 in zip(parts1, parts2):
            if part1 > part2:
                return 1
            elif part1 < part2:
                return -1
        return 0
    
    def download_latest_release(self, file_name, chunk_size=8192, retries=3, timeout=30):
        """
        Скачивает самый последний релиз с сервера GitHub.

        Args:
            file_name (str): Имя файла для сохранения.
            chunk_size (int): Размер части для скачивания.
            retries (int): Количество попыток скачивания.
            timeout (int): Время ожидания ответа сервера.

        Raises:
            RequestException: Если скачивание не удалось после всех попыток.

        Returns:
            str: Имя скачанного файла.
        """
        for _ in range(retries):
            try:
                with requests.get(self.get_latest_release_url(), stream=True, timeout=timeout) as response:
                    response.raise_for_status()
                        
                    with open(file_name, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                file.write(chunk)
                    
                return file_name
                
            except requests.Timeout:
                logging.error(f"Timeout occurred during download. Retrying ({retries} retries left).")
            
            except requests.RequestException as e:
                logging.error(f"Error during download: {e}. Retrying ({retries} retries left).")
        
        raise RequestException(f"Failed to download after {retries} retries.")
    
    def update(self):
        """
        Обновляет программу до новой версии.

        Обновляет программу, скачивая архив с сервера, распаковывая его и удаляя старую версию.
        """
        destination_folder = "DM-Bot"
        zip_filename = "DM-Bot.zip"

        try:
            if self.compare_versions(self.get_version_server(), self.get_version_local()) != 1:
                logging.info("Обновлений не обнаружено. У вас самая новая версия DM-Bot.")
                return

            if os.path.exists(destination_folder):
                logging.info("Удаление старой версии")
                for item in os.listdir(destination_folder):
                    if item in self._data_dirs:
                        continue

                    item_path = os.path.join(destination_folder, item)
                    
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)

            logging.info("Начинаю скачивать архив с сервера...")
            self.download_latest_release(file_name=zip_filename)
            
            logging.info("Начало распаковки...")
            password = self.extract_key_from_zip(zip_filename)

            with pyzipper.AESZipFile(zip_filename, 'r') as zip_ref:
                zip_ref.setpassword(password)
                zip_ref.extractall(os.getcwd())

            logging.info("Архив распакован!")
            os.remove(zip_filename)

            logging.info("Программа успешно обновлена")
        
        except Exception as err:
            logging.error(f"Получена ошибка при попытке обновления: {err}")
            return
