import argparse
import logging
from pathlib import Path

PREAMBLE = bytes.fromhex('F000203200013310')
TERMINATOR = bytes.fromhex('F7')


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Combines/merges SysEx preset files for bulk transmission to the Behringer Pro VS Mini synthesizer.')

    parser.add_argument(
        'directory',
        help='Directory to get the preset files from. Only the first 32 files are merged!')
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


def parse_files(directory_path, extension):
    sysex_contents = []

    sysex_filepaths = list(directory_path.glob(f'*.{extension}'))
    if len(sysex_filepaths) == 0:
        raise FileNotFoundError('No matching files found!')
    logging.info(f'Found {len(sysex_filepaths)} sysex files in {directory_path.absolute()}')
    logging.debug(f'Sysex files found:\n{'\n'.join(sysex_filepath.as_posix() for sysex_filepath in sysex_filepaths)}')

    for sysex_filepath in sysex_filepaths:
        sysex_content = sysex_filepath.read_bytes()
        if sysex_content.startswith(PREAMBLE):
            logging.info(f'Skipping combined file {sysex_filepath.name}')
            continue
        logging.info(f'Adding {sysex_filepath.name}')
        logging.debug(f'File contents:\n{sysex_content.hex()}')
        sysex_contents.append(sysex_content)

    return sysex_contents[:32]


def combine_files(sysex_contents):
    combined_contents = []
    for sysex_content in sysex_contents:
        sysex_stripped = sysex_content[8:-3]
        logging.debug(f'Stripped contents: {sysex_stripped.hex()}')
        combined_contents.append(sysex_stripped)

    return bytes().join(combined_contents)


def calculate_checksum(combined_contents):
    checksum_int = (~sum(combined_contents) + 1) & 127
    return checksum_int.to_bytes()


def main():
    args = parse_arguments()
    sysex_bytes = []

    logging.basicConfig(
        format='%(levelname)s: %(message)s' if args.verbose else '%(message)s',
        level=logging.DEBUG if args.verbose else logging.INFO)

    directory_path = Path(args.directory)
    sysex_contents = parse_files(directory_path, args.extension)

    logging.debug(f'Adding preamble: {PREAMBLE.hex()}')
    sysex_bytes.append(PREAMBLE)
    combined_contents = combine_files(sysex_contents)
    logging.debug(f'Adding combined bytes: {combined_contents.hex()}')
    sysex_bytes.append(combined_contents)
    checksum = calculate_checksum(combined_contents)
    logging.debug(f'Adding calculated checksum: {checksum.hex()}')
    sysex_bytes.append(checksum)
    logging.debug(f'Adding terminator: {TERMINATOR.hex()}')
    sysex_bytes.append(TERMINATOR)

    output_path = Path(args.output or f'{args.directory}/combined.syx')
    logging.info(f'Writing the combined SysEx to {output_path.absolute()}')
    output_path.write_bytes(bytes().join(sysex_bytes))
    logging.info('Done!')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:  # sorry :(
        logging.critical(e)
        exit(1)
