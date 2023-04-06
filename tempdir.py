print("begin " + __name__)

import os

def tempdir(filename: str, temp_dir: str = "temp") -> str:
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    return os.path.join(temp_dir, filename)


if __name__ == "main":
    print(tempdir("AAAAAAAA.txt"))

print("end " + __name__)