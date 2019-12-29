from collections import namedtuple
import shutil
import os
import subprocess


FileType = namedtuple('FileType', 'source destination')

show = FileType('fetch_tv_tmp', '/volume1/video/tv/')
movie = FileType('fetch_movies_tmp', '/volume1/video/movies/')

extensions = ['mp4']


def quick_join(*a):
    return '/'.join(a)


class AFile(namedtuple('AFile', 'name source type')):
    @property
    def destination(self):
        return quick_join(
            self.type.destination,
            self.name[0].upper(),
            self.location,
            self.name
        )

    @property
    def dest_dir(self):
        return quick_join(
            self.type.destination,
            self.name[0].upper(),
            self.location
        )

    @property
    def location(self):
        return self.source.split('/')[-2]

    def __str__(self):
        return '{self.name}: {self.location} [{self.source} {self.destination}]'.format(self=self)


def find_files(t):
    """
    Find the files to move, return a list of tuples - location & name
    """
    walked_path = quick_join(os.environ['HOME'], t.source)
    files = []
    for dirpath, _, filenames in os.walk(walked_path):
        location = dirpath.replace(walked_path, '').strip('/')
        for f in filenames:
            if '.' not in f or f.split('.')[-1] not in extensions:
                continue
            a = AFile(f, quick_join(dirpath, f), t)
            print(a)
            files.append(a)
    return files


def move_files(file_list):
    """
    Iterate through the list of files, moving them into the correct location
    """
    for f in file_list:
        print('move', f.name, 'from', f.source, 'to', f.destination)
        try:
            os.makedirs(f.dest_dir)
        except FileExistsError as e:
            print(f.dest_dir, 'exists')
        shutil.move(f.source, f.destination)


def index_files(file_list):
    """
    Trigger synoindex for the newly added files
    """
    for f in file_list:
        result = subprocess.run(
            ['/usr/syno/bin/synoindex', '-a', f.destination]
        )
        print(result)


def run():
    for t in [show, movie]:
        to_migrate = find_files(t)
        move_files(to_migrate)
        index_files(to_migrate)


if __name__ == '__main__':
    run()
