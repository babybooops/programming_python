import csv
import hashlib
import pickle
from datetime import datetime
from pathlib import Path

from prettytable import PrettyTable


class HashFiles:

    def __init__(self, hash_type='md5') -> None:
        self.hash_type = hash_type
        self.processed_data = []

    def add_file(self, file_path: Path) -> None:
        data = {'full_path': Path(file_path).resolve(), 'date': datetime.now()}
        match self.hash_type:
            case 'md5':
                hash_algo = hashlib.md5()
            case 'sha1':
                hash_algo = hashlib.sha1()
            case 'sha256':
                hash_algo = hashlib.sha256()
            case 'sha512()':
                hash_algo = hashlib.sha512()
            case 'sha512()':
                hash_algo = hashlib.sha512()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_algo.update(chunk)
        data['checksum'] = hash_algo.hexdigest()
        self.processed_data.append(data)

    def add_directory(self, directory: Path) -> None:
        for file in Path(directory).glob('**/*'):
            self.add_file(file)

    def delete_file(self, file_path: Path) -> None:
        for i, file in enumerate(self.processed_data):
            if file['full_path'] == Path(file_path).resolve():
                self.processed_data.pop(i)

    @staticmethod
    def save_object(file_path: Path, obj: object) -> None:
        with open(file_path, 'wb') as f:
            pickle.dump(obj, f)

    @staticmethod
    def load_object(file_path: Path) -> object:
        with open(file_path, 'rb') as f:
            obj = pickle.load(f)
        return obj

    def export_to_csv(self, file_path: Path) -> None:
        keys = self.processed_data[0].keys()
        with open(file_path, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.processed_data)

    def print_table(self) -> None:
        table = PrettyTable()

        for c in self.processed_data[0].keys():
            table.add_column(c, [])

        for dct in self.processed_data:
            table.add_row([dct.get(c, "") for c in self.processed_data[0].keys()])
        print(table)
