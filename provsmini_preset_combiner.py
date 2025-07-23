import argparse
import logging
from pathlib import Path

PREAMBLE = bytes.fromhex('F000203200013310')
TERMINATOR = bytes.fromhex('F7')


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Combines SysEx preset files for bulk transmission to the Behringer Pro VS Mini synthesizer.')

    parser.add_argument(
        'directory',
        help='Directory to get the preset files from. Only the first 32 files are combined!')
    parser.add_argument(
        '-e', '--extension',
        default='syx',
        help='Extension of the files, can use globs. Default is "syx".')
    parser.add_argument(
        '-o', '--output',
        help='Path for the combined preset file. Defaults to "combined.syx" in the source directory.')
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        default=False,
        help='Output messages about operations being carried out.')

    return parser.parse_args()


def combine_input(input_path, extension):
    sysex_contents = []

    sysex_filepaths = list(input_path.glob(f'*.{extension}'))
    if len(sysex_filepaths) == 0:
        raise FileNotFoundError('No matching files found!')
    logging.info(f'Found {len(sysex_filepaths)} SysEx files in {input_path.absolute()}')
    logging.debug(f'SysEx files found:\n{'\n'.join(sysex_filepath.as_posix() for sysex_filepath in sysex_filepaths)}')

    for sysex_filepath in sysex_filepaths:
        sysex_content = sysex_filepath.read_bytes()
        if sysex_content.startswith(PREAMBLE):
            logging.warning(f'Skipping combined file {sysex_filepath.name}')
            continue
        if not (sysex_content.startswith(PREAMBLE[:-1]) and sysex_content.endswith(TERMINATOR) and len(sysex_content) == 75):
            logging.warning(f'Skipping file with unrecognized format: {sysex_filepath.name}')
            continue
        preset_name = sysex_content[63:71].decode('ascii').rstrip()
        if len(sysex_contents) == 32:
            logging.warning(f'Skipping file above the 32-preset limit: {sysex_filepath.name} ({preset_name})')
            continue
        logging.info(f'Adding {sysex_filepath.name} ({preset_name})')
        logging.debug(f'File contents:\n{sysex_content.hex()}')
        sysex_contents.append(sysex_content[8:-3])

    return bytes().join(sysex_contents)


def calculate_checksum(combined_contents):
    checksum_int = (~sum(combined_contents) + 1) & 127
    return checksum_int.to_bytes()


def main():
    args = parse_arguments()
    output_bytes = []

    logging.basicConfig(
        format='%(levelname)s: %(message)s' if args.verbose else '%(message)s',
        level=logging.DEBUG if args.verbose else logging.INFO)

    logging.debug(f'Adding preamble: {PREAMBLE.hex()}')
    output_bytes.append(PREAMBLE)

    input_path = Path(args.directory)
    sysex_contents = combine_input(input_path, args.extension)
    logging.debug(f'Adding combined bytes: {sysex_contents.hex()}')
    output_bytes.append(sysex_contents)

    checksum = calculate_checksum(sysex_contents)
    logging.debug(f'Adding calculated checksum: {checksum.hex()}')
    output_bytes.append(checksum)

    logging.debug(f'Adding terminator: {TERMINATOR.hex()}')
    output_bytes.append(TERMINATOR)

    output_path = Path(args.output or f'{args.directory}/combined.syx')
    logging.info(f'Writing the combined SysEx to {output_path.absolute()}')
    output_path.write_bytes(bytes().join(output_bytes))
    logging.info('Done!')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:  # sorry :(
        logging.critical(e)
        exit(1)
