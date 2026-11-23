# AssertionError: assert 'file_with_mark.txt' in ['C:\\Users\\Kokil Rana\\AppData\\Local\\Temp\\pytest-of-Kokil Rana\\pytest-3\\test_search_for_mark_mark_in_f0\\file_with_mark.txt']
# The previous code did not correctly handle the file path returned by the search function.
# I will modify the code to correctly extract the file name from the full path.

import os

def search_for_mark(directory):
    results = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                if 'Mark' in f.read():
                    results.append(file)
    return results