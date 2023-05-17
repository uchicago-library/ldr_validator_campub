import fs.memoryfs, PIL.Image, unittest

from validate import get_root_and_mvol_chunk_from_path

class TestValidator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestValidator, self).__init__(*args, **kwargs)

        # set up a memory-based filesystem and some test cases.
        self.memory_fs = fs.memoryfs.MemoryFS()
        
        # valid directory.
        identifier = 'mvol-0001-0002-0003'
        self._make_dc_xml(identifier)
        self._make_struct_txt(identifier)
        self._make_tif_files(identifier)
        self._make_xml_files(identifier)
            
        # directory where TIFFs are empty.
        identifier = 'mvol-0001-0002-0004'
        self._make_dc_xml(identifier)
        self._make_struct_txt(identifier)
        try:
           self.memory_fs.makedirs('/data/{}/tif'.format('/'.join(identifier.split('-'))))
        except fs.errors.DirectoryExists:
            pass
        for i in range(10):
            self.memory_fs.touch(
                '/data/{}/tif/{}_{:04d}.tif'.format(
                    '/'.join(identifier.split('-')),
                    identifier,
                    i
                ),
            )
        self._make_xml_files(identifier)
    
        # directory where OCR is empty.
        identifier = 'mvol-0001-0002-0005'
        self._make_dc_xml(identifier)
        self._make_struct_txt(identifier)
        self._make_tif_files(identifier)
        try:
           self.memory_fs.makedirs('/data/{}/xml'.format('/'.join(identifier.split('-'))))
        except fs.errors.DirectoryExists:
            pass
        for i in range(10):
            self.memory_fs.touch(
                '/data/{}/xml/{}_{:04d}.xml'.format(
                    '/'.join(identifier.split('-')),
                    identifier,
                    i
                ),
            )
    
        # numbered file mismatch.
        identifier = 'mvol-0001-0002-0006'
        self._make_dc_xml(identifier)
        self._make_struct_txt(identifier)
        self._make_tif_files(identifier)
        try:
           self.memory_fs.makedirs('/data/{}/xml'.format(
                '/'.join(identifier.split('-'))
            ))
        except fs.errors.DirectoryExists:
            pass

    def test_get_root_and_mvol_chunk_from_path_no_mvol_dir(self):
        """ Raise a ValueError if this function is passed a path without an mvol
            directory.
        """
        with self.assertRaises(ValueError):
            get_root_and_mvol_chunk_from_path(
                '/data/no_mvol_dir'
            )

        with self.assertRaises(ValueError):
            get_root_and_mvol_chunk_from_path(
                r'C:\Data\no_mvol_dir',
                sep='\\'
            )

    def test_get_root_and_mvol_chunk_from_path(self):
        """ Test a few different paths to be sure this function returns the
            correct root and mvol chunk.
        """
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                '/data/mvol'
            ),
            (
                '/data',
                'mvol'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                r'C:\Data\mvol', 
                sep='\\'
            ),
            (
                r'C:\Data',
                'mvol'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                '/data/mvol/0001'
            ),
            (
                '/data',
                'mvol-0001'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                r'C:\Data\mvol\0001', 
                sep='\\'
            ),
            (
                r'C:\Data',
                'mvol-0001'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                '/data/mvol/0001/0002'
            ),
            (
                '/data',
                'mvol-0001-0002'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                r'C:\Data\mvol\0001\0002', 
                sep='\\'
            ),
            (
                r'C:\Data',
                'mvol-0001-0002'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                '/data/mvol/0001/0002/0003'
            ),
            (
                '/data',
                'mvol-0001-0002-0003'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                r'C:\Data\mvol\0001\0002\0003', 
                sep='\\'
            ),
            (
                r'C:\Data',
               'mvol-0001-0002-0003'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                '/data/mvol/0001/0002/0003/jpg'
            ),
            (
                '/data',
                'mvol-0001-0002-0003'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                r'C:\Data\mvol\0001\0002\0003\jpg',
                sep='\\'
            ),
            (
                r'C:\Data',
                'mvol-0001-0002-0003'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                '/data/mvol/0001/0002/0003/tif'
            ),
            (
                '/data',
                'mvol-0001-0002-0003'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                r'C:\Data\mvol\0001\0002\0003\tif',
                sep='\\'
            ),
            (
                r'C:\Data',
                'mvol-0001-0002-0003'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                '/data/mvol/0001/0002/0003/xml'
            ),
            (
                '/data',
                'mvol-0001-0002-0003'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                r'C:\Data\mvol\0001\0002\0003\xml',
                sep='\\'
            ),
            (
                r'C:\Data',
                'mvol-0001-0002-0003'
            )
        )

    def test_get_root_and_mvol_chunk_from_path_bad_mvol_chunk(self):
        """ Raise a ValueError if this function is passed a path doesn't create
            a valid mvol chunk.
        """
        with self.assertRaises(ValueError):
            get_root_and_mvol_chunk_from_path(
                '/data/mvol/0001/0002/0003/0004'
            )

        with self.assertRaises(ValueError):
            get_root_and_mvol_chunk_from_path(
                r'C:\Data\mvol\0001\0002\0003\0004',
                sep='\\'
            )
        with self.assertRaises(ValueError):
            get_root_and_mvol_chunk_from_path(
                '/data/mvol/0001/0002/weird_dir'
            )

        with self.assertRaises(ValueError):
            get_root_and_mvol_chunk_from_path(
                r'C:\Data\mvol\0001\0002\weird_dir',
                sep='\\'
            )

    def _make_dc_xml(self, identifier):
        """Make a .dc.xml file for test cases.
    
        Args:
            identifier: a string, an mvol identifier (e.g., 'mvol-0001-0002-0003')
    
        Side Effect:
            Create a .dc.xml file in the appropriate place in the filesystem.
        """
    
        mvol_root = '/data/{}'.format(
            '/'.join(identifier.split('-'))
        )
        try:
            self.memory_fs.makedirs(mvol_root)
        except fs.errors.DirectoryExists:
            pass
        with self.memory_fs.open(
            '{}/{}.dc.xml'.format(
                mvol_root,
                identifier
            ),
            'w'
        ) as f:
            f.write('''<?xml version="1.0"?>
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:title>Title</dc:title>
  <dc:date>2023-04</dc:date>
  <dc:identifier>{}</dc:identifier>
  <dc:description>Description</dc:description>
</metadata>'''.format(identifier))

    def _make_struct_txt(self, identifier):
        """Make a .struct.txt file for test cases.
    
        Args:
            identifier: a string, an mvol identifier (e.g., 'mvol-0001-0002-0003')
    
        Side Effect:
            Create a .struct.txt file in the appropriate place in the filesystem.
        """
        mvol_root = '/data/{}'.format(
            '/'.join(identifier.split('-'))
        )
        try:
            self.memory_fs.makedirs(mvol_root)
        except fs.errors.DirectoryExists:
            pass
        with self.memory_fs.open(
            '{}/{}.struct.txt'.format(
                mvol_root,
                identifier
            ),
            'w'
        ) as f:
            f.write('''\t0001\t
1\t0002\t
2\t0003\t
3\t0004\t
4\t0005\t
5\t0006\t
6\t0007\t
7\t0008\t
 \t0009\t''')

    def _make_tif_files(self, identifier):
        """Make a sequence of TIFF files for test cases.
    
        Args:
            file_system: a filesystem object, (e.g., from Python's fs module)
            identifier: a string, an mvol identifier (e.g., 'mvol-0001-0002-0003')
    
        Side Effect:
    	Create a sequence of TIFF files at the appropriate place in the
            filesystem.
        """
        mvol_root = '/data/{}'.format(
            '/'.join(identifier.split('-'))
        )
        try:
           self.memory_fs.makedirs('{}/tif'.format(mvol_root))
        except fs.errors.DirectoryExists:
            pass
        for i in range(10):
            img = PIL.Image.new(mode='RGB', size=(i+1, i+1))
            img.putpixel((0,0), (i+1, i+1, i+1))
            with self.memory_fs.open(
                '{}/tif/{}_{:04d}.tif'.format(
                    mvol_root,
                    identifier,
                    i
                ),
                'wb'
            ) as f:
                img.save(f)

    def _make_xml_files(self, identifier):
        """Make a sequence of XML files for test cases.
    
        Args:
            identifier: a string, an mvol identifier (e.g., 'mvol-0001-0002-0003')
    
        Side Effect:
    	Create a sequence of XML files at the appropriate place in the
            filesystem.
        """
        mvol_root = '/data/{}'.format(
            '/'.join(identifier.split('-'))
        )
        try:
           self.memory_fs.makedirs('{}/xml'.format(mvol_root))
        except fs.errors.DirectoryExists:
            pass
        for i in range(10):
            with self.memory_fs.open(
                '{}/xml/{}_{:04d}.xml'.format(
                    mvol_root,
                    identifier,
                    i
                ),
                'w'
            ) as f:
                f.write('''<?xml version="1.0" encoding="utf-8"?>
<alto xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/standards/alto/ns-v2# http://www.loc.gov/standards/alto/alto-v2.0.xsd" xmlns="http://www.loc.gov/standards/alto/ns-v2#">
  <Layout>
    <Page ID="P0" PHYSICAL_IMG_NR="0" HEIGHT="5424" WIDTH="4432" ACCURACY="0.8071983">
      <PrintSpace>
        <TextBlock ID="P0_TB00001" HPOS="1474" VPOS="653" WIDTH="1464" HEIGHT="63">
          <TextLine ID="P0_TL00001" HPOS="1476" VPOS="655" WIDTH="1460" HEIGHT="60">
            <String ID="P0_S00001" HPOS="1476" VPOS="655" WIDTH="359" HEIGHT="56" STYLEREFS="StyleId-0" CONTENT="FOUNDED" WC="0.926050365" CC="0020001" />
            <SP ID="P0_SP00001" WIDTH="0" HPOS="0" VPOS="0" />
            <String ID="P0_S00002" HPOS="1883" VPOS="658" WIDTH="98" HEIGHT="51" STYLEREFS="StyleId-0" CONTENT="BY" WC="0.876470566" CC="11" />
            <SP ID="P0_SP00002" WIDTH="0" HPOS="0" VPOS="0" />
            <String ID="P0_S00003" HPOS="2026" VPOS="658" WIDTH="193" HEIGHT="52" STYLEREFS="StyleId-0" CONTENT="JOHN" WC="0.93921566" CC="0010" />
            <SP ID="P0_SP00003" WIDTH="0" HPOS="0" VPOS="0" />
            <String ID="P0_S00004" HPOS="2269" VPOS="660" WIDTH="71" HEIGHT="51" STYLEREFS="StyleId-0" CONTENT="D." WC="0.972549" CC="00" />
            <SP ID="P0_SP00004" WIDTH="0" HPOS="0" VPOS="0" />
            <String ID="P0_S00005" HPOS="2382" VPOS="655" WIDTH="554" HEIGHT="60" STYLEREFS="StyleId-0" CONTENT="ROCKEFELLER" WC="0.891265631" CC="03000110010" />
            <SP ID="P0_SP00005" WIDTH="0" HPOS="0" VPOS="0" />
          </TextLine>
        </TextBlock>
      </PrintSpace>
    </Page>
  </Layout>
</alto>''')

if __name__ == '__main__':
    unittest.main()
