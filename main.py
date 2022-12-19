from utilities import *

import argparse


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', type=str, choices=['anonymize', 'encrypt', 'decrypt'],
                        help='mode of operation')
    parser.add_argument('input_dir', type=str, help='input directory containing DICOM files')
    parser.add_argument('output_dir', type=str, help='output directory for processed DICOM files')
    args = parser.parse_args()

    # Create a mode configuration object
    mode_config = HardAnonymize()

    # Create a DicomChanger object
    changer = DicomChanger(mode_config, mode=args.mode)

    # Process all DICOM files in the input directory and save the output to the output directory
    changer.run_over_folder(args.input_dir, args.output_dir)

if __name__ == '__main__':
    main()
