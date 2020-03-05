import hashlib
import json
import os
import shutil
import hmac
from functools import reduce

from apscheduler.schedulers.background import BackgroundScheduler


class FileUtils():
    """
    Class for files processing
    """

    path = os.path.join(os.path.dirname(__file__), "..")
    replicas_path = os.path.join(path, "replicas")
    hashes = {}
    json_filename = os.path.join(path, "files.json")

    def __init__(self):
        if not bool(self.hashes) and os.path.exists(self.json_filename):
            with open(self.json_filename) as json_data:
                self.hashes = json.load(json_data)
        self.start_scheduler()

    def get_hash(self, filename):
        """
        Read json with filenames and hashes

        Returns:
            dict -- files and hashes
        """
        msg = ""
        d_hashes = {}
        if bool(self.hashes):
            replicas = self.hashes["replicas"]
        else:
            result = {"message": "HIDS failure. Please populate files."}, 500

        try:
            for replica in replicas:
                try:
                    dict_hashes = {
                        replica: {filename: replicas[replica][filename]}
                    }
                    msg = ""
                except Exception:
                    msg += f"'{filename}' not exist in '{replica}'; "
                d_hashes.update(dict_hashes)
            result = d_hashes, 200
        except Exception as e:
            if not result:
                result = {"message": e.strerror}, 400
        if msg != "":
            result = {"message": msg}, 400
        return result

    def check_file(self, filename, client_hash, token):
        """
        return:
            MAC
            or
            Integrity error
        """
        msg = ""
        replicas = self.get_hash(filename)
        if replicas[1] == 200:
            replicas = replicas[0]
            for replica in replicas:
                dict_hash = replicas[replica][filename]
                if client_hash == dict_hash:
                    result = self.mac(filename, dict_hash, token), 200
                    msg = ""
                    break
                else:
                    msg += f"Integrity error in {filename} for {replica}"
        else:
            result = replicas

        if msg != "":
            result = {"message": msg}, 400

        return result

    def mac(self, file_name, file_hash, token):

        mensaje = file_name + file_hash
        mac = hmac.new(mensaje.encode(), token.encode(), hashlib.sha256)
        return str(mac.digest())

    def get_hashes(self):
        """
        Read json with filenames and hashes

        Returns:
            dict -- files and hashes
        """
        if bool(self.hashes):
            result = self.hashes, 200
        else:
            result = {"message": "HIDS failure. Please populate files."}, 500

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

    def __file_to_hash(self, file):
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

        return self.files_hashes_to_dict(self.replicas_path), 201

    def daily_analysis(self):
        fecha_actual = datetime.now()
        file_logs = "logs-" + str(fecha_actual.month) + \
            "-" + str(fecha_actual.year) + ".log"
        file_logs_path = os.path.join(self.path, file_logs)
        with open(file_logs_path, "a+", encoding="utf-8") as f:
            f.write(
                "================== Analysis of " +
                fecha_actual.now().strftime("%d/%m/%Y")
                + " ==================\n"
            )
            for replica in self.hashes["replicas"].keys():
                dict_hashes_replica = self.hashes["replicas"][replica]
                for file_name in dict_hashes_replica.keys():
                    hash_dict = dict_hashes_replica[file_name]
                    hash_of_file_in_replica = self._file_to_hash(
                        os.path.join(self.replicas_path, replica, file_name))
                    if hash_dict != hash_of_file_in_replica:
                        f.write(
                            "INTEGRITY ERROR (" +
                            fecha_actual.now().strftime("%H:%M:%S %d/%m/%Y") +
                            "): '" + file_name + "' (" + replica + ")\n"
                        )
            f.write("\n")

    def export_dict_json(self):
        with open(self.json_filename, 'w') as json_file:
            json.dump(self.hashes, json_file)

    def start_scheduler(self):
        scheduler = BackgroundScheduler()

        # Para cambiar el intervalo, sustituir hours=24 por minutes= o seconds=
        scheduler.add_job(self.daily_analysis, "interval", hours=24)
        scheduler.add_job(self.export_dict_json, "interval", hours=1)

        scheduler.start()
        return {"message": "Daily Analysis started successfully"}, 200
