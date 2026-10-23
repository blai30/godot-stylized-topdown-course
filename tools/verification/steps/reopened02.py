import sys
sys.path.insert(0, sys.argv[1])
from steps import write

# The FileSystem dock showing the top folders, as at the end of lesson 2's folder steps (before .gdignore) or after the
# reopen (with it). Which one depends on the snapshot the run starts from.
name = 'l02_reopened'
write(sys.argv[2], [
    {'op': 'fs', 'path': 'res://'},
    {'op': 'capture', 'name': name, 'frames': 60},
])
