import os
import osgtest.library.core as core
import osgtest.library.files as files
import unittest

class TestStopHadoop(unittest.TestCase):

    def test_01_stop_hadoop(self):
        if core.state['hadoop.started-server'] == False:
            core.skip('did not start server')
            return

        command = ('service', 'hadoop-hdfs-datanode', 'stop')
        stdout, _, fail = core.check_system(command, 'Stop Hadoop datanode')
        self.assert_(stdout.find('FAILED') == -1, fail)
        command = ('service', 'hadoop-hdfs-namenode', 'stop')
        stdout, _, fail = core.check_system(command, 'Stop Hadoop namenode')
        self.assert_(stdout.find('FAILED') == -1, fail)

        files.restore('/etc/hadoop/conf/hdfs-site.xml',"hdfs")
        files.restore('/etc/hadoop/conf/core-site.xml',"hdfs")
