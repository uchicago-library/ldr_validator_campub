"""Usage:
    validate.py [--root=<root>] [--mvol-chunk=<mvol_chunk>]
"""

import docopt, os, re, sys

def get_root_and_mvol_chunk_from_path(p, sep=os.sep):
    """Get a root and mvol chunk from a path in the filesystem. 
       
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

if __name__ == '__main__':
    args = docopt.docopt(__doc__)

    # Try to automatically determine the root and mvol_chunk if necessary.
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

    print(root)
    print(mvol_chunk)
