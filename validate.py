"""Usage:
    validate.py [--root=<root>] [--mvol-chunk=<mvol_chunk>]
"""

import docopt, os, re, sys
import csv
import getpass
import io
import logging
import os
import paramiko
import re
import requests
import sqlite3
import stat
import subprocess
import sys
from pathlib import Path 
from lxml import etree
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
        
    dirs = os.path.normpath(p).split(sep)

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
    return bool(re.match('^mvol-\d{4}-\d{4}-[0-9A-Z]{4}(-\d{2})?$', identifier_chunk))

class ValidationError(Exception):
    """Raised when a validation function finds an error."""
    pass

class Validator():
    def __init__(self, root, identifier, sep, memory_fs = None):
        self.root = root
        self.identifier = identifier
        self.sep = sep
        self.memory_fs = memory_fs

    def validate(self):
        """Call all methods that begin with the string 'validate_'. """
        for i in dir(self):
            if callable(getattr(self, i) and i.startswith('validate_'):
                getattr(self, i)()

class MvolValidator(Validator):
    def validate_dc_xml_is_singleton(self):
        """Check to see if a given mvol root contains exactly one dc.xml file.
    
            Raises ValidatorError if this digital object is invalid. 
        """
        if self.memory_fs != None:
            walk_fun = fs.walk.Walker
        else:
            walk_fun = os.walk
    
        paths = []
        for root, _, files in walk_fun(self.root):
            for f in files:
                paths.append(self.sep.join((self.root, root, f)))
        if len( 
            filter(
                lambda x: x.endswith('.dc.xml'),
                paths
            )
        ) != 1:
            raise ValidationError(self.identifier + ' does not contain exactly one .dc.xml file.')

    def validate_dc_xml_is_named_correctly_in_correct_location(self):
        """Check to see if a given mvol root contains a .dc.xml file in the correct
           location.

            Raises ValidatorError if this digital object is invalid. 
        """
        if self.memory_fs != None:
            exists_fun = memory_fs.exists
        else:
            exists_fun = os.path.exists
    
        if not(
            exists_fun(
                self.sep.join(
                    (
                        self.root, 
                        self.identifier.replace('-', sep),
                        self.identifier + '.dc.xml'
                    )
                )
            )
        ):
            raise ValidationError(self.identifier + ' is named incorrectly or in the wrong location.')

    def validate_dc_xml_is_well_formed(self):
        """Check to see if a given mvol_root contains a dc.xml file 
           mvol directory) contains exactly one dc.xml file, named correctly.
     
            Raises ValidatorError if this digital object is invalid. 
        """
        if self.memory_fs != None:
            walk_fun = fs.walk.Walker
        else:
            walk_fun = os.walk
        try: 
            dc_xml_path = filter(
                lambda x: x == identifier + '.dc.xml',
                [self.sep.join(self.root, root, f) 
                 for root, _, files 
                 in walk_fun(self.root) 
                 for f in files
                ]
            )[0]
        except IndexError:
            raise ValidationError(self.identifier + ' is named incorrectly or in the wrong location.')
    
        try:
            if memory_fs != None:
                with memory_fs.open(dc_xml_path) as f:
                    xml.etree.ElementTree.fromstring(f.read())
            else:
                xml.etree.ElementTree.parse(dc_xml_path)
        except xml.etree.ElementTree.ParseError:
            raise ValidationError(identifier + ' is not well-formed XML.')

    def _dc_xml_get_xml(self):
        """Helper function- get the .dc.xml for a given identifier.
     
            Returns: etree XML object.
        """
        dc_xml_path = self.sep.join(
            (
                self.root,
                self.identifier.replace('-', self.sep),
                self.identifier + '.dc.xml'
            )
        )
    
        if self.memory_fs != None:
            with self.memory_fs.open(dc_xml_path) as f:
                return xml.etree.ElementTree.fromstring(f.read())
        else:
            return xml.etree.ElementTree.parse(dc_xml_path)

    def validate_dc_xml_has_valid_root(self):
        """Check to see if a given mvol_root contains a dc.xml file with a valid
           root element.
     
            Raises ValidatorError if this digital object is invalid. 
        """
    
        try:
            if self._dc_xml_get_xml().getroot().tag != 'metadata':
                raise ValidationError(self.identifier + ' should have <metadata> root element with no namespace.')
        except xml.etree.ElementTree.ParseError:
            raise ValidationError(self.identifier + ' is not well-formed XML.')

    def validate_dc_xml_has_valid_title(self):
        """Check to see if a given mvol_root contains a dc.xml file with a valid
           title element.
     
            Raises ValidatorError if this digital object is invalid. 
        """
        try:
            if len(
                self._dc_xml_get_xml().findall(
                    'dc:title', 
                    namespaces={
                        'dc': 'http://purl.org/dc/elements/1.1/'
                    }
                )
            ) != 1:
                raise ValidationError(self.identifier + ' should have exactly one <dc:title> element.')
        except xml.etree.ElementTree.ParseError:
            raise ValidationError(self.identifier + ' is not well-formed XML.')

    def validate_dc_xml_has_valid_identifier(self):
        """Check to see if a given mvol_root contains a dc.xml file with a valid
           title element.
     
            Raises ValidatorError if this digital object is invalid. 
        """
        try:
            if len(
                self._dc_xml_get_xml().findall(
                    'dc:identifier', 
                    namespaces={
                        'dc': 'http://purl.org/dc/elements/1.1/'
                    }
                )
            ) != 1:
                raise ValidationError(self.identifier + ' should have exactly one <dc:identifier> element.')
        except xml.etree.ElementTree.ParseError:
            raise ValidationError(self.identifier + ' is not well-formed XML.')

    def validate_dc_xml_has_valid_date(self):
        """Check to see if a given mvol_root contains a dc.xml file with a valid
           title element.
     
            Raises ValidatorError if this digital object is invalid. 
        """
        try:
            if len(
                self._dc_xml_get_xml().findall(
                    'dc:date', 
                    namespaces={
                        'dc': 'http://purl.org/dc/elements/1.1/'
                    }
                )
            ) != 1:
                raise ValidationError(self.identifier + ' should have exactly one <dc:date> element.')
        except xml.etree.ElementTree.ParseError:
            raise ValidationError(self.identifier + ' is not well-formed XML.')

    def validate_dc_xml_has_valid_description(self):
        """Check to see if a given mvol_root contains a dc.xml file with a valid
           title element.
     
            Raises ValidatorError if this digital object is invalid. 
        """
        try:
            if len(
                self._dc_xml_get_xml().findall(
                    'dc:description', 
                    namespaces={
                        'dc': 'http://purl.org/dc/elements/1.1/'
                    }
                )
            ) != 1:
                raise ValidationError(self.identifier + ' should have exactly one <dc:description> element.')
        except xml.etree.ElementTree.ParseError:
            raise ValidationError(self.identifier + ' is not well-formed XML.')

class OutOfTheWay():
    def validate_files(self, identifier):
        """For a given identifier, make sure a TIFF file exists. Confirm
        that the file is non-empty.
        
        Args:
            identifier (str): e.g. 'speculum-0001-001', 'chopin-001-001'
        """

        if not self.is_identifier_chunk(identifier):
            print("File doesn't exist")
            sys.exit()

        if 'ewm' in identifier or 'gms' in identifier:
            path = self.get_path(identifier[:8])
        elif 'chopin' in identifier:
            path = self.get_path(identifier[:10])
        elif 'speculum' in identifier:
            path = self.get_path(identifier[:13])

        dir_files = os.listdir(path)

        for folder in dir_files:
            if '.' not in folder:
                for image in os.listdir(path + '/' + str(folder)):
                    if identifier in image:
                        path += '/' + str(folder) + '/' + str(image)
                        f = open(path)
                        return self._validate_file_notempty(f)
        
        return ['{} tiff missing\n'.format(identifier)]

    def validate_tiff_directory(self, identifier, folder_name):
        """Validates TIFF directories within an identifier.
        
        Args:
            identifier (str): e.g. 'chopin-001' 
            folder_name (str): e.g. 'TIFF' 
            
        Returns:
            pass: empty list
            fail: list with error messages
        """

        extensions = {
            'ALTO': 'xml',
            'JPEG': 'jpg',
            'POS': 'pos',
            'TIFF': 'tif'
        }

        if folder_name not in extensions:
            raise ValueError('unsupported folder name.\n')

        if not self.is_identifier(identifier):
            raise ValueError('invalid identifier.\n')

        path = self.get_path(identifier)
        folders = os.listdir(path)

        entries = []
        for directory in folders:
            if '.' not in directory:
                for entry in os.listdir(path + '/' + str(directory)):
                    entries.append(path + '/' + directory + '/' + str(entry))
        
        errors = []
        for i in entries:
            file_name = i.split('/')[-1]

            if not file_name.endswith(extensions[folder_name]):
                errors.append('%s is not a tif file' % file_name)

            f = open(i)
            empty = self._validate_file_notempty(f)
            if empty:
                errors.append(empty[0])
            f.close()

        return errors
                        

    def validate_directory(self, identifier, folder_name):
        """A helper function to validate ALTO, JPEG, and TIFF folders inside mmdd
        folders.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
            folder_name (str): the name of the folder: ALTO|JPEG|TIFF

        Returns:
            list: error messages, or an empty list.
        """

        assert self.get_project(identifier) == 'mvol'

        extensions = {
            'ALTO': 'xml',
            'JPEG': 'jpg',
            'POS': 'pos',
            'TIFF': 'tif'
        }

        if folder_name not in extensions.keys():
            raise ValueError('unsupported folder_name.\n')

        mmdd_path = self.get_path(identifier)

        # raise an IOError if the ALTO, JPEG, or TIFF directory does not exist.
        os.stat(mmdd_path + '/' + folder_name)

        filename_re = '^{}_[0-9]+\.{}$'.format(identifier, extensions[folder_name])

        entries = []
        for entry in os.listdir('{}/{}'.format(mmdd_path, folder_name)):
            if entry.endswith(extensions[folder_name]):
                entries.append(entry)
        entries.sort()

        entries_pass = []
        entries_fail = []
        for entry in entries:
            if re.match(filename_re, entry):
                if folder_name == 'ALTO':
                    with open('{}/ALTO/{}'.format(self.get_path(identifier), entry)) as f:
                        try:
                            ElementTree.fromstring(f.read())
                            entries_pass.append(entry)
                        except (ElementTree.ParseError, UnicodeDecodeError):
                            entries_fail.append(entry)
            else:
                entries_fail.append(entry)

        errors = []
        if entries_fail:
            for entry in entries_fail:
                errors.append(
                    '{}/{}/{} problem.\n'.format(
                        identifier,
                        folder_name,
                        entry
                    )
                )
        return errors

    def validate_alto_or_pos_directory(self, identifier):
        """Validate that an ALTO or POS folder exists. Make sure it contains appropriate
        files.

        Args:
            identifier (str): 'mvol-0001-0002-0003'

        Returns:
            list: error messages, or an empty list.
        """

        assert self.get_project(identifier) == 'mvol'

        try:
            return self.validate_directory(identifier, 'ALTO')
        except IOError:
            try:
                return self.validate_directory(identifier, 'POS')
            except IOError:
                return ['{} ALTO or POS missing\n'.format(identifier)]

    def validate_jpeg_directory(self, identifier):
        """Validate that an JPEG folder exists. Make sure it contains appropriate
        files.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'

        Returns:
            list: error messages, or an empty list.
        """

        assert self.get_project(identifier) == 'mvol'

        try:
            return self.validate_directory(identifier, 'JPEG')
        except IOError:
            return ['{} JPEG missing\n'.format(identifier)]

    def validate_tiff_directory(self, identifier):
        """Validate that an TIFF folder exists. Make sure it contains appropriate
        files.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'

        Returns:
            list: error messages, or an empty list.
        """

        assert self.get_project(identifier) == 'mvol'
        try:
            return self.validate_directory(identifier, 'TIFF')
        except IOError:
            return ['{} TIFF missing\n'.format(identifier)]

    def validate_struct_txt(self, identifier, f=None):
        """Make sure that a given struct.txt is valid. It should be tab-delimited
        data, with a header row. Each record should contains a field for object,
        page and milestone.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
            f: a file-like object, for testing. 
        """

        assert self.get_project(identifier) == 'mvol'

        if not f:
            try:
                f = open(
                    '{}/{}.struct.txt'.format(self.get_path(identifier), identifier))
            except (FileNotFoundError, IOError):
                return ['{} struct.txt missing\n'.format(identifier)]

        line = f.readline()
        if not re.match('^object\tpage\tmilestone', line):
            return ['{} struct.txt has one or more errors\n'.format(identifier)]
        line = f.readline()
        while line:
            if not re.match('^\d{8}(\t.*)?$', line):
                return ['{} struct.txt has one or more errors\n'.format(identifier)]
            line = f.readline()
        return []

    def validate_txt(self, identifier):
        """Make sure that a .txt file exists for an identifier.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
        """

        assert self.get_project(identifier) == 'mvol'

        try:
            f = open('{}/{}.txt'.format(
                self.get_path(identifier),
                identifier))
            return DigitalCollectionValidator._validate_file_notempty(f)
        except (FileNotFoundError, IOError):
            return ['{} txt missing\n'.format(identifier)]

    def validate_pdf(self, identifier):
        """Make sure that a PDF exists for an identifier.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
        """

        assert self.get_project(identifier) == 'mvol'

        try:
            f = open('{}/{}.pdf'.format(
                self.get_path(identifier),
                identifier))
            return DigitalCollectionValidator._validate_file_notempty(f)
        except (FileNotFoundError, IOError):
            return ['{} pdf missing\n'.format(identifier)]

    def validate_allowable_files_only(self, identifier):
        """
        JEJ TODO: make sure only allowable files are in the directory.
        """
        assert self.get_project(identifier) == 'mvol'

        errors = []

        allowable_files = set((
            '{}.dc.xml'.format(identifier),
            '{}.mets.xml'.format(identifier),
            '{}.METS.xml'.format(identifier),
            '{}.pdf'.format(identifier),
            '{}.struct.txt'.format(identifier),
            '{}.txt'.format(identifier)
        ))

        files_present = set()
        for f in os.listdir('{}/{}'.format(
            self.local_root, 
            identifier.replace('-', '/')
        )):
            if os.path.isfile('{}/{}/{}'.format(
                self.local_root,
                identifier.replace('-', '/'),
                f
            )):
                files_present.add(f)

        for f in files_present.difference(allowable_files):
            errors.append('non-allowable file {} in {}\n'.format(f, identifier))

        '''
        if not os.path.isdir('{}/{}/JPEG'.format(
            self.local_root,
            identifier.replace('-', '/')
        )):
            errors.append('JPEG dir missing in {}\n'.format(identifier))
        '''

        if not os.path.isdir('{}/{}/TIFF'.format(
            self.local_root,
            identifier.replace('-', '/')
        )):
            errors.append('JPEG dir missing in {}\n'.format(identifier))

        if not os.path.isdir('{}/{}/ALTO'.format(
            self.local_root,
            identifier.replace('-', '/')
        )) and not os.path.isdir('{}/{}/POS'.format(
            self.local_root,
            identifier.replace('-', '/')
        )):
            errors.append('ALTO or POS dir missing in {}\n'.format(identifier))

        counts = {}
        for d in ('ALTO', 'POS', 'JPEG', 'TIFF'):
            directory = '{}/{}/{}'.format(
                self.local_root,
                identifier.replace('-', '/'),
                d
            )
            if os.path.isdir(directory):
                counts[d] = len(os.listdir(directory))

        if len(set(counts.values())) > 1:
            errors.append('file count mismatch in {}\n'.format(identifier))

        return errors


    def validate_ocr(self, identifier):
        """Be sure OCR conversion works for this item.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
        """

        assert self.get_project(identifier) == 'mvol'

        with open('/dev/null', 'w') as f:
            return_code = subprocess.call([
                'python',
                '/data/s4/jej/ocr_converters/build_ia_bookreader_ocr.py',
                '--local-root={}'.format(self.local_root),
                identifier,
                '0',
                '0'
            ],
            stdout=f
        )
        if return_code == 0:
            return []
        else:
            return ['trouble with OCR on {}\n'.format(identifier)]

    def validate(self, identifier):
        """Wrapper to call all validation functions. 

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
        """

        assert self.get_project(identifier) == 'mvol'

        errors = []
        errors += self.validate_alto_or_pos_directory(identifier)
        # errors += self.validate_jpeg_directory(identifier)
        errors += self.validate_tiff_directory(identifier)
        errors += self.validate_pdf(identifier)
        errors += self.validate_struct_txt(identifier)
        errors += self.validate_txt(identifier)
        errors += self.validate_dc_xml(identifier)
        errors += self.validate_allowable_files_only(identifier)
        if not errors:
            pass
            #errors += self.validate_ocr(identifier)
        return errors

    def get_csv_data(self, identifier_chunk):
        """Get CSV data for a specific identifier chunk.
 
        Args:
            identifier_year (str): e.g. 'mvol-0004-1951'

        Returns:
            dict: data about these identifiers.
        """
        path = self.get_path(identifier_chunk)
        csv_data = {}
        for entry in os.listdir(path):
            if re.search('\.csv$', entry):
                f = self.ftp.file('{}/{}'.format(path, entry))
                reader = csv.reader(f)
                next(reader, None)
                try:
                    for row in reader:
                        csv_data[row[2]] = {
                            'title': row[0],
                            'date': row[1],
                            'description': row[3]
                        }
                except IndexError:
                    break
        return csv_data

    @staticmethod
    def _validate_file_notempty(f):
        """Make sure that a given file is not empty.

        Args:
            f: a file-like object.
        """
        errors = []

        f.seek(0, os.SEEK_END)
        size = f.tell()

        if not size:
            try:
                name = f.name
                name = name.split('/')[-1]
                errors.append('%s is an empty file.\n' % name)
            except AttributeError:
                errors.append('empty file.\n')
    
        f.close()
        return errors


if __name__ == '__main__':
    args = docopt.docopt(__doc__)

    logger = logging.getLogger()

    # Try to automatically determine and set the root and mvol_chunk if
    # necessary.
    auto_root = auto_mvol_chunk = None
    if args['--root'] == None or args['--mvol-chunk'] == None:
        try:
            auto_root, auto_mvol_chunk = get_root_and_mvol_chunk_from_path(os.getcwd())
        except ValueError:
            pass

    if args['--root'] == None and auto_root != None:
        args['--root'] = auto_root
    if args['--mvol-chunk'] == None and auto_mvol_chunk != None:
        args['--mvol-chunk'] = auto_mvol_chunk

    if args['--root'] == None or args['--mvol-chunk'] == None:
        sys.stderr.write('Was not able to determine root or mvol chunk.\n')
        sys.exit()

    # Look for mvol directories and validate each one. 
    for root, dirs, files in os.walk(
        os.sep.join(
            (
                args['--root'], 
                args['--mvol-chunk'].replace('-', os.sep)
            )
        )
    ):
        for d in dirs:
            p = os.sep.join((root, d))
            _, mvol_chunk = get_root_and_mvol_chunk_from_path(p)
            if is_identifier(mvol_chunk):
                mvol = mvol_chunk
                # .dc.xml
                for f in (
                    dc_xml_is_singleton,
                    dc_xml_is_named_correctly_in_correct_location,
                    dc_xml_is_well_formed,
                    dc_xml_has_valid_root,
                    dc_xml_has_valid_title,
                    dc_xml_has_valid_identifier,
                    dc_xml_has_valid_date,
                    dc_xml_has_valid_description,
                ):
                    try:
                        f(
                            args['--root'],
                            mvol, 
                            os.sep
                        )
                    except ValidationError as e:
                        logger.exception(e)


                    sys.stderr.write(mvol + ' .dc.xml is not well-formed XML.\n')
                        sys.stderr.write(mvol + ' .dc.xml should have a <metadata> root element with no namespace.\n')
                        sys.stderr.write(mvol + ' .dc.xml should have a <dc:title> element with the correct dc namespace.\n')
                        sys.stderr.write(mvol + ' .dc.xml should have a <dc:identifier> element with the correct dc namespace.\n')
                        sys.stderr.write(mvol + ' .dc.xml should have a <dc:date> element with the correct dc namespace.\n')
                        sys.stderr.write(mvol + ' .dc.xml should have a <dc:description> element with the correct dc namespace.\n')
            

            

    # is dc.xml there?
    # is it well-formed XML?
    # is it valid?
    
    # is struct.txt there?
    # is it well-formed (correct # of columns)
    # is it valid?
    
    # is tif and xml dir there?
    # are the files in tif and xml contain named correctly?
    # are files in tif actually tifs?
    # are the files in xml well-formed xml?
    # are the files in xml valid?
    # are there the same number of files in each dir?
