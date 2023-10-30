import pydicom
import os
from typing import List, Optional, Dict, Union, Tuple, Set

from cryptography.fernet import Fernet
from utilities.encryption_manager import detect_if_encrypted


def load_dcm_files(folder: str) -> List[str]:
    """
    Load DICOM files from a given folder.

    Parameters:
        folder (str): Path to the folder containing DICOM files.

    Returns:
        List[str]: List of paths to DICOM files.
    """
    dcm_files = []
    # Iterate through all files in the folder and its subfolders
    for root, _, files in os.walk(folder):
        for file in files:
            # If the file is a DICOM file, add its path to the list
            if is_file_a_dicom(os.path.join(root, file)):
                dcm_files.append(os.path.join(root, file))
    return dcm_files


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


def check_config(config: Optional[Dict[str, List[str]]]) -> Dict[str, List[str]]:
    """
    Check and return the given config dictionary.

    Parameters:
        config (Optional[Dict[str, List[str]]]): Configuration dictionary.

    Returns:
        Dict[str, List[str]]: Configuration dictionary.
    """
    if config is None:
        # Set default config if none is provided
        config = {
            "NonModify": [],
        }
    return config


def get_tags(folder: str) -> Set[Tuple[str, str, str]]:
    """
    Get unique tags from DICOM files in a given folder.

    Parameters:
        folder (str): Path to the folder containing DICOM files.

    Returns:
        Set[Tuple[str, str, str]]: Set of unique tags in the form (tag_flag, tag_name, value).
    """
    tags_set = set()

    # Read a representative DICOM file to get the tag values
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


def encrypt(string: Union[str, pydicom.multival.MultiValue], fernet: Fernet) -> Union[bytes, List[bytes]]:
    """
    Encrypt a string using a Fernet object.

    Parameters:
        string (Union[str, pydicom.multival.MultiValue]): String or MultiValue object to encrypt.
        fernet (Fernet): Fernet object for encryption.

    Returns:
        Union[bytes, List[bytes]]: Encrypted data.
    """
    if isinstance(string, pydicom.multival.MultiValue):
        # If the string is a pydicom MultiValue object, encrypt each value in the object
        return [
            fernet.encrypt((str(type(string)) + "%" + str(string)).encode())
            for _ in string
        ]
    # Otherwise, encrypt the string
    return fernet.encrypt((str(type(string)) + "%" + str(string)).encode())


def decrypt(string: bytes, fernet: Fernet) -> str:
    """
    Decrypt a string using a Fernet object.

    Parameters:
        string (bytes): Encrypted data.
        fernet (Fernet): Fernet object for decryption.

    Returns:
        str: Decrypted string.
    """
    # Decrypt the string and return the decoded result
    return fernet.decrypt(string).decode()
