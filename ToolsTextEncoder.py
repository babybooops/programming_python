import re

from unicodedata import normalize


class Encoder:
    @staticmethod
    def rot13_text(string: str) -> str:
        chars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
        trans = chars[13:] + chars[:13]
        rot_char = lambda c: trans[chars.find(c)] if chars.find(c) > -1 else c
        return ''.join(rot_char(c) for c in string)

    @staticmethod
    def bacon_text(message: str) -> str:
        lookup = {'A': 'aaaaa', 'B': 'aaaab', 'C': 'aaaba', 'D': 'aaabb', 'E': 'aabaa',
                  'F': 'aabab', 'G': 'aabba', 'H': 'aabbb', 'I': 'abaaa', 'J': 'abaab',
                  'K': 'ababa', 'L': 'ababb', 'M': 'abbaa', 'N': 'abbab', 'O': 'abbba',
                  'P': 'abbbb', 'Q': 'baaaa', 'R': 'baaab', 'S': 'baaba', 'T': 'baabb',
                  'U': 'babaa', 'V': 'babab', 'W': 'babba', 'X': 'babbb', 'Y': 'bbaaa', 'Z': 'bbaab'}
        cipher = ''
        for letter in message.upper():
            if letter != ' ':
                cipher += lookup[letter]
            else:
                cipher += ' '

        return cipher

    @staticmethod
    def rot13_file(path_to_file_read: str, path_to_file_write: str) -> str:
        with open(path_to_file_read, 'r') as f:
            string = f.read()
        chars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
        trans = chars[13:] + chars[:13]
        rot_char = lambda c: trans[chars.find(c)] if chars.find(c) > -1 else c
        with open(path_to_file_write, 'w') as f:
            f.write(''.join(rot_char(c) for c in string))

    @staticmethod
    def bacon_file(path_to_file_read: str, path_to_file_write: str) -> str:
        with open(path_to_file_read, 'r') as f:
            message = f.read()
        lookup = {'A': 'aaaaa', 'B': 'aaaab', 'C': 'aaaba', 'D': 'aaabb', 'E': 'aabaa',
                  'F': 'aabab', 'G': 'aabba', 'H': 'aabbb', 'I': 'abaaa', 'J': 'abaab',
                  'K': 'ababa', 'L': 'ababb', 'M': 'abbaa', 'N': 'abbab', 'O': 'abbba',
                  'P': 'abbbb', 'Q': 'baaaa', 'R': 'baaab', 'S': 'baaba', 'T': 'baabb',
                  'U': 'babaa', 'V': 'babab', 'W': 'babba', 'X': 'babbb', 'Y': 'bbaaa', 'Z': 'bbaab'}
        cipher = ''
        for letter in message.upper().replace(',', '').replace('.', ''):
            if letter != ' ':
                cipher += lookup[letter]
            else:
                cipher += ' '
        with open(path_to_file_write, 'w') as f:
            f.write(cipher)
