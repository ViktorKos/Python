import sys
from pathlib import Path
import shutil
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor

categories = {
    'Images': ['.jpeg', '.png', '.jpg', '.svg'],
    'Videos': ['.avi', '.mp4', '.mov', '.mkv'],
    'Music': ['.mp3', '.ogg', '.wav', '.amr'],
    'Archives': ['.zip', '.tar', '.rar', '.gz'],
    'Documents': ['.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx', 'xls'],
    'Other': []
}


def normalize(line: str) -> str:
    cyr_to_lat_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h',
        'ґ': 'g', 'д': 'd', 'е': 'e', 'є': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i',
        'ї': 'i', 'й': 'i', 'к': 'k', 'л': 'l',
        'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
        'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'shch', 'ю': 'u', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H',
        'Ґ': 'G', 'Д': 'D', 'Е': 'E', 'Є': 'E',
        'Ж': 'ZH', 'З': 'Z', 'И': 'Y', 'І': 'I',
        'Ї': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L',
        'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P',
        'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'KH', 'Ц': 'TS', 'Ч': 'CH',
        'Ш': 'SH', 'Щ': 'SHCH', 'Ю': 'U', 'Я': 'YA',
    }
    for cyr, lat in cyr_to_lat_dict.items():
        if cyr in line:
            line = line.replace(cyr, lat)

    for i in range(len(line)):
        if line[i].isdigit() or line[i].isalpha():
            continue
        line = line.replace(line[i], '_')
    return line


def report(root_dir):
    print('Список файлів в кожній категорії:')
    for item in root_dir.iterdir():
        if item.is_dir():
            print(item.stem)
            for file in item.iterdir():
                print(f'    {file.stem}{file.suffix}')

    known_ext = set()
    unknown_ext = set()
    all_ext = []

    for values_list in categories.values():
        all_ext.extend(values_list)

    for item in root_dir.iterdir():
        if item.is_dir():
            for file in item.iterdir():
                if file.suffix.lower() in all_ext:
                    known_ext.add(file.suffix.lower())
                else:
                    unknown_ext.add(file.suffix.lower())

    print('')
    print('Перелік усіх відомих скрипту розширень, які зустрічаються в цільовій теці:')
    print(' '.join(map(str, known_ext)), end='\n\n')
    print('Перелік всіх розширень, які скрипту невідомі:')
    print(' '.join(map(str, unknown_ext)), end='\n\n')


def unpack(file: Path, destination_dir: Path) -> None:
    destination_dir = destination_dir.parent.joinpath(f'{destination_dir.stem}', )
    if destination_dir.exists():
        destination_dir = get_unique_name(destination_dir)
    shutil.unpack_archive(file.resolve(), destination_dir)
    file.unlink()


def get_unique_name(file: Path) -> Path:
    new_id = 1
    while file.exists():
        file = file.parent.joinpath(f'{file.stem}_{new_id}{file.suffix}')
    return file


def move_file(file: Path, root_dir: Path, category: str) -> None:
    destination_dir = root_dir.joinpath(category)
    if not destination_dir.exists():
        Path.mkdir(destination_dir)
    new_file_dist = destination_dir.joinpath(f'{normalize(file.stem)}{file.suffix}')
    if category == 'Archives':
        unpack(file, new_file_dist)
        return
    if new_file_dist.exists():
        new_file_dist = get_unique_name(new_file_dist)
    file.replace(new_file_dist)


def categorize(file: Path) -> str:
    for category, cat_ext in categories.items():
        if file.suffix.lower() in cat_ext:
            return category
    return 'Other'


def sorter(path: Path, root_dir: Path) -> None:
    with ThreadPoolExecutor() as executor:
        futures = []

        for item in path.iterdir():
            if item.is_file():
                file_category = categorize(item)
                futures.append(executor.submit(move_file, item, root_dir, file_category))
            elif (item.is_dir() and item.stem not in categories) or (item.is_dir() and item.parent != root_dir):
                futures.append(executor.submit(sorter, item, root_dir))

        for future in futures:
            future.result()

        for item in path.iterdir():
            if item.is_dir() and not any(item.iterdir()):
                item.rmdir()


def clear(file):
    try:
        file = Path(file)
        root_dir = Path(file).resolve()
    except IndexError:
        return "No path to folder"
    if not root_dir.exists():
        return 'Folder does not exists'

    sorter(file, root_dir)
    report(root_dir)