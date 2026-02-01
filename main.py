import requests
import os
from urllib.parse import unquote
import re
import pyfiglet
from colorama import Fore,init
import time
from tqdm import tqdm
import pdfplumber
def end_calc(finish_time):
    hours = finish_time // 3600
    minutes = (finish_time % 3600) // 60
    seconds = finish_time % 60
    if hours <= 1:
        result = f"Загрузка завершена за {hours} ч {minutes} мин {seconds} сек"
    elif minutes <= 1:
        result = f"Загрузка завершена за {minutes} мин {seconds} сек"
    else:
        result = f"Загрузка завершена {seconds} за сек"
    return result
def clear_terminal():
    global art
    init(autoreset=True) 
    art = pyfiglet.figlet_format("WebFileCrawler", font="big")
    os.system('cls')
    print(Fore.GREEN + art)
def pdf_to_txt_plumber(pdf_path, txt_path):
    with pdfplumber.open(pdf_path) as pdf:
        with open(txt_path, 'w', encoding='utf-8') as f:
            for page in pdf.pages:
                f.write(page.extract_text() + '\n')
def clean_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "_", filename)
def is_pdf_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            return f.read(4) == b'%PDF'
    except:
        return False
if __name__ == '__main__':
    clear_terminal()#

    user_url = input(Fore.GREEN + "Ссылка для установки \n")
    clear_terminal()

    index = int(input(Fore.GREEN + "Стартовый индекс \n"))
    clear_terminal()

    download_path = input(Fore.GREEN + "Путь установки \n")
    os.makedirs(download_path, exist_ok=True)
    clear_terminal()

    find_word = input(Fore.GREEN + "Искомое слово \n") or None
    clear_terminal()

    log_path = os.path.join(download_path, "download_log.txt")
    log_file = open(log_path, 'w', encoding='utf-8')
    log_file.write(f"{art}\n")

    pbar = tqdm(           
        unit=" файл",
        bar_format=(
            Fore.GREEN
            + "Скачивание файлов : {n_fmt} файлов "
            "[{elapsed}, {rate_fmt}]"
        )
    )

    total_size = 0
    empty_files = 0
    files_count = 0

    start_time = int(time.time())

    while True:
        namecheck = str(None)
        url = re.sub(r'id=\d+', f'id={index}',user_url) 

        try:
            response = requests.get(url, timeout=30)
        except requests.exceptions.RequestException as e:
            index += 1
            time.sleep(2)
            continue
        if response.status_code == 200:
            empty_files = 0
            filename = "Файл без имени.pdf"

            if 'Content-Disposition' in response.headers:
                content_disposition = response.headers['Content-Disposition']
                    
                if "filename*=UTF-8''" in content_disposition:
                    filename = content_disposition.split("filename*=UTF-8''")[-1]
                    filename = unquote(filename)
                elif 'filename=' in content_disposition:
                    filename = content_disposition.split('filename=')[-1].strip('"')
                    try:
                        filename = filename.encode('latin-1').decode('utf-8')
                    except:
                        try:
                            filename = unquote(filename)
                        except:
                            filename = f"Файл без имени{index}.pdf"
                              
            if find_word is not None:
                namecheck = filename
                if find_word in namecheck.lower():
                    filename = clean_filename(filename)
                    if not filename or filename in (".pdf", "_pdf", "_.pdf"):
                        filename = f"Файл_без_имени_{index}.pdf"
                    full_path = os.path.join(download_path, filename)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    txt_folder = os.path.join(download_path, find_word)
                    os.makedirs(txt_folder, exist_ok=True)
                    txt_path = os.path.join(txt_folder, filename.replace('.pdf', '.txt'))
                    with open(full_path, 'wb') as file:
                        file.write(response.content)

                    if response.headers.get('Content-Type', '').lower() == 'application/pdf' and is_pdf_file(full_path):
                        pdf_to_txt_plumber(full_path, txt_path)
                    else:
                        log_file.write(f"{filename} ID: {index} (не PDF)\n")
                    total_size += len(response.content)
                    pbar.update(1)
                    log_file.write(f"{filename} ID: {index}\n")
                    files_count += 1
                    index += 1
                else:
                    filename = clean_filename(filename)
                    if not filename or filename in (".pdf", "_pdf", "_.pdf"):
                        filename = f"Файл_без_имени_{index}.pdf"
                    full_path = os.path.join(download_path, filename)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, 'wb') as file:
                        file.write(response.content)
                    total_size += len(response.content)
                    pbar.update(1)
                    log_file.write(f"{filename} ID: {index}\n")
                    files_count += 1
                    index += 1
            else:
                filename = clean_filename(filename)
                if not filename or filename in (".pdf", "_pdf", "_.pdf"):
                    filename = f"Файл_без_имени_{index}.pdf"
                full_path = os.path.join(download_path, filename)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'wb') as file:
                    file.write(response.content)
                total_size += len(response.content)
                pbar.update(1)
                log_file.write(f"{filename} ID: {index}\n")
                files_count += 1
                index += 1
 
        else:
            empty_files += 1
            log_file.write(f"Файл не найден ID:{index}\n")
            index += 1

            if empty_files >= 1000:
                end_time = int(time.time())
                finish_time = end_time - start_time
                result_message = end_calc(finish_time=finish_time)
                pbar.close()
                log_file.write(f"{result_message},было установленно {files_count} файлов общим объемом {total_size / (1024 * 1024):.2f} Мб")
                log_file.close()
                break           
    input("Загрузка завершена....")