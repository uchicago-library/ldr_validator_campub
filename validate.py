"""Usage:
    validate.py [path]
"""

import argparse
import docopt
import csv
import io
import logging
import os
import re
import sys
from lxml import etree
import xml
from xml.etree import ElementTree


def get_root_and_mvol_chunk_from_path(p, sep=os.sep):
    """Get a root and mvol chunk from a path in the filesystem. This function
       uses the path as a string variable only- it does not check to see if
       the path is actually available in the filesystem.
       
        Args:
            p (string), a filesystem path.

            sep (string), an OS path separator. (This paramater is provided
                mainly so that the correct separator can be passed in for 
                unit testing.)

        Returns:
            A tuple. The first element is a filesystem path, and the second is
            an mvol chunk like "mvol", "mvol-0001", or "mvol-0001-0002"
    """
        
    dirs = os.path.abspath(p).split(sep)

    # if the user runs this command in a directory containing an 'mvol'
    # directory, append that.
    if dirs[-1] != 'mvol' and 'mvol' in os.listdir(p):
        dirs.append('mvol')

    # If the user runs this command inside one of the sequence directories, pop
    # that directory off the list. 
    if dirs[-1] in ('jpg', 'tif', 'xml'):
        dirs.pop()

    root = mvol_chunk = None
    for i in range(len(dirs)):
        if dirs[i] == 'mvol':
            root = sep.join(dirs[0:i])
            mvol_chunk = '-'.join(dirs[i:])
            break
    if root == None:
        raise ValueError

    # Raise an exception if the mvol_chunk doesn't make sense.
    if re.match('^mvol(-[0-9]{4}){0,3}$', mvol_chunk):
        return (root, mvol_chunk)
    else:
        raise ValueError

def is_identifier(identifier_chunk):
    """Return true if this identifier chunk is a complete identifier. 

    Args:
        identifier_chunk (str): e.g., 'mvol-0001', 'mvol-0001-0002-0003'

    Returns:
        bool
    """
    return bool(
        re.match(
	    '^mvol-\d{4}-\d{4}-[0-9A-Z]{4}(-\d{2})?$', 
            identifier_chunk
        )
    )

class Validator():
    def __init__(self, root, identifier, sep, memory_fs = None):
        if type(self) == Validator:
            raise NotImplementedError
        self.root = root
        self.identifier = identifier
        self.sep = sep
        self.memory_fs = memory_fs

        if self.memory_fs != None:
            self.exists_fun = memory_fs.exists
            self.walk_fun = fs.walk.Walker
        else:
            self.exists_fun = os.path.exists
            self.walk_fun = os.walk

        logging.basicConfig(
            format = "%(asctime)s - %(levelname)s - %(message)s",
            level = logging.INFO
        )
        self.logger = logging.getLogger()

    def validate(self):
        """Call all methods that begin with the string 'validate_'. """
        for i in dir(self):
            if callable(getattr(self, i)) and i.startswith('validate_'):
                getattr(self, i)()

