import os

current_directory = os.curdir
files_in_current_directory = os.listdir(current_directory)
# print(files_in_current_directory)
sorted_files = sorted(
    files_in_current_directory,
    key=lambda file: os.path.getmtime(os.path.join(current_directory, file)),
)
print(sorted_files)
