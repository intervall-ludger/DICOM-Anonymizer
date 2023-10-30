import pydicom
import nibabel as nib
import numpy as np
import os
import hashlib
from typing import List, Optional, Dict, Union

from cryptography.fernet import Fernet
from utilities.encryption_manager import detect_if_encrypted


# Load DICOM files from a given folder
def load_dcm_files(folder: str) -> List[str]:
    dcm_files = []
    # Iterate through all files in the folder and its subfolders
    for root, _, files in os.walk(folder):
        for file in files:
            # If the file is a DICOM file, add its path to the list
            if is_file_a_dicom(os.path.join(root, file)):
                dcm_files.append(os.path.join(root, file))
    return dcm_files


# Check if a file is a DICOM file
def is_file_a_dicom(file: str) -> bool:
    """
    Check if a file is a DICOM file.

    Parameters:
        file (str): Path to the file to identify.

    Returns:
        bool: True if the file is DICOM, False otherwise.
    """
    try:
        pydicom.dcmread(file)
    except pydicom.errors.InvalidDicomError:
        return False
    return True


# Check and return the given config dictionary
def check_config(config: Optional[Dict[str, List[str]]]) -> Dict[str, List[str]]:
    if config is None:
        # Set default config if none is provided
        config = {
            "NonModify": [],
        }
    return config


def get_tags(folder):
    tags_set = set()

    # Lesen Sie einen repräsentativen DICOM-Datei, um die Tag-Werte zu erhalten
    flags = []
    for representative_file in load_dcm_files(folder):
        ds = pydicom.dcmread(str(representative_file))

        if detect_if_encrypted(ds):
            raise ValueError
        for elem in ds:
            tag_flag = str(elem.tag)
            if tag_flag in flags:
                continue
            flags.append(tag_flag)
            tag_name = elem.keyword
            if tag_name:
                value = str(elem.value)[:20]
                tags_set.add((tag_flag, tag_name, value))
    return tags_set


# Encrypt a string using a Fernet object
def encrypt(
    string: Union[str, pydicom.multival.MultiValue], fernet: Fernet
) -> Union[bytes, List[bytes]]:
    if type(string) == pydicom.multival.MultiValue:
        # If the string is a pydicom MultiValue object, encrypt each value in the object
        return [
            fernet.encrypt((str(type(string)) + "%" + str(string)).encode())
            for _ in string
        ]
    # Otherwise, encrypt the string
    return fernet.encrypt((str(type(string)) + "%" + str(string)).encode())


# Decrypt a string using a Fernet object
def decrypt(string: bytes, fernet: Fernet) -> str:
    # Decrypt the string and return the decoded result
    return fernet.decrypt(string).decode()


if __name__ == "__main__":
    s = "1"
    b = 2
