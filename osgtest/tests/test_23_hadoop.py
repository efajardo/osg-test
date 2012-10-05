import os
import pwd
import shutil
import osgtest.library.core as core
import osgtest.library.files as files
import unittest
import socket

class TestStartHadoop(unittest.TestCase):

    def write_dict(self,dict,filename):
        str="<?xml version=\"1.0\"?>\n"
        str=str+"<?xml-stylesheet type=\"text/xsl\""
        str=str+" href=\"configuration.xsl\"?>\n"
        str=str+"<configuration>\n"
        for prop in dict:
            str=str+"<property><name>%s</name>" % prop
            str=str+"<value>%s</value></property>\n" % dict[prop]
        str=str+"</configuration>\n"
        files.write(filename, str, owner="hdfs")

    def write_site_config(self,filename):
        hostname = socket.getfqdn()
        site_dict={"dfs.block.size":"134217728",
            "dfs.replication":"1",
            "dfs.replication.max":"1",
            "dfs.replication.min":"1",
            "dfs.datanode.du.reserved":"1000000",
            "dfs.balance.bandwidthPerSec":"200000",
            "dfs.data.dir":core.config['hdfs.data'],
            "dfs.datanode.handler.count":"20",
            "dfs.hosts.exclude":"/etc/hosts_exclude",
            "dfs.namenode.handler.count":"40",
            "dfs.namenode.logging.level":"all",
            "dfs.checkpoint.dir":core.config['hdfs.checkpoint'],
            "dfs.http.address":"%s:50070"%hostname,
            "dfs.checkpoint.period":"86400",
            "dfs.permissions.supergroup":"root"}

        self.write_dict(site_dict,filename)

    def write_core_config(self,filename):
        hostname = socket.getfqdn()
        core_dict={"fs.default.name":"hdfs://%s:9000"%hostname,
            "hadoop.tmp.dir":core.config['hdfs.scratch'],
            "dfs.umaskmode":"002",
            "io.bytes.per.checksum":"hadoop.log.dir",
            "hadoop.log.dir":"/var/log/hadoop-hdfs"}

        # NEED NAMENODE NAME
        self.write_dict(core_dict,filename)

    def test_01_start_hadoop(self):
        core.state['hadoop.started-server'] = False
        if core.missing_rpm('osg-se-hadoop-namenode','osg-se-hadoop-datanode','hadoop-hdfs'):
            core.skip('hadoop hdfs not installed')
            return
        user=pwd.getpwnam("hdfs")
        core.config['hdfs.directory']='/tmp/hdfs'
        core.config['hdfs.scratch']='/tmp/hdfs/scratch'
        core.config['hdfs.data']='/tmp/hdfs/data'
        core.config['hdfs.checkpoint']='/tmp/hdfs/checkpoint'

        for key in ('hdfs.directory','hdfs.scratch',
          'hdfs.data','hdfs.checkpoint'):
            if not os.path.exists(core.config[key]):
                os.mkdir(core.config[key])
            os.chown(core.config[key], user.pw_uid, user.pw_gid)

        if os.path.exists(os.path.join(core.config['hdfs.scratch'],"dfs")):
            command = ('rm', '-Rf',os.path.join(core.config['hdfs.scratch'],"dfs"))
            stdout, stderr, fail = core.check_system(command, 'Clean Hadoop', shell=True,stdin="Y\r\n")

        self.write_site_config("/etc/hadoop/conf/hdfs-site.xml")                
        self.write_core_config("/etc/hadoop/conf/core-site.xml")                
        
        command = ('hadoop', 'namenode','-format')
        stdout, stderr, fail = core.check_system(command, 'Format Hadoop', shell=True)
        command = ('chown', '-R','hdfs:hdfs',core.config['hdfs.directory'])
        stdout, stderr, fail = core.check_system(command, 'Format Hadoop', shell=True)
            
        command = ('service', 'hadoop-hdfs-namenode', 'start')
        stdout, stderr, fail = core.check_system(command, 'Start Hadoop namenode')
        self.assert_(stdout.find('FAILED') == -1, fail)
        #self.assert_(os.path.exists(core.config['xrootd.pid-file']),
        #             'xrootd server PID file missing')
        command = ('service', 'hadoop-hdfs-datanode', 'start')
        stdout, stderr, fail = core.check_system(command, 'Start Hadoop namenode')
        self.assert_(stdout.find('FAILED') == -1, fail)
        core.state['hadoop.started-server'] = True

