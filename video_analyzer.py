import csv
import datetime
import hashlib
import json
import math
import time
from os import walk, stat, mkdir, listdir, remove
from os.path import abspath, exists, isfile
from pathlib import Path

import cv2
from PIL import Image, ImageDraw, ImageFont
from pymediainfo import MediaInfo
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import *
from db import VideoInfo, AudioInfo, Base


class VideoAnalyzer:
    """Основной класс"""

    def __init__(self, path: str) -> None:
        """Конструктор класса. Создаёт объект класса на основе переданной директории
        Атрибуты:
        path -- путь к директории, которую нужно просканировать
        """
        print("Идет подключение к базе данных")
        print("Подключение установлено")
        self.files_dict = {}
        self.path = path

    def get_files_dict(self) -> None:
        """Рекурсивно находит файлы в директории self.path
            и фильтрует их, исходя из расширений, указанных в конфигах
        """
        if (isfile(self.path)):
            self.files_dict[abspath(self.path)] = {}
            return
        print(f"Получение всех вложенных файлов из директории '{self.path}'.")
        needle_files = []  # получаем список всех файлов в переданном каталоге
        for root, dirs, files in walk(self.path):
            for file in files:
                res = root + "\\" + file
                needle_files.append(res)

        print("Фильтрация файлов по расширениям.")
        result = {}  # словарь с ключом путь и значением словарь
        for file in needle_files:  # фильтруем список файлов, оставляя только файлы с нужными расширениями
            for ext in FILE_EXTENSIONS:
                if file[-len(ext):] == ext:
                    res = abspath(file)
                    result[res] = {}
        self.files_dict = result
        print(result)

    def get_video_metadata(self, file: str) -> None:
        """получает метаданные файла и записывает их в поле класса
        """
        positions = {
            "bitrate": cv2.CAP_PROP_BITRATE,  # битрейт видео
            "fps": cv2.CAP_PROP_FPS,  # количество кадров в секунду
            "frames": cv2.CAP_PROP_FRAME_COUNT,  # количество кадров в видеофайле
            "width": cv2.CAP_PROP_FRAME_WIDTH,  # ширина кадра
            "height": cv2.CAP_PROP_FRAME_HEIGHT,  # высота кадра
        }
        vid_capture = cv2.VideoCapture(file)

        metadata = {}
        for pos in positions:
            metadata[pos] = vid_capture.get(positions[pos])
        media_info = json.loads(MediaInfo.parse(file, output="JSON"))
        for i in media_info["media"]["track"]:
            if i["@type"] == "Video":
                metadata["length"] = i["Duration"]
                metadata["codec"] = i['Format_Commercial']  # видео кодек
                metadata["colorDepth"] = i['BitDepth']  # глубина цвета
                metadata["colorSpace"] = i['ColorSpace']  # цветовое пространство
        self.files_dict[file]['metadata'] = metadata

    def get_file_attributes(self, file: str) -> None:
        """Получает системные атрибуты для переданного файла
        
        Keyword arguments:
        file -- файл, для которого получаются атрибуты
        """

        attributes_dict = {}
        attributes = stat(file)
        attributes_dict['cdate'] = datetime.datetime.fromtimestamp(attributes.st_ctime)  # дата создания
        attributes_dict['uid'] = attributes.st_uid  # id владельца файла в системе
        attributes_dict['size'] = attributes.st_size  # Размер файла
        attributes_dict['mtime'] = datetime.datetime.fromtimestamp(
            attributes.st_mtime)  # Время последнего изменения файла (в сек)
        self.files_dict[file]['attributes'] = attributes_dict

    def get_file_audio_attributes(self, file: str) -> None:
        media_info = json.loads(MediaInfo.parse(file, output="JSON"))
        audio_dict = []
        for i in media_info["media"]["track"]:
            if i["@type"] == "Audio":
                audio_dict.append({
                    "audioBitrate": i["BitRate"],  # аудио битрейт
                    "channels": i["Channels"],  # количество каналов
                    "samplingRate": i["SamplingRate"],  # частота дискретизации
                    "audioCodec": i["Format_String"]  # аудио кодек
                })
        self.files_dict[file]['audio_attributes'] = audio_dict

    def divisorGenerator(self, n):
        large_divisors = []
        for i in range(1, int(math.sqrt(n) + 1)):
            if n % i == 0:
                yield i
                if i * i != n:
                    large_divisors.append(n // i)
        for divisor in reversed(large_divisors):
            yield divisor

    def create_thumbnails_by_steps(self, file: str, step=STEP) -> str:
        """Создаёт раскадровку для каждого видеофайла по заданному количеству секунд и возвращает путь к директории, где она лежит
        """
        videoCapture = cv2.VideoCapture(file)  # открываем видео

        frames = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)  # считываем общее количество кадров видеофайла
        fps = videoCapture.get(cv2.CAP_PROP_FPS)  # считываем количество кадров в секунду у видеофайла
        duration = frames // fps  # подсчитываем продолжительность видео

        if not exists(THUMBNAILS_PATH):  # создаём каталог для раскадровок (если ещё не создан)
            mkdir(THUMBNAILS_PATH)

        file_thumbnails_path = f"{THUMBNAILS_PATH}\\file_id({Path(file).stem})"  # задаем путь для сохранения кадров

        if not exists(file_thumbnails_path):
            mkdir(file_thumbnails_path)

        for file in listdir(file_thumbnails_path):  # очищаем каталог от уже имеющихся раскадровок
            remove(f"{file_thumbnails_path}\\{file}")

        second = 0  # установка нулевого кадра
        success = True

        while success and second <= duration:  # Создаём изображение с кадром из видео каждые STEP секунд
            videoCapture.set(cv2.CAP_PROP_POS_MSEC, second * 1000)  # сдвиг на каждые 10 сек видео
            success, image = videoCapture.read()
            if success:
                cv2.imwrite(file_thumbnails_path + f"\\frame_({second})_second{THUMBNAIL_EXTENSION}",
                            image)  # сохраняем в папку
                alpha_image = Image.open(file_thumbnails_path + f"\\frame_({second})_second{THUMBNAIL_EXTENSION}")
                draw = ImageDraw.Draw(alpha_image)
                draw.text((alpha_image.size[0], alpha_image.size[1]), time.strftime('%H:%M:%S', time.gmtime(second)),
                          'white', anchor='rb', font=ImageFont.truetype("arial.ttf", 90))
                alpha_image.save(file_thumbnails_path + f"\\frame_({second})_second{THUMBNAIL_EXTENSION}")
                second += step
            else:
                pass

        videoCapture.release()  # удаляем объекты из памяти
        cv2.destroyAllWindows()
        image_for_size = Image.open(file_thumbnails_path + f"\\frame_({second - step})_second{THUMBNAIL_EXTENSION}")
        divisors = list(self.divisorGenerator(duration // step))
        print(divisors)
        if len(divisors) % 2 == 0:
            x = int(divisors[len(divisors) // 2])
            y = int((duration // step) // x)
        elif len(divisors) == 1:
            x = 1
            y = 0
        else:
            x = int(divisors[len(divisors) // 2 + 1])
            y = int((duration // step) // x)
        new_image = Image.new("RGB",
                              (image_for_size.size[0] * x,
                               image_for_size.size[1] * y), 'white')
        for i, thumbnail in enumerate(Path(f"{file_thumbnails_path}").glob("*.*")):
            alpha_image = Image.open(thumbnail)
            column = i % x
            row = i // x
            if y != 0:
                new_image.paste(alpha_image, (alpha_image.size[0] * column, alpha_image.size[1] * row))
            else:
                new_image.paste(alpha_image, (alpha_image.size[0] * column, 0))
        new_image.save(f"{file_thumbnails_path}/final_thumbnail{THUMBNAIL_EXTENSION}")
        return file_thumbnails_path

    def create_thumbnails_by_count(self, file: str, count=COUNT) -> str:
        """Создаёт раскадровку для каждого видеофайла по заданному количеству кадров и возвращает путь к диерктории, где она лежит
        """
        videoCapture = cv2.VideoCapture(file)  # открываем видео

        frames = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)  # считываем общее количество кадров видеофайла
        fps = videoCapture.get(cv2.CAP_PROP_FPS)  # считываем количество кадров в секунду у видеофайла
        duration = frames // fps  # подсчитываем продолжительность видео

        if not exists(THUMBNAILS_PATH):  # создаём каталог для раскадровок (если ещё не создан)
            mkdir(THUMBNAILS_PATH)

        file_thumbnails_path = f"{THUMBNAILS_PATH}\\file_id({Path(file).stem})"  # задаем путь для сохранения кадров

        if not exists(file_thumbnails_path):
            mkdir(file_thumbnails_path)

        for file in listdir(file_thumbnails_path):  # очищаем каталог от уже имеющихся раскадровок
            remove(f"{file_thumbnails_path}\\{file}")

        second = 0  # установка нулевого кадра
        success = True

        while success and second <= duration:  # Создаём изображение с кадром из видео каждые STEP секунд
            videoCapture.set(cv2.CAP_PROP_POS_MSEC, second * 1000)  # сдвиг на каждые 10 сек видео
            success, image = videoCapture.read()
            if success:
                cv2.imwrite(file_thumbnails_path + f"\\frame_({second})_second{THUMBNAIL_EXTENSION}",
                            image)  # сохраняем в папку
                alpha_image = Image.open(file_thumbnails_path + f"\\frame_({second})_second{THUMBNAIL_EXTENSION}")
                draw = ImageDraw.Draw(alpha_image)
                draw.text((alpha_image.size[0], alpha_image.size[1]), time.strftime('%H:%M:%S', time.gmtime(second)),
                          'white', anchor='rb', font=ImageFont.truetype("arial.ttf", 90))
                alpha_image.save(file_thumbnails_path + f"\\frame_({second})_second{THUMBNAIL_EXTENSION}")
                second += duration // count
            else:
                pass

        videoCapture.release()  # удаляем объекты из памяти
        cv2.destroyAllWindows()
        image_for_size = Image.open(
            file_thumbnails_path + f"\\frame_({second - duration // count})_second{THUMBNAIL_EXTENSION}")
        divisors = list(self.divisorGenerator(duration // (duration // count)))
        if len(divisors) % 2 == 0:
            x = int(divisors[len(divisors) // 2])
            y = int((duration // (duration // count)) // x)
        elif len(divisors) == 1:
            x = 1
            y = 0
        else:
            x = int(divisors[len(divisors) // 2 + 1])
            y = int((duration // (duration // count)) // x)
        new_image = Image.new("RGB",
                              (image_for_size.size[0] * x,
                               image_for_size.size[1] * y), 'white')
        for i, thumbnail in enumerate(Path(f"{file_thumbnails_path}").glob("*.*")):
            alpha_image = Image.open(thumbnail)
            column = i % x
            row = i // x
            if y != 0:
                new_image.paste(alpha_image, (alpha_image.size[0] * column, alpha_image.size[1] * row))
            else:
                new_image.paste(alpha_image, (alpha_image.size[0] * column, 0))
        new_image.save(f"{file_thumbnails_path}/final_thumbnail{THUMBNAIL_EXTENSION}")
        return file_thumbnails_path

    def hash_file(self, file: str) -> None:
        # make a hash object
        h = hashlib.sha1()

        # open file for reading in binary mode
        with open(file, 'rb') as f:
            # loop till the end of the file
            chunk = 0
            while chunk != b'':
                # read only 1024 bytes at a time
                chunk = f.read(1024)
                h.update(chunk)

        # save the hex representation of digest
        self.files_dict[file]['hash'] = h.hexdigest()

    def add_files_to_db(self) -> None:
        """Записывает данные в базу данных
        """
        for i in self.files_dict.keys():
            self.get_video_metadata(i)
            self.get_file_attributes(i)
            self.get_file_audio_attributes(i)
            self.hash_file(i)
        engine = create_engine(f"sqlite:///{DB_FILENAME}", echo=False)
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            for path, data in self.files_dict.items():
                if (session.query(VideoInfo).filter(VideoInfo.hash == data["hash"]).first() is not None):
                    session.query(VideoInfo).filter(VideoInfo.hash == data["hash"]).update({
                        "hash": data["hash"],
                        "name": Path(path).stem,
                        "format": Path(path).suffix,
                        "size": data["attributes"]["size"],
                        "length": data["metadata"]["length"],
                        "videoBitrate": data["metadata"]["bitrate"],
                        "dateCreate": data["attributes"]["cdate"],
                        "dateChange": data["attributes"]["mtime"],
                        "owner": data["attributes"]["uid"],
                        "path": path,
                        "frameWidth": data["metadata"]["width"],
                        "frameHeight": data["metadata"]["height"],
                        "fps": data["metadata"]["fps"],
                        "frames": data["metadata"]["frames"],
                        "videoCodec": data["metadata"]["codec"],
                        "colorDepth": data["metadata"]["colorDepth"],
                        "colorSpace": data["metadata"]["colorSpace"]
                    })
                    for i, audio in enumerate(data["audio_attributes"]):
                        # обновление информации аудио
                        session.query(AudioInfo).filter(AudioInfo.video_id == session.query(VideoInfo.id).filter(
                            VideoInfo.hash == data["hash"])).update({
                            "audioBitrate": audio["audioBitrate"],
                            "channels": audio["channels"],
                            "samplingRate": audio["samplingRate"],
                            "audioCodec": audio["audioCodec"],
                        })
                    session.commit()
                    continue
                video = VideoInfo(
                    hash=data["hash"],
                    name=Path(path).stem,
                    format=Path(path).suffix,
                    size=data["attributes"]["size"],
                    length=data["metadata"]["length"],
                    videoBitrate=data["metadata"]["bitrate"],
                    dateCreate=data["attributes"]["cdate"],
                    dateChange=data["attributes"]["mtime"],
                    owner=data["attributes"]["uid"],
                    path=path,
                    frameWidth=data["metadata"]["width"],
                    frameHeight=data["metadata"]["height"],
                    fps=data["metadata"]["fps"],
                    frames=data["metadata"]["frames"],
                    videoCodec=data["metadata"]["codec"],
                    colorDepth=data["metadata"]["colorDepth"],
                    colorSpace=data["metadata"]["colorSpace"]
                )
                session.add(video)
                session.flush()
                for track in data['audio_attributes']:
                    audio = AudioInfo(
                        video_id=video.id,
                        audioBitrate=track["audioBitrate"],
                        channels=track["channels"],
                        samplingRate=track["samplingRate"],
                        audioCodec=track["audioCodec"],
                    )
                    session.add(audio)
                session.commit()

    def db_to_csv(self, path=".") -> None:
        with open(f'{path}/{DB_TBLNAME}.csv', 'w', encoding='utf-8') as f:
            outcsv = csv.writer(f)
            engine = create_engine(f"sqlite:///{DB_FILENAME}", echo=False)
            with Session(engine) as session:
                records = session.query(VideoInfo).all()
                [outcsv.writerow([getattr(curr, column.name) for column in VideoInfo.__mapper__.columns]) for curr in
                 records]
        with open(f'{path}/{DB_TBLNAME}_audio.csv', 'w', encoding='utf-8') as f:
            outcsv = csv.writer(f)
            engine = create_engine(f"sqlite:///{DB_FILENAME}", echo=False)
            with Session(engine) as session:
                records = session.query(AudioInfo).all()
                [outcsv.writerow([getattr(curr, column.name) for column in AudioInfo.__mapper__.columns]) for curr in
                 records]
