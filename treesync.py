#!/usr/bin/env python

# A tool for synchronising two directory trees.

#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program; if not, a copy is available at
#    http://www.gnu.org/licenses/gpl.txt

import os, sys
from cmdline.cmdline import CommandLineApp
from filecmp import dircmp

class Treesync(CommandLineApp):
    def __init__(self):
        CommandLineApp.__init__(self)
        argv = sys.argv
        op = self.option_parser
        usage = 'usage: %s tree1 tree2' % os.path.basename(argv[0])
        op.set_usage(usage)

        op.add_option('-n', '--dry-run', dest='dry_run', default=False, action='store_true',
                      help="Just print shell commands; don't actually do anything")

        op.add_option('-d', '--delete', dest='delete', default=False, action='store_true',
                      help="Delete files from receiver that do not exist in sender")

        op.add_option('--delete-only', dest='delete_only', default=False, action='store_true',
                      help="Delete files from receiver that do not exist in sender, and do not copy files.")

    def main(self, source, dest):
        global settings
        settings = self.options
        sync(source, dest)
        
def sync(source, dest):
    """Compare top-level contents. If unequal, carry out equalising
    shell commands; recursively synchronise subdirectories."""
    dcmp = dircmp(source, dest)
    if settings.delete:
        for f in dcmp.right_only:
            delete(f, dest)
    if not settings.delete_only:
        for f in dcmp.left_only:
            copy(f, source, dest)
    dcmp = dircmp(source, dest)
    for d in dcmp.common_dirs:
        sync(os.path.join(source, d), os.path.join(dest, d))

def copy(fname, source, dest):
    if settings.verbose:
        log(os.path.join(source, fname))
    sourcef = os.path.join(source, fname)
    destf = os.path.join(dest, fname)
    cmd = 'cp -r "%s" "%s"' % (sourcef, destf)
    if not settings.dry_run:
        try:
            system(cmd)
        except Exception, e:
            sys.stderr.write('Failed to copy %s to %s: %s' % (sourcef, destf, e))
        
def delete(fname, dest):
    if settings.verbose:
        log('__Deleting__ %s' % os.path.join(dest, fname))
    destf = os.path.join(dest, fname)
    cmd = 'rm -rf "%s"' % os.path.join(dest, fname)
    if not settings.dry_run:
        try:
            system(cmd)
        except Exception, e:
            sys.stderr.write('Failed to delete %s: %s' % (destf, e))

def log(msg):
    if not settings.quiet:
        print(msg)

def system(cmd, allowed_exit_statuses=[0]):
    # see e.g. http://mail.python.org/pipermail/python-list/2003-May/205411.html
    exit_status = os.system(cmd)
    normal_exit = (exit_status % 256 == 0)
    if not exit_status in allowed_exit_statuses:
        raise Exception('command %s exited with code %d (%d)' % 
                             (cmd, exit_status, exit_status / 256))
    return exit_status


if __name__ == '__main__':
    treesync = Treesync()
    treesync.run()
