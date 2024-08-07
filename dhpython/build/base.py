# Copyright © 2012-2013 Piotr Ożarowski <piotr@debian.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import logging
from functools import wraps
from glob import glob1
from os import remove, walk
from os.path import exists, isdir, join
from pathlib import Path
from shlex import quote
from shutil import rmtree, copyfile, copytree, which
from dhpython.debhelper import DebHelper, build_options
from dhpython.exceptions import RequiredCommandMissingException
from dhpython.tools import execute

log = logging.getLogger('dhpython')


def copy_test_files(dest='{build_dir}',
                    filelist='{home_dir}/testfiles_to_rm_before_install',
                    add_to_args=('test', 'tests')):

    def _copy_test_files(func):

        @wraps(func)
        def __copy_test_files(self, context, args, *oargs, **kwargs):
            files_to_copy = {'pyproject.toml', 'pytest.ini', 'test', 'tests'}
            # check debian/pybuild_pythonX.Y.testfiles
            for tpl in ('_{i}{v}', '_{i}{m}', ''):
                tpl = tpl.format(i=args['interpreter'].name,
                                 v=args['version'],
                                 m=args['version'].major)
                fpath = join(args['dir'], 'debian/pybuild{}.testfiles'.format(tpl))
                if exists(fpath):
                    with open(fpath, encoding='utf-8') as fp:
                        # overwrite files_to_copy if .testfiles file found
                        files_to_copy = [line.strip() for line in fp.readlines()
                                         if not line.startswith('#')]
                        break

            files_to_remove = set()
            for name in files_to_copy:
                src_dpath = join(args['dir'], name)
                dst_dpath = join(dest.format(**args), name.rsplit('/', 1)[-1])
                if exists(src_dpath):
                    if not exists(dst_dpath):
                        log.debug("Copying %s to %s for tests", src_dpath, dst_dpath)
                        if isdir(src_dpath):
                            copytree(src_dpath, dst_dpath)
                        else:
                            copyfile(src_dpath, dst_dpath)
                        files_to_remove.add(dst_dpath + '\n')
                    if not args['args'] and 'PYBUILD_TEST_ARGS' not in context['ENV']\
                       and (self.cfg.test_pytest or self.cfg.test_nose) \
                       and name in add_to_args:
                        args['args'] = name
            if files_to_remove and filelist:
                with open(filelist.format(**args), 'a', encoding="UTF-8") as fp:
                    fp.writelines(files_to_remove)

            return func(self, context, args, *oargs, **kwargs)
        return __copy_test_files
    return _copy_test_files


