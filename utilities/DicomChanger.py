import os

import pydicom
from .helper_function import mk_dir, np, load_dcm_files, Fernet, encrypt, decrypt
from scipy.ndimage.filters import gaussian_filter
from pydicom.data import get_testdata_file
from copy import deepcopy
from .ModeConfigurations import AbstractModeConfiguration

class DicomChanger:
    def __init__(
        self, mode_config: AbstractModeConfiguration, mode: str = "anonymize", key=None
    ):
        # Validate that the mode is one of the allowed values
        assert mode in ["anonymize", "encrypt", "decrypt"]
        self.mode = mode
        self.key_cf = mode_config
        # Generate a key if none is provided
        if key is None:
            key = Fernet.generate_key()
        self.fernet = Fernet(key)
        self.errors = []

    def run_over_folder(self, dcm_folder: str, dcm_anonymize_folder: str = None):
        # Load all DICOM files in the folder
        dcm_files = load_dcm_files(dcm_folder)
        # Process each file
        for dcm_file in dcm_files:
            # Determine the output file path
            dcm_change_file = dcm_file.replace(dcm_folder, dcm_anonymize_folder)
            # Create the output directory if it doesn't exist
            mk_dir(os.path.dirname(dcm_change_file))
            # Process the file
            self.run_on_file(dcm_file, dcm_change_file)

    def run_on_file(self, dcm_file: str, dcm_anonymize_file: str):
        # Choose the appropriate processing method based on the mode
        if self.mode == "anonymize":
            self.anonymize(dcm_file, dcm_anonymize_file)
        elif self.mode == "encrypt":
            self.encrypt(dcm_file, dcm_anonymize_file)

    def anonymize(self, dcm_file: str, dcm_anonymize_file: str):
        # Load the DICOM file
        ds = pydicom.dcmread(dcm_file)
        # Remove private tags
        ds.remove_private_tags()
        # Load a default DICOM file to use as a template
        fpath = get_testdata_file("MR_small.dcm")
        default_ds = pydicom.dcmread(fpath)
        # Iterate of DICOM Tags
        for element in ds:
            if element.keyword in self.key_cf.change_false_keys():
                continue
            if element.keyword in default_ds:
                element_ = default_ds.get_item(element.keyword)
            else:
                element_ = element
                element_.clear()
            ds.__setitem__(element.keyword, element_)
        ds.save_as(dcm_anonymize_file)

    def encrypt(self, dcm_file: str, dcm_encrypt_file: str):
        # Load the DICOM file
        ds = pydicom.dcmread(dcm_file)
        # Iterate through all elements in the DICOM file
        for element in ds:
            # Skip elements that should not be modified
            if element.keyword in self.key_cf.change_false_keys():
                continue
            # Make a deep copy of the element
            element_ = deepcopy(element)
            try:
                # Encrypt the element's value
                element_.value = encrypt(element_.value, self.fernet)
                # Set the element in the DICOM dataset
                ds.__setitem__(element.keyword, element_)
            except ValueError:
                # If encryption fails, log the element's keyword
                self.errors.append(element.keyword)
                pass
            except TypeError:
                # If encryption fails, log the element's keyword
                self.errors.append(element.keyword)
                pass

        # Save the encrypted DICOM file
        ds.save_as(dcm_encrypt_file)
