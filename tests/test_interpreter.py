import unittest
from os import environ
from os.path import exists
from dhpython.interpreter import Interpreter


class TestInterpreter(unittest.TestCase):
    def setUp(self):
        self._triplet = environ.get('DEB_HOST_MULTIARCH')
        environ['DEB_HOST_MULTIARCH'] = 'MYARCH'

    def tearDown(self):
        if self._triplet:
            environ['DEB_HOST_MULTIARCH'] = self._triplet

    @unittest.skipUnless(exists('/usr/bin/python3.1'), 'python3.1 is not installed')
    def test_python31(self):
        i = Interpreter('python3.1')
        self.assertEqual(i.soabi(), '')
        self.assertIsNone(i.check_extname('foo.so'))
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertIsNone(i.check_extname('foo/bar/bazmodule.so'))

    @unittest.skipUnless(exists('/usr/bin/python3.1-dbg'), 'python3.1-dbg is not installed')
    def test_python31dbg(self):
        i = Interpreter('python3.1-dbg')
        self.assertEqual(i.soabi(), '')
        self.assertIsNone(i.check_extname('foo.so'))
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertIsNone(i.check_extname('foo/bar/bazmodule.so'))

    @unittest.skipUnless(exists('/usr/bin/python3.2'), 'python3.2 is not installed')
    def test_python32(self):
        i = Interpreter('python3.2')
        self.assertEqual(i.soabi(), 'cpython-32mu')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-32mu.so')
        self.assertIsNone(i.check_extname('foo.cpython-33m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-32mu-OTHER.so'))  # different architecture
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/bazmodule.cpython-32mu.so')

    @unittest.skipUnless(exists('/usr/bin/python3.2-dbg'), 'python3.2-dbg is not installed')
    def test_python32dbg(self):
        i = Interpreter('python3.2-dbg')
        self.assertEqual(i.soabi(), 'cpython-32dmu')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-32dmu.so')
        self.assertIsNone(i.check_extname('foo.cpython-33m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-32dmu-OTHER.so'))  # different architecture
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/bazmodule.cpython-32dmu.so')

    @unittest.skipUnless(exists('/usr/bin/python3.4'), 'python3.4 is not installed')
    def test_python34(self):
        i = Interpreter('python3.4')
        self.assertEqual(i.soabi(), 'cpython-34m')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-34m-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.cpython-32m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-34m-OTHER.so'))  # different architecture
        self.assertEqual(i.check_extname('foo.cpython-34m.so'), r'foo.cpython-34m-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/baz.cpython-34m-MYARCH.so')

    @unittest.skipUnless(exists('/usr/bin/python3.4-dbg'), 'python3.4-dbg is not installed')
    def test_python34dbg(self):
        i = Interpreter('python3.4-dbg')
        self.assertEqual(i.soabi(), 'cpython-34dm')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-34dm-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.cpython-32m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-34m-OTHER.so'))  # different architecture
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/baz.cpython-34dm-MYARCH.so')

    @unittest.skipUnless(exists('/usr/bin/python3.5'), 'python3.5 is not installed')
    def test_python35(self):
        i = Interpreter('python3.5')
        self.assertEqual(i.soabi(), 'cpython-35m')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-35m-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.cpython-32m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-35m-OTHER.so'))  # different architecture
        self.assertEqual(i.check_extname('foo.cpython-35m.so'), r'foo.cpython-35m-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/baz.cpython-35m-MYARCH.so')

    @unittest.skipUnless(exists('/usr/bin/python3.5-dbg'), 'python3.5-dbg is not installed')
    def test_python35dbg(self):
        i = Interpreter('python3.5-dbg')
        self.assertEqual(i.soabi(), 'cpython-35dm')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-35dm-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.cpython-32m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-35m-OTHER.so'))  # different architecture
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/baz.cpython-35dm-MYARCH.so')

    @unittest.skipUnless(exists('/usr/bin/python3.6'), 'python3.6 is not installed')
    def test_python36(self):
        i = Interpreter('python3.6')
        self.assertEqual(i.soabi(), 'cpython-36m')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-36m-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.cpython-32m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-36m-OTHER.so'))  # different architecture
        self.assertEqual(i.check_extname('foo.cpython-36m.so'), r'foo.cpython-36m-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/baz.cpython-36m-MYARCH.so')

    @unittest.skipUnless(exists('/usr/bin/python3.6-dbg'), 'python3.6-dbg is not installed')
    def test_python36dbg(self):
        i = Interpreter('python3.6-dbg')
        self.assertEqual(i.soabi(), 'cpython-36dm')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-36dm-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.cpython-32m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-36m-OTHER.so'))  # different architecture
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/baz.cpython-36dm-MYARCH.so')

    @unittest.skipUnless(exists('/usr/bin/python3.7'), 'python3.7 is not installed')
    def test_python37(self):
        i = Interpreter('python3.7')
        self.assertEqual(i.soabi(), 'cpython-37m')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-37m-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.cpython-32m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-37m-OTHER.so'))  # different architecture
        self.assertEqual(i.check_extname('foo.cpython-37m.so'), r'foo.cpython-37m-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/baz.cpython-37m-MYARCH.so')

    @unittest.skipUnless(exists('/usr/bin/python3.7-dbg'), 'python3.7-dbg is not installed')
    def test_python37dbg(self):
        i = Interpreter('python3.7-dbg')
        self.assertEqual(i.soabi(), 'cpython-37dm')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-37dm-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.cpython-32m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-37m-OTHER.so'))  # different architecture
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/baz.cpython-37dm-MYARCH.so')

    @unittest.skipUnless(exists('/usr/bin/python3.8'), 'python3.8 is not installed')
    def test_python38(self):
        i = Interpreter('python3.8')
        self.assertEqual(i.soabi(), 'cpython-38')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-38-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.cpython-32m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-38-OTHER.so'))  # different architecture
        self.assertEqual(i.check_extname('foo.cpython-38.so'), r'foo.cpython-38-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/baz.cpython-38-MYARCH.so')

    @unittest.skipUnless(exists('/usr/bin/python3.8-dbg'), 'python3.8-dbg is not installed')
    def test_python38dbg(self):
        i = Interpreter('python3.8-dbg')
        self.assertEqual(i.soabi(), 'cpython-38d')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-38d-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.cpython-32m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-38-OTHER.so'))  # different architecture
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/baz.cpython-38d-MYARCH.so')

    @unittest.skipUnless(exists('/usr/bin/python3.9'), 'python3.9 is not installed')
    def test_python39(self):
        i = Interpreter('python3.9')
        self.assertEqual(i.soabi(), 'cpython-39')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-39-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.cpython-32m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-39-OTHER.so'))  # different architecture
        self.assertEqual(i.check_extname('foo.cpython-39.so'), r'foo.cpython-39-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/baz.cpython-39-MYARCH.so')

    @unittest.skipUnless(exists('/usr/bin/python3.9-dbg'), 'python3.9-dbg is not installed')
    def test_python39dbg(self):
        i = Interpreter('python3.9-dbg')
        self.assertEqual(i.soabi(), 'cpython-39d')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-39d-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.cpython-32m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-39-OTHER.so'))  # different architecture
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/baz.cpython-39d-MYARCH.so')

    @unittest.skipUnless(exists('/usr/bin/python3.10'), 'python3.10 is not installed')
    def test_python310(self):
        i = Interpreter('python3.10')
        self.assertEqual(i.soabi(), 'cpython-310')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-310-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.cpython-32m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-310-OTHER.so'))  # different architecture
        self.assertEqual(i.check_extname('foo.cpython-310.so'), r'foo.cpython-310-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/baz.cpython-310-MYARCH.so')

    @unittest.skipUnless(exists('/usr/bin/python3.10-dbg'), 'python3.10-dbg is not installed')
    def test_python310dbg(self):
        i = Interpreter('python3.10-dbg')
        self.assertEqual(i.soabi(), 'cpython-310d')
        self.assertEqual(i.check_extname('foo.so'), r'foo.cpython-310d-MYARCH.so')
        self.assertIsNone(i.check_extname('foo.cpython-32m.so'))  # different version
        self.assertIsNone(i.check_extname('foo.cpython-310-OTHER.so'))  # different architecture
        self.assertIsNone(i.check_extname('foo.abi3.so'))
        self.assertEqual(i.check_extname('foo/bar/bazmodule.so'), r'foo/bar/baz.cpython-310d-MYARCH.so')


if __name__ == '__main__':
    unittest.main()
