import osgtest.library.core as core
import osgtest.library.files as files
import osgtest.library.service as service
import osgtest.library.osgunittest as osgunittest

class TestStopCondorCE(osgunittest.OSGTestCase):
    def test_01_stop_condorce(self):
        core.skip_ok_unless_installed('condor', 'htcondor-ce', 'htcondor-ce-client', 'htcondor-ce-condor')
        self.skip_ok_unless(core.state['condor-ce.started-service'], 'did not start server')
        service.check_stop('condor-ce')

    def test_02_restore_config(self):
        core.skip_ok_unless_installed('condor', 'htcondor-ce', 'htcondor-ce-client', 'htcondor-ce-condor')

        if core.rpm_is_installed('gums-service') and core.state['condor-ce.gums-auth']:
            files.restore(core.config['condor-ce.lcmapsdb'], 'condor-ce.gums')
            files.restore(core.config['condor-ce.gsi-authz'], 'condor-ce')
            files.restore(core.config['condor-ce.gums-properties'], 'condor-ce')
        files.restore(core.config['condor-ce.condor-cfg'], 'condor-ce')
        files.restore(core.config['condor-ce.condor-ce-cfg'], 'condor-ce')
        files.restore(core.config['condor-ce.lcmapsdb'], 'condor-ce')
        if core.options.hostcert:
            files.restore(core.config['condor-ce.condorce_mapfile'], 'condor-ce')
