from datetime import datetime
from logging import exception
import os
import sys
import shutil
from pathlib import Path
from time import gmtime

foldersCatalog = {
    1: 'images',
    2: 'video',
    3: 'documents',
    4: 'audio',
    5: 'archives',
    6: 'other'
}

extentionsCatalog = {
    'JPEG': 1,
    'PNG': 1,
    'JPG': 1,
    'SVG': 1,
    'AVI': 2,
    'MP4': 2,
    'MOV': 2,
    'MKV': 2,
    'DOC': 3,
    'DOCX': 3,
    'TXT': 3,
    'PDF': 3,
    'XLSX': 3,
    'PPTX': 3,
    'MP3': 4,
    'OGG': 4,
    'WAV': 4,
    'AMR': 4,
    'ZIP': 5,
    'GZ': 5,
    'TAR': 5
}


def prepareTranslationMap() -> dict():
    CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
    CYR = tuple(CYRILLIC_SYMBOLS)
    LAT = (
        "a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
        "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g"
    )
    TRANSLATION_MAP = {}
    for c, l in zip(CYR, LAT):
        TRANSLATION_MAP[ord(c)] = l
        TRANSLATION_MAP[ord(c.upper())] = l.upper()
    return TRANSLATION_MAP


def normalize(fileName: str, map: dict()) -> str:
    translated = fileName.translate(map)
    for char in translated:
        if not(ord(char) >= ord('a') and ord(char) <= ord('z')
               or ord(char) >= ord('A') and ord(char) <= ord('Z')
               or char.isnumeric()):
            translated = translated.replace(char, '_')
    return translated


def listFiles(dirPath: str) -> list():
    files = list()

    def loopThroughFiles(dirPath: str):
        nonlocal files
        path = Path(dirPath)
        for fileObj in path.iterdir():
            if fileObj.is_file():
                files.append((fileObj.parent, fileObj.stem, fileObj.suffix))
            elif fileObj.is_dir() and not fileObj.name in foldersCatalog.values():
                loopThroughFiles(fileObj)
        return
    loopThroughFiles(dirPath)
    return files


def deleteEmptyFolders(dirPath: str):
    path = Path(dirPath)
    for fileObj in path.iterdir():
        if fileObj.is_dir() and not fileObj.name in foldersCatalog.values():
            shutil.rmtree(fileObj)
    return


def unzipArchives(dirPath: str):
    path = Path.joinpath(Path(dirPath), foldersCatalog[5])
    for fileObj in path.iterdir():
        if fileObj.is_file():
            try:
                shutil.unpack_archive(
                    filename=fileObj, extract_dir=Path.joinpath(
                        path, fileObj.stem)
                )
            except Exception:
                print(f"Cannot unzip file {fileObj.name}")
    return


def getTimestampStr() -> str:
    curTime = datetime.now()
    return f"_{curTime.tm_hour}{curTime.tm_min}{curTime.tm_sec}"


def main():
    translation_map = prepareTranslationMap()
    categorizedFiles = list()
    knownExtentions = set()
    unknownExtentions = set()
    rootFolder = sys.argv[1]
    rootPath = Path(rootFolder)
    if rootPath.exists():
        # create standard folders
        for folder in foldersCatalog.values():
            Path.mkdir(Path.joinpath(rootPath, folder),
                       parents=True, exist_ok=True)
        # parse files names and pathes
        files = listFiles(rootPath)
        for f in files:
            fDir = f[0]
            fName = f[1]
            fExtWithDot = f[2]
            newName = normalize(fName, translation_map)
            currentFileLocation = Path.joinpath(fDir, fName+fExtWithDot)
            extention = fExtWithDot[1:].upper()
            if extention in extentionsCatalog:
                folderId = extentionsCatalog[extention]
                knownExtentions.add(extention)
            else:
                folderId = 6  # other
                unknownExtentions.add(extention)
            newDir = Path.joinpath(rootPath, foldersCatalog[folderId])
            newFileLocation = Path.joinpath(newDir, newName+fExtWithDot)
            if newFileLocation.exists():
                # if file already exists add a timestamp
                timeStamp = getTimestampStr()
                newFileLocation = Path.joinpath(
                    newDir, newName+timeStamp+fExtWithDot)
            categorizedFiles.append(
                foldersCatalog[folderId] + ' \ ' + newName +
                fExtWithDot + '<--' + fName+fExtWithDot
            )
            try:
                shutil.move(currentFileLocation, newFileLocation)
            except:
                print(
                    f"Process error. Cannot move file from {currentFileLocation} to {newFileLocation}")
                raise
        deleteEmptyFolders(rootFolder)
        unzipArchives(rootFolder)
        # output
        print(f"Known extentions: {knownExtentions}")
        print(f"Unknown extentions: {unknownExtentions}")
        categorizedFiles.sort()
        for f in categorizedFiles:
            print(f)
    else:
        print(f"The path {rootFolder} does not exist")


if __name__ == '__main__':
    main()
    exit()