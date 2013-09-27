"""Utilities for creating CAs, certificates and CRLs"""

import os
import re

import osgtest.library.core as core
import osgtest.library.files as files

config = '/etc/pki/tls/openssl.cnf'
cert_ext_config = 'openssl-cert-extensions.conf' 
ca_file = "OSG-Test-CA.pem"
ca_key = "OSG_TEST-CA.key"
crl_file = "OSG-Test-CA.r0"
host_request = "host_req"
dn = "\"/DC=org/DC=Open Science Grid/O=OSG Test/CN=OSG Test CA\""
days = 1
sn = "A1B2C3D4E5F6"

def configure_openssl():
    """Lays down files and configuration for creating CAs, certs and CRLs"""
    working_dir = os.getcwd()
    # Instead of patching openssl's config file
    files.replace(config, "# crl_extensions	= crl_ext", "crl_extensions	= crl_ext", owner="CA")
    files.replace(config, "basicConstraints = CA:true", "basicConstraints = critical, CA:true", backup=False)
    files.replace(config,
                  "# keyUsage = cRLSign, keyCertSign",
                  "keyUsage = critical, digitalSignature, cRLSign, keyCertSign",
                  backup=False)
    files.replace(config,
                  "dir		= ../../CA		# Where everything is kept",
                  "dir		= %s		# Where everything is kept" % working_dir,
                  backup=False)
    
    # Put down necessary files
    files.write("index.txt", "", backup=False)
    files.write("serial", sn, backup=False)
    files.write("crlnumber", "01", backup=False)

def create_ca():
    """Create a CA similar to DigiCert's """
    configure_openssl()
    
    os.system("openssl genrsa -out %s 2048" % ca_key)
    os.system("openssl req -new -x509 -out %s -key %s -subj %s -config %s -days %s" %
              (ca_file, ca_key, dn, config, days))

def create_host_cert():
    """Create a cert similar to DigiCert's"""
    host_pk_der = "hostkey.der"
    host_pk = "hostkey.pem"
    host_cert = "hostcert.pem"
    
    os.system("openssl req -new -nodes -out %s -keyout %s -subj %s" %
              (host_request, host_pk_der, dn))
    # Have to run the private key through RSA to get proper format (-keyform doesn't work in openssl > 0.9.8)
    os.system("openssl rsa -in %s -outform PEM -out %s" % (host_pk_der, host_pk)) 
    files.remove(host_pk_der)
    os.chmod(host_pk, 0400)

    hostname = core.get_hostname()
    files.replace(cert_ext_config,
                  'subjectAltName=DNS:##HOSTNAME##',
                  'subjectAltName=DNS:%s' % hostname,
                  owner="CA")

    os.system("openssl ca -config %s -cert %s -keyfile %s -days %s -policy policy_anything -preserveDN -extfile %s -in "
              "%s -notext -out %s -outdir . -batch" %
              (config, ca_file, ca_key, days, cert_ext_config, host_request, host_cert))
 
def create_crl():
    """Create CRL to accompany our CA"""
    os.system("openssl ca -gencrl -config %s -cert %s -keyfile %s -crldays %s -out %s" %
              (config, ca_file, ca_key, days, crl_file))

def cleanup_files():
    """Cleanup openssl files and config we laid down"""
    # Cleanup files from previous runs
    files.remove("*.pem")
    files.remove("*.r0")
    files.remove("index.txt*")
    files.remove("crlnumber")
    files.remove("certs", force=True)
    files.remove(ca_key)
    files.remove(ca_file)

    # Cleanup files
    files.remove("%s.pem" % sn)
    files.remove(host_request)
    files.remove("serial*")

    files.restore(config, "CA")
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
