import os

# Use this like
# > with ChDir(my_dir):
# >   do_something()
# Then, the working directory will be set to my_dir, do_something() will be called,
# and the working directory will be set back.
class ChDir:
    def __init__(self, dir):
        self.dir = dir

    def __enter__(self):
        self.old_dir = os.getcwd()
        os.chdir(self.dir)

    def __exit__(self, type, value, traceback):
        os.chdir(self.old_dir)