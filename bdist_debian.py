# bdist_debian.py
#
# Add 'bdist_debian' Debian binary package distribution support to 'distutils'.
#
# This command builds '.deb' packages and supports the "Maemo" extensions for the Nokia N770/N800/N810.
#
# Written by: Gene Cash <gene.cash@gmail.com> 16-NOV-2007
#
# Ammended for Wah!Cade by: Andy Balcombe <wahcade@anti-particle.com> 24-MAR-2008
# Tweaked for Mah!Cade by: Wayne Moulden <wahkisubmit@gmail.com> 01-MAY-2011

import os
import base64
import hashlib
from distutils.core import Command, Distribution
from distutils.dir_util import remove_tree

# make these legal keywords for setup()
Distribution.section=None
Distribution.depends=None
Distribution.recommends=None
Distribution.suggests=None


class ControlFile(object):

    def __init__(self, Installed_Size=0, Long_Description='', Description='', **kwargs):
        self.options = kwargs
        self.description = Description
        self.long_description = Long_Description
        self.installed_size = Installed_Size

    def getContent(self):
        """build content of control file"""
        #best order for options
        order = ['6:Recommends', '4:Maintainer', '1:Package', '8:Section', '9:Priority', '7:Suggests', '5:Depends', '2:Version', '3:Architecture']
        order.sort()
        #
        content = []
        for o in order:
            opt = o[2:]
            if opt in self.options:
                content.append('%s: %s' % (opt, self.options[opt]))
        #content=['%s: %s' % (k, v) for k,v in self.options.iteritems()]
        content.append('Installed-Size: %d' % self.installed_size)
        if self.description != 'UNKNOWN':
            content.append('Description: %s' % self.description.strip())
            if self.long_description != 'UNKNOWN':
                self.long_description=self.long_description.replace('\n', '\n ')
                content.append(' '+self.long_description.strip() + '\n')
        #done
        return '\n'.join(content)+'\n'


class bdist_debian(Command):
    description=''
    # List of option tuples: long name, short name (None if no short name), and help string.
    user_options=[('name=', None, 'Application name'),
                  ('section=', None, 'Section (Only "user/*" will display in App Mgr usually)'),
                  ('priority=', None, 'Priority'),
                  ('depends=', None, 'Other Debian package dependencies (comma separated)'),
                  ('recommends=', None, 'Other recommended Debian package dependencies (comma separated)'),
                  ('suggests=', None, 'Other suggested Debian package dependencies (comma separated)')]

    def initialize_options(self):
        self.section=None
        self.priority=None
        self.depends=None
        self.recommends=None
        self.suggests=None

    def finalize_options(self):
        if self.section is None:
            self.section='user/other'

        if self.priority is None:
            self.priority='optional'

        self.maintainer='%s <%s>' % (self.distribution.get_maintainer(), self.distribution.get_maintainer_email())

        if self.depends is None:
            self.depends='python2.5'

        self.name=self.distribution.get_name()
        self.description=self.distribution.get_description()
        self.long_description=self.distribution.get_long_description()
        #self.version=self.distribution.get_version()
        for line in open ('VERSION','r'):
                self.version = line.rstrip('\n')

        # process new keywords
        if self.distribution.section != None:
            self.section=self.distribution.section
        if self.distribution.depends != None:
            self.depends=self.distribution.depends
        if self.distribution.recommends != None:
            self.recommends=self.distribution.recommends
        if self.distribution.suggests != None:
            self.suggests=self.distribution.suggests

    def run(self):
        build_dir = os.path.join(self.get_finalized_command('build').build_base, 'wahcade')
        dist_dir = 'dist'
        binary_fn = 'debian-binary'
        control_fn = './control'
        md5sums_fn = './md5sums'
        data_fn = 'data'
        tgz_ext = '.tar.gz'

        #
        md5 = ''
        # build everything locally
        self.run_command('build')
        install=self.reinitialize_command('install', reinit_subcommands=1)
        install.root=build_dir
        self.run_command('install')

        # find out how much space it takes
        installed_size=0
        for root, dirs, files in os.walk('build'):
            for name in files:
                fname=os.path.join(root, name)
                installed_size += os.path.getsize(fname)
                if fname.startswith(build_dir):
                    m = hashlib.md5()
                    [m.update(l) for l in file(fname, 'r').readlines()]
                    fname = fname.replace(build_dir, '')[1:]
                    md5 += '%s %s\n' % (m.hexdigest(), fname)

        # make compressed tarball
        self.make_archive(os.path.join(dist_dir, data_fn), 'gztar', root_dir=build_dir)

        # remove all the stuff we just built
        remove_tree(build_dir)

        # create control file contents
        ctl = ControlFile(
            Package = self.name,
            Version = self.version,
            Section = self.section,
            Priority = self.priority,
            Installed_Size = (installed_size / 1024) + 1,
            Architecture = 'all',
            Maintainer = self.maintainer,
            Depends = self.depends,
            Description = self.description,
            Long_Description = self.long_description,
            Recommends = self.recommends,
            Suggests = self.suggests).getContent()

        # grab scripts
        scripts={}
        for fn in ('postinst', 'preinst', 'postrm', 'prerm', 'config'):
            if os.path.exists(fn):
                scripts[fn]=file(fn, 'rb').read()

        # now to create the deb package
        os.chdir(dist_dir)

        # write control file
        file(control_fn, 'wb').write(ctl)

        #write md5sums file
        file(md5sums_fn, 'wb').write(md5)

        # write any scripts and chmod a+rx them
        files=[control_fn, md5sums_fn]
        for fn in scripts:
            files.append(fn)
            file(fn, 'wb').write(scripts[fn])
            os.chmod(fn, 0555)

        # make "control" compressed tarball with control file and any scripts
        self.spawn(['tar', '-czf', control_fn + tgz_ext] + files)

        # make debian-binary file
        file(binary_fn, 'wb').write('2.0\n')

        # make final archive
        package_filename='%s_%s_all.deb' % (self.name, self.version)
        #self.spawn(['ar', '-cr', package_filename, binary_fn, control_fn+tgz_ext, data_fn+tgz_ext])

        #fixed deb builder script
        fix_script = """#!/bin/sh
echo Started
mkdir -p tmp/DEBIAN
cd tmp
tar -xzvpf ../data.tar.gz
cd DEBIAN
tar -xzvpf ../../control.tar.gz
cp ../../debian-binary ./
# Make some tweak to preinst/postinst/etc...
cd ../../
dpkg-deb -b tmp %s
# new.deb should not cause the same complaints
#rm -rf tmp
""" % (package_filename)

        #write the script & execute it
        file('fix_deb', 'w').write(fix_script)
        os.chmod('fix_deb', 0755)
        os.system('./fix_deb')
