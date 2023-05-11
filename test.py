import unittest

from validate import get_root_and_mvol_chunk_from_path

class TestValidator(unittest.TestCase):
    def test_get_root_and_mvol_chunk_from_path_no_mvol_dir(self):
        """ Raise a ValueError if this function is passed a path without an mvol
            directory.
        """
        with self.assertRaises(ValueError):
            get_root_and_mvol_chunk_from_path(
                '/home/jej/no_mvol_dir'
            )

        with self.assertRaises(ValueError):
            get_root_and_mvol_chunk_from_path(
                r'C:\Users\jej\no_mvol_dir',
                sep='\\'
            )

    def test_get_root_and_mvol_chunk_from_path(self):
        """ Test a few different paths to be sure this function returns the
            correct root and mvol chunk.
        """
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                '/home/jej/mvol'
            ),
            (
                '/home/jej',
                'mvol'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                r'C:\Users\jej\mvol', 
                sep='\\'
            ),
            (
                r'C:\Users\jej',
                'mvol'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                '/home/jej/mvol/0001'
            ),
            (
                '/home/jej',
                'mvol-0001'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                r'C:\Users\jej\mvol\0001', 
                sep='\\'
            ),
            (
                r'C:\Users\jej',
                'mvol-0001'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                '/home/jej/mvol/0001/0002'
            ),
            (
                '/home/jej',
                'mvol-0001-0002'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                r'C:\Users\jej\mvol\0001\0002', 
                sep='\\'
            ),
            (
                r'C:\Users\jej',
                'mvol-0001-0002'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                '/home/jej/mvol/0001/0002/0003'
            ),
            (
                '/home/jej',
                'mvol-0001-0002-0003'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                r'C:\Users\jej\mvol\0001\0002\0003', 
                sep='\\'
            ),
            (
                r'C:\Users\jej',
               'mvol-0001-0002-0003'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                '/home/jej/mvol/0001/0002/0003/jpg'
            ),
            (
                '/home/jej',
                'mvol-0001-0002-0003'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                r'C:\Users\jej\mvol\0001\0002\0003\jpg',
                sep='\\'
            ),
            (
                r'C:\Users\jej',
                'mvol-0001-0002-0003'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                '/home/jej/mvol/0001/0002/0003/tif'
            ),
            (
                '/home/jej',
                'mvol-0001-0002-0003'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                r'C:\Users\jej\mvol\0001\0002\0003\tif',
                sep='\\'
            ),
            (
                r'C:\Users\jej',
                'mvol-0001-0002-0003'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                '/home/jej/mvol/0001/0002/0003/xml'
            ),
            (
                '/home/jej',
                'mvol-0001-0002-0003'
            )
        )
        self.assertEqual(
            get_root_and_mvol_chunk_from_path(
                r'C:\Users\jej\mvol\0001\0002\0003\xml',
                sep='\\'
            ),
            (
                r'C:\Users\jej',
                'mvol-0001-0002-0003'
            )
        )

    def test_get_root_and_mvol_chunk_from_path_bad_mvol_chunk(self):
        """ Raise a ValueError if this function is passed a path doesn't create
            a valid mvol chunk.
        """
        with self.assertRaises(ValueError):
            get_root_and_mvol_chunk_from_path(
                '/home/jej/mvol/0001/0002/0003/0004'
            )

        with self.assertRaises(ValueError):
            get_root_and_mvol_chunk_from_path(
                r'C:\Users\jej\mvol\0001\0002\0003\0004',
                sep='\\'
            )
        with self.assertRaises(ValueError):
            get_root_and_mvol_chunk_from_path(
                '/home/jej/mvol/0001/0002/weird_dir'
            )

        with self.assertRaises(ValueError):
            get_root_and_mvol_chunk_from_path(
                r'C:\Users\jej\mvol\0001\0002\weird_dir',
                sep='\\'
            )

if __name__ == '__main__':
    unittest.main()
