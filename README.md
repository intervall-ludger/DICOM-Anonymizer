# DICOM Anonymizer

## Overview

The DICOM Anonymizer is a powerful tool built using PyQt6 that allows users to process and anonymize DICOM files. It provides various functionalities, such as changing tag values, using dummy values, deleting tags, and even encrypting tag values. The application also has a built-in search functionality to easily filter and locate specific tags within the DICOM files. Additionally, for ease of use, a standalone executable version is available for users who do not wish to run the application from source.

## Features

1. **Load DICOM Files**: Choose a directory containing your DICOM files to load and view the tags in a table format.
2. **Search Functionality**: Easily search for specific Tag (Flag), Tag Name, or Value using the built-in search fields.
3. **Tag Modification**: For each DICOM tag, decide whether to:
    - Keep the tag unchanged.
    - Replace the tag value with a dummy value.
    - Replace the tag value with a new value.
    - Delete the tag.
    - Encrypt the tag value.
4. **Save and Load Configurations**: Save your modification choices in a configuration file and load them later for consistent processing across multiple sessions.
5. **Encryption**: If any tags are selected for encryption, you can provide an encryption password. The selected tags will be encrypted using this password.
6. **Progress Tracking**: A progress bar displays the progress of processing the DICOM files.
7. **Auto-Select Functionality**: Automatically select tags based on predefined criteria (this needs to be defined in the `auto_select` utility).
8. **Standalone Executable**: For users who prefer not to run the application from the source, a standalone `.exe` version is available.

## Installation

### Prerequisites
- Python 3.8 or higher (for running from source).
- PyQt6 library (for running from source).
- pydicom library (for running from source).

### Steps

#### From Source:
1. Clone the repository:
   ```
   git clone [repository_url]
   ```
2. Navigate to the repository directory:
   ```
   cd DICOMAnonymizer
   ```
3. Install the required libraries:
   ```
   pip install -r requirements.txt
   ```

#### Using Standalone Executable:
1. Download the `DICOMAnonymizer.exe` from the releases section.
2. Run the executable.

## Usage

1. Launch the application (either from source or by running the executable).
2. Use the "Select Folder" button to load DICOM files.
3. View and modify the DICOM tags as required.
4. Use the "Save Config" option in the File menu to save your modifications for future sessions.
5. Use the "Process" button to apply your modifications to the DICOM files.
6. If any tags are encrypted, provide an encryption password.

## Contributing

Contributions are welcome! Please make sure to create a new branch for each feature or bugfix and submit a pull request.

## License

This project is licensed under the MIT License.

## Feedback

Feedback is greatly appreciated. If you find any bugs or have suggestions, please open an issue in the repository.
