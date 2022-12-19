# DICOM-Anonymizer
The DICOM-Anonymizer used the DicomChanger class which provides methods for anonymizing, encrypting, and decrypting DICOM files. It takes a mode configuration object that specifies which elements in the DICOM file should be modified and how.

## Environment Setup

Alternatively, you can use the Soruce code, which has the advantage that you can make changes.

1. Install [python3.10](https://www.python.org/downloads/release/python-3100/)
2. Clone MaskRegistration Repository
 ```bash
git clone https://github.com/ludgerradke/DICOM-Anonymizer
 ```
3. Open DICOM-Anonymizer
 ```bash
cd DICOM-Anonymizer
 ```
4. Install requirements.
 ```bash
 pip install -r requirements.txt
 ```

## Usage

### **Use DICOM-Anonymizer with CLI**

To use the Dicom-Anonymizer function, you can call it from the command line as follows:

````bash
python main.py anonymize /path/to/input/folder /path/to/output/folder
````

This will anonymize all DICOM files in the **/path/to/input/folder** and save the output to **/path/to/output/folder**.

You can specify 'encrypt' or 'decrypt' as the mode instead of 'anonymize' to perform encryption or decryption on the DICOM files.

````bash
python main.py encrypt /path/to/input/folder /path/to/output/folder
````

````bash
python main.py decrypt /path/to/input/folder /path/to/output/folder
````

### **Use DICOM-Anonymizer with Python Code**

````python
from utilities.ModeConfigurations import HardAnonymize
from utilities.DicomChanger import DicomChanger

# Create a mode configuration object
mode_config = HardAnonymize()

# Create a DicomChanger object in anonymize mode
changer = DicomChanger(mode_config, mode='anonymize')

# Specify the input and output directories
input_dir = '/path/to/input/folder'
output_dir = '/path/to/output/folder'

# Anonymize all DICOM files in the input directory and save the output to the output directory
changer.run_over_folder(input_dir, output_dir)
````
Note: The input directory should contain DICOM files, and the output directory should be a new or empty directory where the anonymized DICOM files will be saved.

To use the DicomChanger in encrypt or decrypt mode, simply pass the appropriate mode string ('encrypt' or 'decrypt') to the constructor. The run_over_folder and run_on_file methods can then be used in the same way to process the DICOM files.

For example, to encrypt the DICOM files in the input directory and save the output to the output directory:

````python
# Create a DicomChanger object in encrypt mode
changer = DicomChanger(mode_config, mode='encrypt')

# Encrypt all DICOM files in the input directory and save the output to the output directory
changer.run_over_folder(input_dir, output_dir)
````

To decrypt the encrypted DICOM files in the input directory and save the output to the output directory:

```python
# Create a DicomChanger object in decrypt mode
changer = DicomChanger(mode_config, mode='decrypt')

# Decrypt all DICOM files in the input directory and save the output to the output directory
changer.run_over_folder(input_dir, output_dir)
```


## DicomChanger (Documentation)

**Attributes**:

- mode (str): The mode of operation for the DicomChanger ('anonymize', 'encrypt', 'decrypt').
- key_cf (AbstractModeConfiguration): The mode configuration object.
- fernet (Fernet): The Fernet object used for encrypting and decrypting DICOM elements.
- errors (List[str]): A list of keywords for DICOM elements that failed to be encrypted or decrypted.

**Methods**:

- run_over_folder(self, dcm_folder: str, dcm_anonymize_folder: str = None): Processes all DICOM files in the specified folder. The processed files will be saved to the `dcm_anonymize_folder`.
- run_on_file(self, dcm_file: str, dcm_anonymize_file: str): Processes a single DICOM file.
- anonymize(self, dcm_file: str, dcm_anonymize_file: str): Anonymizes a DICOM file by replacing all specified elements with default values.
- encrypt(self, dcm_file: str, dcm_encrypt_file: str): Encrypts the specified elements in a DICOM file.

## Contributing

Everyone is welcome to create an issue or pull request for this project. If you have found a bug or have an idea for an improvement, we encourage you to open an issue or submit a pull request.

Please make sure to use the GitHooks provided with the project to ensure that your code adheres to the style guidelines and passes all tests before submitting a pull request. This will make it easier for the maintainers to review and merge your contribution.

**Git hocks**
Install "pre-commit"
```bash
pip install pre-commit
```

then run:
```bash
pre-commit install
```

## License
[GNU General Public License 3](https://www.gnu.org/licenses/gpl-3.0.html)

The GNU General Public License is a free, copyleft license for software and other kinds of works.
