'''
Used to compile a redistributable salt local only environment
'''
# Import python libs
import os
import shutil
import urllib2
import subprocess
import sys

import distutils.command.sdist
from distutils.core import setup

components = {
              'Jinja2-2.7': 'https://pypi.python.org/packages/source/J/Jinja2/Jinja2-2.7.tar.gz',
              'MarkupSafe-0.18': 'https://pypi.python.org/packages/source/M/MarkupSafe/MarkupSafe-0.18.tar.gz',
              'msgpack-pure-0.1.3': 'https://pypi.python.org/packages/source/m/msgpack-pure/msgpack-pure-0.1.3.tar.gz',
              'PyYAML-3.10': 'https://pypi.python.org/packages/source/P/PyYAML/PyYAML-3.10.tar.gz'
              }
libs = set([
            'salt',
            'yaml',
            'jinja2',
            'msgpack_pure',
            'markupsafe',
            ])

CWD = os.getcwd()
PATH = os.environ['PATH']

prereqs = set([
            'wget',
            'git',
            'tar',
            ])

def check_prereq():
    '''
    Check to ensure the system has the necessary tools to run this script
    '''
    failed_deps = [] 
    for req in prereqs:
        found = False
        for path in PATH.split(os.pathsep):
            if os.path.exists(os.path.join(path, req)):
                found = True
        if not found:
            failed_deps.append(req)

    return failed_deps

def build_setup(salt, git_version = None):
    '''
    Download the components
    '''
    for failed_req in check_prereq():
        print "{0} not installed. Aborting!".format(failed_req)
        sys.exit(1)

    for name, addr in components.items():
        subprocess.call('wget --no-check-certificate {0}'.format(addr), shell=True)
        subprocess.call('tar xvf {0}'.format(os.path.basename(addr)), shell=True)
        for sub in os.listdir(name):
            full = os.path.join(name, sub)
            if not os.path.isdir(full):
                continue
            if sub in libs:
                shutil.copytree(full, os.path.join(CWD, sub))
                continue
            if sub == 'lib':
                shutil.copytree(os.path.join(full, 'yaml'), os.path.join(CWD, 'yaml'))
    if salt == 'git':
        subprocess.call('git clone https://github.com/saltstack/salt.git', shell=True)
        shutil.move('salt', 'salt_git')
        cwd = os.getcwd()
        try:
            os.chdir("salt_git")
            subprocess.call('git checkout {0}'.format(git_version), shell=True)
        finally:
            os.chdir(cwd)
        shutil.move('salt_git/salt', os.path.join(CWD, 'salt'))
    else:
        tar_tgt = '{0}.tgz'.format(name)
        url = urllib2.urlopen(
                'https://github.com/saltstack/salt/archive/{0}.tar.gz'.format(salt)
                )
        with open(tar_tgt, 'w+') as fp_:
            fp_.write(url.read())
            subprocess.call('tar xvf {0}'.format(tar_tgt), shell=True)
            for sub in os.listdir(name):
                full = os.path.join(name, sub)
                if not os.path.isdir(full):
                    continue
                if sub in libs:
                    shutil.copytree(full, os.path.join(CWD, sub))
    shutil.copy('salt_git/scripts/salt-call', os.path.join(CWD, 'salt-call'))
    shutil.copy('salt_git/scripts/salt-ssh', os.path.join(CWD, 'salt-ssh'))


def clean():
    '''
    Clean up!
    '''
    for name in components:
        shutil.rmtree(name)
        os.remove('{0}.tgz'.format(name))
    shutil.rmtree('salt_git')
    for name in libs:
        shutil.rmtree(name)

class sdist(distutils.command.sdist.sdist):
    '''
    Subclass of sdist subcommand for optional git version.
    '''
    user_options = distutils.command.sdist.sdist.user_options + [
        ('git-version=', None, 'Specify Git version'),
    ]

    def initialize_options(self, *args, **kwargs):
        self.git_version = 'develop'
        distutils.command.sdist.sdist.initialize_options(self, *args, **kwargs)

    def run(self, *args, **kwargs):
        self.distribution.metadata.version = self.git_version
        build_setup('git', self.git_version)
        distutils.command.sdist.sdist.run(self, *args, **kwargs)

setup(name='salt-thin',
      version=None,
      description='Salt without the network and bundled deps',
      author='Thomas S Hatch',
      author_email='thatch@saltstack.com',
      url='https://github.com/saltstack/salt-thin',
      scripts=['salt-call', 'salt-ssh'],
      cmdclass={'sdist': sdist},
)
