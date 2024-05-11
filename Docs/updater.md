# Документация по файлу `updater.py`


## `Updater.__init__`<br>
Инициализация объекта класса Updater.<br>
<br>

## `Updater.check_file_in_directory`<br>
Проверяет наличие файла в указанной директории.<br>
**Args:**<br>
directory (str): Директория для поиска файла.<br>
filename (str): Имя файла для проверки.<br>
**Returns:**<br>
bool: True, если файл существует; False, если файла нет.<br>
<br>

## `Updater.get_version_local`<br>
Получает версию программы из указанного файла.<br>
**Args:**<br>
directory (str): Директория, где находится файл.<br>
filename (str): Имя файла, из которого нужно получить версию.<br>
**Returns:**<br>
str: Версия программы, полученная из файла.<br>
<br>

## `Updater.get_version_server`<br>
Получает версию программы с сервера.<br>
**Returns:**<br>
str: Версия программы, полученная с сервера.<br>
<br>

## `Updater.extract_key_from_zip`<br>
Извлекает ключ шифрования из архива.<br>
**Args:**<br>
zip_file (str): Путь к архиву.<br>
**Returns:**<br>
bytes: Ключ шифрования или None, если архив не зашифрован.<br>
<br>

## `Updater.compare_versions`<br>
Сравнивает две версии и возвращает результат сравнения.<br>
**Args:**<br>
version1 (str): Первая версия для сравнения.<br>
version2 (str): Вторая версия для сравнения.<br>
**Returns:**<br>
int: 1, если version1 > version2; -1, если version1 < version2; 0, если version1 == version2.<br>
<br>

## `Updater.download_latest_release`<br>
Скачивает самый последний релиз с сервера GitHub.<br>
**Args:**<br>
file_name (str): Имя файла для сохранения.<br>
chunk_size (int): Размер части для скачивания.<br>
retries (int): Количество попыток скачивания.<br>
timeout (int): Время ожидания ответа сервера.<br>
**Raises:**<br>
RequestException: Если скачивание не удалось после всех попыток.<br>
**Returns:**<br>
str: Имя скачанного файла.<br>
<br>

## `Updater.update`<br>
Обновляет программу до новой версии.<br>
Обновляет программу, скачивая архив с сервера, распаковывая его и удаляя старую версию.<br>
<br>
