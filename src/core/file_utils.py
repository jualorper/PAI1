import hashlib
import json
import os
import shutil


def file_generator(path, num_replicas, num_files):
    """
    Generate files and replicas

    Arguments:
        path {str} -- Base path to generate files
        num_replicas {integer} -- Number of replicas
        num_files {integer} -- Number of files

    Returns:
        dict -- Dict with files and hashes
    """
    path = os.path.join(path, "replicas")
    # Delete all files
    shutil.rmtree(path)

    if not os.path.exists(path):
        os.mkdir(path)

    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    num_letters = len(letters)

    for i in range(num_replicas):
        next = [""]
        directorio = "replica" + str(i)

        if not os.path.exists(os.path.join(path, directorio)):
            os.mkdir(os.path.join(path, directorio))

        for i in range(num_files):
            with open(
                    os.path.join(
                        path,
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

    return files_hashes_to_dict(path)


def files_hashes_to_dict(path):
    """
    Generate dictionary with files and hashes

    Arguments:
        path {str} -- Path files

    Returns:
        dict -- Dict with files and hashes
    """
    d = {'name': os.path.basename(path)}
    if os.path.isdir(path):
        d['children'] = [
            files_hashes_to_dict(os.path.join(path, x))
            for x in os.listdir(path)
        ]
    else:
        d['hash'] = _file_to_hash(path)

    with open('files.json', 'w') as json_file:
        json.dump(d, json_file)
    return d


def _file_to_hash(file):
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
