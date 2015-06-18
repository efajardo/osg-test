import os
import errno
import shutil

import osgtest.library.core as core
import osgtest.library.osgunittest as osgunittest

class TestCert(osgunittest.OSGTestCase):

    def test_01_install_host_cert(self):
        core.state['certs.hostcert_created'] = False
        try:
            host_cert_dir = '/etc/grid-security'
            os.mkdir(host_cert_dir)
        except OSError, e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        if core.options.hostcert:
            host_cert = os.path.join(host_cert_dir, 'hostcert.pem')
            host_key = os.path.join(host_cert_dir, 'hostkey.pem')
            self.assertFalse(os.path.exists(host_cert) or os.path.exists(host_key), "hostcert or hostkey already exist")
            shutil.copy2('/usr/share/osg-test/hostcert.pem', host_cert_dir)
            shutil.copy2('/usr/share/osg-test/hostkey.pem', host_cert_dir)
            os.chmod(host_cert, 0644)
            os.chmod(host_key, 0400)
            core.state['certs.hostcert_created'] = True
