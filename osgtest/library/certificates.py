"""Utilities for creating CAs, certificates and CRLs"""

import os
import re

import osgtest.library.core as core
import osgtest.library.files as files

openssl_config = '/etc/pki/tls/openssl.cnf'
cert_ext_config = '/usr/share/osg-test/openssl-cert-extensions.conf' 
ca_file = "OSG-Test-CA.pem"
ca_key = "OSG-Test-CA.key"
crl_file = "OSG-Test-CA.r0"
host_request = "host_req"
dn = '/DC=org/DC=Open Science Grid/O=OSG Test/CN=OSG Test CA'
days = '1'
sn = "A1B2C3D4E5F6"

def configure_openssl():
    """Lays down files and configuration for creating CAs, certs and CRLs"""
    working_dir = os.getcwd()
    # Instead of patching openssl's config file
    files.replace(openssl_config, "# crl_extensions	= crl_ext", "crl_extensions	= crl_ext", owner="CA")
    files.replace(openssl_config, "basicConstraints = CA:true", "basicConstraints = critical, CA:true", backup=False)
    files.replace(openssl_config,
                  "# keyUsage = cRLSign, keyCertSign",
                  "keyUsage = critical, digitalSignature, cRLSign, keyCertSign",
                  backup=False)
    files.replace(openssl_config,
                  "dir		= ../../CA		# Where everything is kept",
                  "dir		= %s		# Where everything is kept" % working_dir,
                  backup=False)

    # Patches openssl-cert-extensions.conf
    files.replace(cert_ext_config,
                  'subjectAltName=DNS:##HOSTNAME##',
                  'subjectAltName=DNS:%s' % core.get_hostname(),
                  owner="CA")
    
    # Put down necessary files
    files.write("index.txt", "", backup=False)
    files.write("serial", sn, backup=False)
    files.write("crlnumber", "01", backup=False)

def create_ca(path):
    """Create a CA similar to DigiCert's """
    core.config['certs.test-ca'] = path + "/" + ca_file
    core.config['certs.test-ca-key'] = path + "/" + ca_key

    command = ("openssl", "genrsa", "-out", core.config['certs.test-ca-key'], "2048")
    core.check_system(command, 'generate CA private key')

    command = ("openssl", "req", "-new", "-x509", "-out", core.config['certs.test-ca'], "-key", 
               core.config['certs.test-ca-key'], "-subj", dn, "-config", openssl_config, "-days", days)
    core.check_system(command, 'generate CA')

def create_host_cert():
    """Create a cert similar to DigiCert's"""
    host_pk_der = "hostkey.der"
    host_pk = "hostkey.pem"
    host_cert = "hostcert.pem"

    command = ("openssl", "req", "-new", "-nodes", "-out", host_request, "-keyout", host_pk_der,"-subj", dn)
    core.check_system(command, 'generate host cert request')
    # Have to run the private key through RSA to get proper format (-keyform doesn't work in openssl > 0.9.8)
    command = ("openssl", "rsa", "-in", host_pk_der, "-outform", "PEM", "-out", host_pk) 
    core.check_system(command, "generate host private key") 
    files.remove(host_pk_der)
    os.chmod(host_pk, 0400)

    command = ("openssl", "ca", "-config", openssl_config, "-cert", ca_file, "-keyfile", ca_key, "-days", days,
               "-policy", "policy_anything", "-preserveDN", "-extfile", cert_ext_config, "-in", host_request, "-notext",
               "-out", host_cert, "-outdir", ".", "-batch")
    core.check_system(command, "generate host cert")

 
def create_crl():
    """Create CRL to accompany our CA."""
    core.config['certs.test-crl'] = os.path.dirname(core.config['certs.test-ca']) + "/" + crl_file
        
    command = ("openssl", "ca", "-gencrl", "-config", openssl_config, "-cert", core.config['certs.test-ca'], "-keyfile",
               core.config['certs.test-ca-key'], "-crldays", days, "-out", core.config['certs.test-crl'])
    core.check_system(command, "generate CRL")

def cleanup_files():
    """Cleanup openssl files and config we laid down"""
    # Cleanup files from previous runs
    # files.remove("*.pem")
    # files.remove("*.r0")
    files.remove("index.txt*")
    files.remove("crlnumber")
    # files.remove("certs", force=True)
    files.remove(ca_key)
    files.remove(ca_file)

    # Cleanup files
    files.remove("%s.pem" % sn)
    files.remove(host_request)
    files.remove("serial*")

    files.restore(openssl_config, "CA")
    files.restore(cert_ext_config, "CA")

def certificate_info(path):
    """Extracts and returns the subject and issuer from an X.509 certificate."""
    command = ('openssl', 'x509', '-noout', '-subject', '-issuer', '-in', path)
    status, stdout, stderr = core.system(command)
    if (status != 0) or (stdout is None) or (stderr is not None):
        raise OSError(status, stderr)
    if len(stdout.strip()) == 0:
        raise OSError(status, stdout)
    subject_issuer_re = r'subject\s*=\s*([^\n]+)\nissuer\s*=\s*([^\n]+)\n'
    matches = re.match(subject_issuer_re, stdout)
    if matches is None:
        raise OSError(status, stdout)
    return (matches.group(1), matches.group(2))

def install_cert(self, target_key, source_key, owner_name, permissions):
    """
    Carefully install a certificate with the given key from the given
    source path, then set ownership and permissions as given.  Record
    each directory and file created by this process into the config
    dictionary; do so immediately after creation, so that the
    remove_cert() function knows exactly what to remove/restore.
    """
    target_path = core.config[target_key]
    target_dir = os.path.dirname(target_path)
    source_path = core.config[source_key]
    user = pwd.getpwnam(owner_name)

    # Using os.path.lexists because os.path.exists return False for broken symlinks
    if os.path.lexists(target_path):
        backup_path = target_path + '.osgtest.backup'
        shutil.move(target_path, backup_path)
        core.state[target_key + '-backup'] = backup_path

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        core.state[target_key + '-dir'] = target_dir
        os.chown(target_dir, user.pw_uid, user.pw_gid)
        os.chmod(target_dir, 0755)

    shutil.copy(source_path, target_path)
    core.state[target_key] = target_path
    os.chown(target_path, user.pw_uid, user.pw_gid)
    os.chmod(target_path, permissions)