class MvolValidator(Validator):
    def validate_dc_xml(self):
        """Be sure exactly one correctly formed .dc.xml file is present.
    
            Side Effect:
              logs appropriate info() messages.
        """
        # be sure there is exactly one dc.xml file.
        paths = []
        for root, _, files in self.walk_fun(
            self.sep.join(
                (
                    self.root,
                    self.identifier.replace('-', self.sep),
                ) 
            )
        ):
            for f in files:
                if f.endswith('.dc.xml'):
                    paths.append(os.path.normpath(self.sep.join((root, f))))

        if len(paths) != 1:
            self.logger.info(
                self.identifier + ' - ' +
                self.identifier + 
		        ' does not contain exactly one dc.xml file'
            )
            # pass through, because there may be a .dc.xml we can test.

        # file is named correctly, in correct location.
        dc_xml_path = self.sep.join(
            (
                self.root, 
                self.identifier.replace('-', self.sep),
                self.identifier + '.dc.xml'
            )
        )

        if not(self.exists_fun(dc_xml_path)):
            self.logger.info(
                self.identifier + ' - ' +
                self.identifier + 
                ' contains a dc.xml file that is either incorrectly named ' + 
                ' or in the wrong location'
            )
            return

        try:
            if self.memory_fs != None:
                with self.memory_fs.open(dc_xml_path) as f:
                    metadata = xml.etree.ElementTree.fromstring(f.read())
            else:
                metadata = xml.etree.ElementTree.parse(dc_xml_path)
        except xml.etree.ElementTree.ParseError:
            self.logger.info(
              self.identifier + ' - ' + dc_xml_path + ' is not well-formed XML'
            )
            return

        # root should be <metadata>
        if metadata.getroot().tag != 'metadata':
            self.logger.info(
                self.identifier + ' - ' +
                dc_xml_path +
                ' should have <metadata> root element with no namespace.'
            )

        # elements. 
        for e in (
            'dc:title',
            'dc:identifier',
            'dc:date',
            'dc:description'
        ):
            if len(
                metadata.getroot().findall(
                    e,
                    namespaces={
                        'dc': 'http://purl.org/dc/elements/1.1/'
                    }
                )
            ) != 1:
                self.logger.info(
                    self.identifier + ' - ' +
                    '{} should have exactly one <{}> element.'.format(
                        dc_xml_path,
                        e
                    )
                )

    def validate_struct_txt(self):
        """Be sure exactly one correctly formed .struct.txt is present.

            Side Effect:
              logs appropriate info() messages.
        """

        # be sure there is exactly one struct.txt file.
        paths = []
        for root, _, files in self.walk_fun(
            self.sep.join(
                (
                    self.root,
                    self.identifier.replace('-', self.sep),
                ) 
            )
        ):
            for f in files:
                if f.endswith('.struct.txt'):
                    paths.append(os.path.normpath(self.sep.join((root, f))))

        if len(paths) != 1:
            self.logger.info(
                self.identifier + ' - ' +
                self.identifier + 
		        ' does not contain exactly one .struct.txt file'
            )
            # pass through, because there may be a .struct.txt we can test.

        # file is named correctly, in correct location.
        struct_txt_path = self.sep.join(
            (
                self.root, 
                self.identifier.replace('-', self.sep),
                self.identifier + '.struct.txt'
            )
        )

        if not(self.exists_fun(struct_txt_path)):
            self.logger.info(
                self.identifier + ' - ' +
                self.identifier + 
                ' contains a struct.txt file that is either incorrectly ' + 
                ' named or in the wrong location'
            )
            return

        with open(struct_txt_path) as f:
            line = f.readline()
            while line:
                if not re.match('^\d{4}(\t.*)?$', line):
                    self.logger.info(
                        self.identifier + ' - ' +
                        struct_txt_path + ' has invalid content'
                    )
                line = f.readline()
            return

    def _validate_directory(self, folder_name):
        """A helper function to validate ALTO, JPEG, and TIFF folders inside mvol
        folders.

        Args:
            folder_name (str): the name of the folder: tif|xml

        Returns:
            list: error messages, or an empty list.
        """

        extensions = {
            'xml': 'xml',
            'jpg': 'jpg',
            'tif': 'tif'
        }

        if folder_name not in extensions.keys():
            raise ValueError('unsupported folder_name\n')

        folder_path = self.sep.join(
            (
                self.root,
                self.identifier.replace('-', self.sep),
                folder_name
            )
        )

        # confirm that the named folder exists.
        if not(self.exists_fun(folder_path)):
            self.logger.info(self.identifier + ' - ' + folder_path + ' does not exist')
            return

        filename_re = '^\d{{4}}\.{}$'.format(extensions[folder_name])

        sequence_files_on_disk = set()
        for f in os.listdir(folder_path):
            if bool(re.search(filename_re, f)):
                sequence_files_on_disk.add(f)
            else:
                self.logger.info(
                    self.identifier + ' - ' +
                    self.sep.join((folder_path, f)) + 
                    ' is not allowed'
                )

        sequence_files_expected = set()
        for i in range(len(sequence_files_on_disk)):
            sequence_files_expected.add('{:04d}.{}'.format(i + 1, extensions[folder_name]))

        if sequence_files_on_disk != sequence_files_expected:
            self.logger.info(
                self.identifier + ' - ' +
                folder_path + 
                ' contains unexpected filenames'
            )

    def validate_tif_directory(self):
        """Validates tif directory
        """
        self._validate_directory('tif')

    def validate_xml_directory(self):
        """Validates TIFF directories within an identifier.
        """
        self._validate_directory('xml')

    def validate_allowable_files_only(self):
        """
        Make sure only allowable files are in the directory.
        """
        files_expected = set((
            '{}.dc.xml'.format(self.identifier),
            '{}.struct.txt'.format(self.identifier),
            'tif',
            'xml'
        ))

        files_present = set()
        for f in os.listdir(
            self.sep.join(
                (
                    self.root,
                    self.identifier.replace('-', self.sep)
                )
            )
        ):
            files_present.add(f)

        for f in (files_present - files_expected):
            self.logger.info(
                self.identifier + ' - ' +
                self.sep.join(
                    (
                        self.root,
                        f
                    )
                ) + ' is not allowed'
            )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('validation_directory', default='.', 
        help='directory to check', nargs='?')
    args = parser.parse_args()

    try:
        root, mvol_chunk = get_root_and_mvol_chunk_from_path(
            args.validation_directory
        )
    except ValueError:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # if the user specified a path using a paramter, check to be sure the
    # root and mvol-chunk folders exist.
    if not os.path.isdir(root):
        sys.stderr.write(root + ' does not exist.\n')
        sys.exit(1)

    if not os.path.isdir(
        os.path.join(
            root,
            mvol_chunk.replace('-', os.sep)
        )
    ):
        sys.stderr.write(
            os.path.join(root, mvol_chunk.replace('-', os.sep)) +
            ' does not exist.\n'
        )
        sys.exit(1)

    # Get a unique list of mvols.
    identifiers = set()
    for r, dirs, files in os.walk(
        os.path.join(
            root,
            mvol_chunk.replace('-', os.sep)
        )
    ):
        for d in dirs:
            _, mvol_chunk = get_root_and_mvol_chunk_from_path(
                os.sep.join((r, d))
            )
            if is_identifier(mvol_chunk):
                identifiers.add(mvol_chunk)

    for identifier in sorted(list(identifiers)):
        MvolValidator(
            root,
            identifier,
            os.sep
        ).validate()

