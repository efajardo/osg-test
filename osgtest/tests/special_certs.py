import os
import shutil

import osgtest.library.core as core
import osgtest.library.files as files
import osgtest.library.osgunittest as osgunittest

class TestCert(osgunittest.OSGTestCase):

    def test_01_install_host_cert(self):
        host_cert_dir = '/etc/grid-security'
        core.state['certs.hostcert_created'] = False

        if core.options.hostcert:
            self.assertFalse(os.path.exists(host_cert) or os.path.exists(host_key), "hostcert or hostkey already exist")
            shutil.copy2('/usr/share/osg-test/hostcert.pem', globus_dir)
            shutil.copy2('/usr/share/osg-test/hostkey.pem', globus_dir)
            host_cert = os.path.join(globus_dir, 'hostcert.pem')
            host_key = os.path.join(globus_dir, 'hostkey.pem')
            os.chmod(host_cert, 0644)
            os.chmod(host_key, 0400)
            core.state['certs.hostcert_created'] = True
