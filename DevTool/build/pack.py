import logging
import os
import secrets
import shutil
import string
import pyzipper
import re

PASSWORD_HELL: int = 42

def generate_random_password(length: int) -> str:
    """
    Генерирует случайный пароль заданной длины.

    Args:
        length (int): Длина пароля.

    Returns:
        str: Случайный пароль.
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def copy_folders(destination: str, folders: list[str]) -> None:
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    source_path = os.path.join(project_root, "Code.DM-Bot")

    for folder in folders:
        source_folder = os.path.join(source_path, folder)
        destination_path = re.sub(r'\.\./', '', folder)
        destination_folder = os.path.join(destination, destination_path)

        if os.path.exists(destination_folder):
            shutil.rmtree(destination_folder)

        shutil.copytree(source_folder, destination_folder)
        logging.info(f"Folder '{folder}' copied to '{destination_folder}'")

def zip_folder(
        folder_path, 
        output_path, 
        password, 
        compression = pyzipper.ZIP_DEFLATED, 
        encryption = pyzipper.WZ_AES
    ) -> None:
    parent_folder = os.path.dirname(folder_path)
    contents = os.walk(folder_path)

    try:
        if password is None:
            with pyzipper.AESZipFile(output_path, 'w', compression=compression) as zip_file:
                for root, folders, files in contents:
                    for folder_name in folders:
                        absolute_path = os.path.join(root, folder_name)
                        relative_path = os.path.relpath(absolute_path, parent_folder)
                        logging.info(f"Adding '{absolute_path}' to archive.")
                        zip_file.write(absolute_path, relative_path)

                    for file_name in files:
                        absolute_path = os.path.join(root, file_name)
                        relative_path = os.path.relpath(absolute_path, parent_folder)
                        logging.info(f"Adding '{absolute_path}' to archive.")
                        zip_file.write(absolute_path, relative_path)
        else:
            with pyzipper.AESZipFile(output_path, 'w', compression=compression, encryption=encryption) as zip_file:
                zip_file.setpassword(password)

                for root, folders, files in contents:
                    for folder_name in folders:
                        absolute_path = os.path.join(root, folder_name)
                        relative_path = os.path.relpath(absolute_path, parent_folder)
                        logging.info(f"Adding '{absolute_path}' to archive.")
                        zip_file.write(absolute_path, relative_path)

                    for file_name in files:
                        absolute_path = os.path.join(root, file_name)
                        relative_path = os.path.relpath(absolute_path, parent_folder)
                        logging.info(f"Adding '{absolute_path}' to archive.")
                        zip_file.write(absolute_path, relative_path)

        logging.info(f"'{output_path}' created successfully.")

    except FileNotFoundError as e:
        logging.error(f"File or directory not found: {e}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

def glue_key(zip_file, key):
    with open(zip_file, 'ab') as f:
        if key is not None:
            key_length = len(key)
            f.write(key)
        else:
            key_length = 0

        f.write(key_length.to_bytes(4, byteorder='big', signed=False))
        logging.info(f"Key '{key}' and its length '{key_length}' appended to '{zip_file}'")

def pack(
        destination_folder: str = "DM-Bot", 
        folder_to_add: list[str] = ["templates", "static"],
        use_password: bool = True 
    ) -> None:
    output_zip_name = destination_folder + ".zip"

    if use_password:
        password = generate_random_password(PASSWORD_HELL)
        password = password.encode("utf-8")
    else:
        password = None

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    copy_folders(destination_folder, folder_to_add)

    zip_folder(destination_folder, output_zip_name, password)

    logging.info(f"Selected folders are copied to '{destination_folder}' and compressed into '{output_zip_name}' with encryption '{password}'")

    glue_key(output_zip_name, password)

