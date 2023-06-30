import warnings

import click

import config
from video_analyzer import VideoAnalyzer
from sqlalchemy import exc as sa_exc


@click.command()
@click.option('--video', default='test/', prompt="Путь к файлу или папке с видео", help='Файл или директория с видео')
@click.option('--file_types', prompt='Типы файлов',
              help='Типы видео', default=config.FILE_EXTENSIONS)
@click.option('--thumbnail_path', prompt='Путь к превью',
              help='Путь к превью', default=config.THUMBNAILS_PATH)
@click.option('--thumbnail_type', prompt='Тип файла превью',
              help='Тип файла превью', default=config.THUMBNAIL_EXTENSION)
@click.option('--preview_count', prompt='Количество превью',
              help='Количество превью', nargs=2, default=('./test/music.mp4', config.COUNT), type=(str, int))
@click.option('--preview_steps', prompt='Шаг для превью',
              help='Шаг для превью', nargs=2, default=('./test/parallax.mp4', config.STEP), type=(str, int))
@click.option('--table_name', prompt='Название таблицы',
              help='Название таблицы', default=config.DB_TBLNAME)
@click.option('--import_to_csv', prompt='Импортировать в csv',
              help='Импортировать в csv', default=True)
def main(video, file_types, thumbnail_path, thumbnail_type, preview_count, preview_steps, table_name, import_to_csv):
    """Консольное приложение для получения информации о видео"""
    config.FILES_EXTENSION = file_types
    config.THUMBNAILS_PATH = thumbnail_path
    config.THUMBNAIL_EXTENSION = thumbnail_type
    config.STEP = preview_steps[1]
    config.COUNT = preview_count[1]
    config.DB_TBLNAME = table_name
    video_info = VideoAnalyzer(video)
    video_info.get_files_dict()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=sa_exc.SAWarning)
        video_info.add_files_to_db()
    if thumbnail_path or thumbnail_type or preview_count or preview_steps:
        if preview_count:
            video_info.create_thumbnails_by_count(preview_count[0], preview_count[1])
        if preview_steps:
            video_info.create_thumbnails_by_steps(preview_steps[0], preview_steps[1])
    if import_to_csv:
        video_info.db_to_csv()


if __name__ == '__main__':
    main()