class Base:
    """Base class for build system plugins

    :attr REQUIRED_COMMANDS: list of command checked by default in :meth:is_usable,
        if one of them is missing, plugin cannot be used.
    :type REQUIRED_COMMANDS: list of strings
    :attr REQUIRED_FILES: list of files (or glob templates) required by given
        build system
    :attr OPTIONAL_FILES: dictionary of glob templates (key) and score (value)
        used to detect if given plugin is the best one for the job
    :type OPTIONAL_FILES: dict (key is a string, value is an int)
    :attr SUPPORTED_INTERPRETERS: set of interpreter templates (with or without
        {version}) supported by given plugin
    """
    DESCRIPTION = ''
    REQUIRED_COMMANDS = []
    REQUIRED_FILES = []
    OPTIONAL_FILES = {}
    SUPPORTED_INTERPRETERS = {'python', 'python3', 'python-dbg', 'python3-dbg',
                              'python{version}', 'python{version}-dbg'}
    # files and directories to remove during clean step (other than .pyc):
    CLEAN_FILES = {'.pytest_cache', '.coverage'}

    def __init__(self, cfg):
        self.cfg = cfg

    def __repr__(self):
        return "BuildSystem(%s)" % self.NAME

    @classmethod
    def is_usable(cls):
        for command in cls.REQUIRED_COMMANDS:
            pth = which(command)
            if not pth:
                raise RequiredCommandMissingException(command)

    def detect(self, context):
        """Return certainty level that this plugin describes the right build system

        This method is using cls.{REQUIRED,OPTIONAL}_FILES only by default,
        please extend it in the plugin if more sofisticated methods can be used
        for given build system.

        :return: 0 <= certainty <= 100
        :rtype: int
        """
        result = 0

        required_files_num = 0
        self.DETECTED_REQUIRED_FILES = {}  # can be used in the plugin later
        for tpl in self.REQUIRED_FILES:
            found = False
            for ftpl in tpl.split('|'):
                res = glob1(context['dir'], ftpl)
                if res:
                    found = True
                    self.DETECTED_REQUIRED_FILES.setdefault(tpl, []).extend(res)
            if found:
                required_files_num += 1
        # add max 50 points depending on how many required files are available
        if self.REQUIRED_FILES:
            result += int(required_files_num / len(self.REQUIRED_FILES) * 50)

        self.DETECTED_OPTIONAL_FILES = {}
        for ftpl, score in self.OPTIONAL_FILES.items():
            res = glob1(context['dir'], ftpl)
            if res:
                result += score
                self.DETECTED_OPTIONAL_FILES.setdefault(ftpl, []).extend(res)
        if result > 100:
            return 100
        return result

    def clean(self, context, args):
        tox_dir = join(args['dir'], '.tox')
        if isdir(tox_dir):
            try:
                rmtree(tox_dir)
            except Exception:
                log.debug('cannot remove %s', tox_dir)

        for fn in self.CLEAN_FILES:
            path = join(context['dir'], fn)
            if isdir(path):
                try:
                    rmtree(path)
                except Exception:
                    log.debug('cannot remove %s', path)
            elif exists(path):
                try:
                    remove(path)
                except Exception:
                    log.debug('cannot remove %s', path)

        dh = DebHelper(build_options())
        # Plugins that rely on repository contents to build MANIFEST
        clean_sources_txt = not set(
            ('python3-setuptools-scm', 'python3-setuptools-git')
        ).intersection(set(dh.build_depends))

        for root, dirs, file_names in walk(context['dir']):
            for name in dirs[:]:
                if name == '__pycache__' or (
                        clean_sources_txt and name.endswith('.egg-info')):
                    dpath = join(root, name)
                    log.debug('removing dir: %s', dpath)
                    try:
                        rmtree(dpath)
                    except Exception:
                        log.debug('cannot remove %s', dpath)
                    else:
                        dirs.remove(name)
            for fn in file_names:
                if fn.endswith(('.pyc', '.pyo')):
                    fpath = join(root, fn)
                    log.debug('removing: %s', fpath)
                    try:
                        remove(fpath)
                    except Exception:
                        log.debug('cannot remove %s', fpath)
            if root.endswith('.egg-info'):
                for fn in file_names:
                    if fn != 'SOURCES.txt':
                        fpath = join(root, fn)
                        log.debug('removing: %s', fpath)
                        try:
                            remove(fpath)
                        except Exception:
                            log.debug('cannot remove %s', fpath)

    def configure(self, context, args):
        raise NotImplementedError("configure method not implemented in %s" % self.NAME)

    def install(self, context, args):
        raise NotImplementedError("install method not implemented in %s" % self.NAME)

    def build(self, context, args):
        raise NotImplementedError("build method not implemented in %s" % self.NAME)

    @copy_test_files()
    def test(self, context, args):
        if self.cfg.test_nose2:
            return 'cd {build_dir}; {interpreter} -m nose2 -v {args}'
        elif self.cfg.test_nose:
            return 'cd {build_dir}; {interpreter} -m nose -v {args}'
        elif self.cfg.test_pytest:
            return 'cd {build_dir}; {interpreter} -m pytest {args}'
        elif self.cfg.test_tox:
            tox_config = None
            if exists(join(args['dir'], 'tox.ini')):
                tox_config = '{dir}/tox.ini'
            elif exists(join(args['dir'], 'pyproject.toml')):
                tox_config = '{dir}/pyproject.toml'
            elif exists(join(args['dir'], 'setup.cfg')):
                tox_config = '{dir}/setup.cfg'
            else:
                raise Exception("tox config not found. "
                    "Expected to find tox.ini, pyproject.toml, or setup.cfg")

            tox_cmd = ['cd {build_dir};',
                   'tox',
                   '-c', tox_config,
                   '--sitepackages',
                   '-e', 'py{version.major}{version.minor}',
                   '-x', 'testenv.passenv+=_PYTHON_HOST_PLATFORM',
            ]
            if args['autopkgtest']:
                tox_cmd += ['--skip-pkg-install']

            # --installpkg was added in tox 4. Keep tox 3 support for now,
            # for backportability
            r = execute(['tox', '--version', '--quiet'], shell=False)
            try:
                major_version = int(r['stdout'].split('.', 1)[0])
            except ValueError as err:
                raise Exception(f"tox was installed but broken: stdout='{r['stdout']}', stderr='{r['stderr']}'") from err
            if major_version < 4:
                # tox will call pip to install the module. Let it install the
                # module inside the virtualenv
                pydistutils_cfg = join(args['home_dir'], '.pydistutils.cfg')
                if exists(pydistutils_cfg):
                    remove(pydistutils_cfg)
            else:
                if not args['autopkgtest']:
                    wheel = self.built_wheel(context, args)
                    if not wheel:
                        self.build_wheel(context, args)
                        wheel = self.built_wheel(context, args)
                    args['wheel'] = wheel
                    tox_cmd += ['--installpkg', '{wheel}']

            tox_cmd.append('{args}')
            return ' '.join(tox_cmd)
        elif self.cfg.test_stestr:
            return (
                'cd {build_dir};'
                'stestr --config {dir}/.stestr.conf init;'
                'PYTHON=python{version} stestr --config {dir}/.stestr.conf run'
            )
        elif self.cfg.test_custom:
            return 'cd {build_dir}; {args}'
        else:
            # Temporary: Until Python 3.12 is established, and packages without
            # test suites have explicitly disabled tests.
            args['ignore_no_tests'] = True
            return 'cd {build_dir}; {interpreter} -m unittest discover -v {args}'

    def build_wheel(self, context, args):
        raise NotImplementedError("build_wheel method not implemented in %s" % self.NAME)

    def built_wheel(self, context, args):
        """Return the path to any built wheels we can find"""
        # pylint: disable=unused-argument
        wheels = list(Path(args['home_dir']).glob('*.whl'))
        n_wheels = len(wheels)
        if n_wheels > 1:
            raise Exception(f"Expecting to have built exactly 1 wheel, but found {n_wheels}")
        if n_wheels == 1:
            return str(wheels[0])
        return None

    def execute(self, context, args, command, log_file=None):
        if log_file is False and self.cfg.really_quiet:
            log_file = None
        command = command.format(**args)
        env = dict(context['ENV'])
        if 'ENV' in args:
            env.update(args['ENV'])
        log.info(command)
        return execute(command, context['dir'], env, log_file)

    def print_args(self, context, args):
        # pylint: disable=unused-argument
        cfg = self.cfg
        if len(cfg.print_args) == 1 and len(cfg.interpreter) == 1 and '{version}' not in cfg.interpreter[0]:
            i = cfg.print_args[0]
            if '{' in i:
                print(i.format(**args))
            else:
                print(args.get(i, ''))
        else:
            for i in cfg.print_args:
                if '{' in i:
                    print(i.format(**args))
                else:
                    print('{} {}: {}'.format(args['interpreter'], i, args.get(i, '')))


def shell_command(func):

    @wraps(func)
    def wrapped_func(self, context, args, *oargs, **kwargs):
        command = kwargs.pop('command', None)
        if not command:
            command = func(self, context, args, *oargs, **kwargs)
            if isinstance(command, int):  # final result
                return command
        if not command:
            log.warning('missing command '
                     '(plugin=%s, method=%s, interpreter=%s, version=%s)',
                     self.NAME, func.__name__,
                     args.get('interpreter'), args.get('version'))
            return command

        if self.cfg.quiet:
            log_file = join(args['home_dir'], '{}_cmd.log'.format(func.__name__))
        else:
            log_file = False

        quoted_args = dict((k, quote(v)) if k in ('dir', 'destdir')
                           or k.endswith('_dir') else (k, v)
                           for k, v in args.items())
        command = command.format(**quoted_args)

        output = self.execute(context, args, command, log_file)
        if output['returncode'] == 5 and args.get('ignore_no_tests', False):
            # Temporary hack (see Base.test)
            pass
        elif output['returncode'] != 0:
            msg = 'exit code={}: {}'.format(output['returncode'], command)
            if log_file:
                msg += '\nfull command log is available in {}'.format(log_file)
            raise Exception(msg)
        return True

    return wrapped_func
