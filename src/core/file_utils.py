import hashlib
import json
import os
import shutil
from functools import reduce


class FileUtils():
    """
    Class for files processing
    """

    path = os.path.join(os.path.dirname(__file__), "..")
    replicas_path = ""
    hashes = {}
    json_filename = os.path.join(path, "files.json")

    def get_hashes(self):
        """
        Read json with filenames and hashes

        Arguments:
            path {str} -- Path of json file

        Returns:
            dict -- files and hashes
        """
        if bool(self.hashes):
            result = self.hashes
        else:
            with open(self.json_filename) as json_data:
                result = json.load(json_data)
            self.hashes = result
        return result

    def files_hashes_to_dict(self, path):
        """
        Generate dictionary with files and hashes

        Arguments:
            path {str} -- Path files

        Returns:
            dict -- Dict with files and hashes
        """
        dir = {}
        rootdir = path.rstrip(os.sep)
        start = rootdir.rfind(os.sep) + 1
        for path, dirs, files in os.walk(rootdir):
            folders = path[start:].split(os.sep)
            subdir = {
                key: self._file_to_hash(
                    os.path.join(path, key)
                ) for key in files
            }
            parent = reduce(dict.get, folders[:-1], dir)
            parent[folders[-1]] = subdir
        with open(self.json_filename, 'w') as self.json_file:
            json.dump(dir, self.json_file)
        self.hashes = dir
        return dir

    def _file_to_hash(self, file):
        """
        Calculate file hash

        Arguments:
            file {str} -- Path of file

        Returns:
            integer -- hash
        """
        sha256_hash = hashlib.sha256()
        with open(file, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
            hash_file = sha256_hash.hexdigest()
        return hash_file

    def file_generator(self, num_replicas, num_files):
        """
        Generate files and replicas

        Arguments:
            path {str} -- Base path to generate files
            num_replicas {integer} -- Number of replicas
            num_files {integer} -- Number of files

        Returns:
            dict -- Dict with files and hashes
        """
        self.replicas_path = os.path.join(self.path, "replicas")
        # Delete all files
        if os.path.exists(self.replicas_path):
            shutil.rmtree(self.replicas_path)

        # Create folder
        os.mkdir(self.replicas_path)

        letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        num_letters = len(letters)

        for i in range(num_replicas):
            next = [""]
            directorio = "replica" + str(i)

            if not os.path.exists(os.path.join(self.replicas_path, directorio)):
                os.mkdir(os.path.join(self.replicas_path, directorio))

            for i in range(num_files):
                with open(
                        os.path.join(
                            self.replicas_path,
                            directorio,
                            f"archivo{i}.txt"
                        ), "w") as file:

                    if next[-1] == letters[-1]:
                        next.append(letters[0])
                    for i in range(len(next)):
                        if letters.index(next[i]) == num_letters - 1:
                            next[i] = "a"
                        else:
                            next[i] = letters[letters.index(next[i]) + 1]
                            break

                    file.write("".join(next))

        return self.files_hashes_to_dict(self.replicas_path)
