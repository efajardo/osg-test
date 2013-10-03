import os
import unittest
import osgtest.library.core as core
import osgtest.library.certificates as certs

class TestUser(unittest.TestCase):

    def test_01_install_ca_and_crl(self):
        certs_dir= '/etc/grid-security/certificates'
        core.state['certs.dir_created'] = False        
        certs.configure_openssl()

        if not os.path.exists(certs_dir):
            core.state['certs.dir_created'] = True
            os.mkdir(certs_dir, 0755)
        
        certs.create_ca(certs_dir)
        certs.create_crl()
    
    def test_02_install_host_cert(self):
        host_cert_dir = '/etc/grid-security'
        host_cert = host_cert_dir + "/hostcert.pem"
        host_key = host_cert_dir + "/hostkey.pem"
        core.state['certs.hostcert_created'] = False
        
        self.assertFalse(os.path.exists(host_cert) or os.path.exists(host_key), "hostcert or hostkey already exist")
        
        if core.options.hostcert:
            certs.create_host_cert(host_cert_dir)
            core.state['certs.hostcert_created'] = True

