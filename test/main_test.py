import unittest
from tempdir import TempDir
import subprocess
import os
import random
import string
import test_utils
from gitversionbuilder import main, utils


class IntegrationTest(unittest.TestCase, test_utils.CodeAsserts):
    def test_empty_git_python(self):
        with TempDir() as git_dir:
            with test_utils.TempFile() as out_file:
                with utils.ChDir(git_dir):
                    commit_id = self._setup_git_return_commit_id()
                expected = """
                        # ---------------------------------------------------
                        # This file is autogenerated by git-version-builder.
                        # DO NOT MODIFY!
                        # ---------------------------------------------------

                        VERSION_STRING = "master-g%s"
                        TAG_NAME = "master"
                        COMMITS_SINCE_TAG = 0
                        GIT_COMMIT_ID = "%s"
                    """ % (commit_id[0:7], commit_id[0:7])
                main.create_version_file(git_directory=git_dir, output_file=out_file, lang="python")
                self.assertCodeEqual(expected, self._read_file(out_file))

    def test_empty_git_cpp(self):
        with TempDir() as git_dir:
            with test_utils.TempFile() as out_file:
                with utils.ChDir(git_dir):
                    commit_id = self._setup_git_return_commit_id()
                expected = """
                        // ---------------------------------------------------
                        // This file is autogenerated by git-version-builder.
                        // DO NOT MODIFY!
                        // ---------------------------------------------------

                        #pragma once
                        #ifndef __GITVERSIONBUILDER__VERSION_H__
                        #define __GITVERSIONBUILDER__VERSION_H__

                        namespace version {
                          constexpr const char *VERSION_STRING = "master-g%s";
                          constexpr const char *TAG_NAME = "master";
                          constexpr const unsigned int COMMITS_SINCE_TAG = 0;
                          constexpr const char *GIT_COMMIT_ID = "%s";
                        }

                        #endif
                    """ % (commit_id[0:7], commit_id[0:7])
                main.create_version_file(git_directory=git_dir, output_file=out_file, lang="cpp")
                self.assertCodeEqual(expected, self._read_file(out_file))

    def test_tagged_git(self):
        with TempDir() as git_dir:
            with test_utils.TempFile() as out_file:
                with utils.ChDir(git_dir):
                    commit_id = self._setup_git_return_commit_id()
                    self._create_git_tag("1.0.1")
                expected = """
                        # ---------------------------------------------------
                        # This file is autogenerated by git-version-builder.
                        # DO NOT MODIFY!
                        # ---------------------------------------------------

                        VERSION_STRING = "1.0.1"
                        TAG_NAME = "1.0.1"
                        COMMITS_SINCE_TAG = 0
                        GIT_COMMIT_ID = "%s"
                    """ % commit_id[0:7]
                main.create_version_file(git_directory=git_dir, output_file=out_file, lang="python")
                self.assertCodeEqual(expected, self._read_file(out_file))

    def test_tagged_git_with_commits_after_tag(self):
        with TempDir() as git_dir:
            with test_utils.TempFile() as out_file:
                with utils.ChDir(git_dir):
                    self._setup_git_return_commit_id()
                    self._create_git_tag("1.0.1")
                    commit_id = self._create_git_commit()
                expected = """
                        # ---------------------------------------------------
                        # This file is autogenerated by git-version-builder.
                        # DO NOT MODIFY!
                        # ---------------------------------------------------

                        VERSION_STRING = "1.0.1-1-g%s"
                        TAG_NAME = "1.0.1"
                        COMMITS_SINCE_TAG = 1
                        GIT_COMMIT_ID = "%s"
                    """ % (commit_id[0:7], commit_id[0:7])
                main.create_version_file(git_directory=git_dir, output_file=out_file, lang="python")
                self.assertCodeEqual(expected, self._read_file(out_file))

    def _setup_git_return_commit_id(self):
        with open(os.devnull, 'w') as devnull:
            subprocess.check_call(["git", "init"], stdout=devnull)
            return self._create_git_commit()

    def _create_git_commit(self):
        filename = self._random_string(10)
        with open(os.devnull, 'w') as devnull:
            subprocess.check_call(["touch", filename], stdout=devnull)
            subprocess.check_call(["git", "add", filename], stdout=devnull)
            subprocess.check_call(["git", "commit", "-m", "message"], stdout=devnull)
            commit_id = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            return commit_id

    def _random_string(self, length):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

    def _create_git_tag(self, tag_name):
        with open(os.devnull, 'w') as devnull:
            subprocess.check_call(["git", "tag", tag_name], stdout=devnull)

    def _read_file(self, filename):
        with open(filename, 'r') as open_file:
            return open_file.read()

if __name__ == '__main__':
    unittest.main()
