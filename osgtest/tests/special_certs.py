import os
import unittest
import osgtest.library.core as core
import osgtest.library.certificates as certs

class TestUser(unittest.TestCase):

    def test_01_configure_openssl(self):
        certs_dir= '/etc/grid-security/certificates'
        core.state['certs.dir_created'] = False        
        certs.configure_openssl()

        if not os.path.exists(certs_dir):
            core.state['certs.dir_created'] = True
            os.mkdir(certs_dir, 0755)
        
        certs.create_ca(certs_dir)
        certs.create_crl()
    
