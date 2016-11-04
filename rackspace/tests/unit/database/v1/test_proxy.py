# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.tests.unit import test_proxy_base
from rackspace.database.v1 import _proxy
from rackspace.database.v1 import backup
from rackspace.database.v1 import backup_schedule
from rackspace.database.v1 import high_availability_instance


class TestDatabaseProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestDatabaseProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def _ha_method(self, method):
        return ("rackspace.database.v1.high_availability_instance."
                "HighAvailabilityInstance.{}").format(method)

    def test_backups(self):
        self.verify_list(self.proxy.backups, backup.Backup, paginated=False)

    def test_backup_create(self):
        self.verify_create(self.proxy.create_backup, backup.Backup)

    def test_backup_delete(self):
        self.verify_delete(self.proxy.delete_backup, backup.Backup, False)

    def test_backup_delete_ignore(self):
        self.verify_delete(self.proxy.delete_backup, backup.Backup, True)

    def test_backup_find(self):
        self.verify_find(self.proxy.find_backup, backup.Backup)

    def test_backup_get(self):
        self.verify_get(self.proxy.get_backup, backup.Backup)

    def test_backup_schedules(self):
        self.verify_list(self.proxy.backup_schedules,
                         backup_schedule.BackupSchedule, paginated=False)

    def test_backup_schedule_create(self):
        self.verify_create(self.proxy.create_backup_schedule,
                           backup_schedule.BackupSchedule)

    def test_backup_schedule_delete(self):
        self.verify_delete(self.proxy.delete_backup_schedule,
                           backup_schedule.BackupSchedule, False)

    def test_backup_schedule_delete_ignore(self):
        self.verify_delete(self.proxy.delete_backup_schedule,
                           backup_schedule.BackupSchedule, True)

    def test_backup_schedule_find(self):
        self.verify_find(self.proxy.find_backup_schedule,
                         backup_schedule.BackupSchedule)

    def test_backup_schedule_get(self):
        self.verify_get(self.proxy.get_backup_schedule,
                        backup_schedule.BackupSchedule)

    def test_backup_schedule_update(self):
        self.verify_update(self.proxy.update_backup_schedule,
                           backup_schedule.BackupSchedule)

    def test_ha_instances(self):
        self.verify_list(self.proxy.ha_instances,
                         high_availability_instance.HighAvailabilityInstance,
                         paginated=False)

    def test_ha_instance_create(self):
        self.verify_create(self.proxy.create_ha_instance,
                           high_availability_instance.HighAvailabilityInstance)

    def test_ha_instance_delete(self):
        self.verify_delete(self.proxy.delete_ha_instance,
                           high_availability_instance.HighAvailabilityInstance,
                           False)

    def test_ha_instance_delete_ignore(self):
        self.verify_delete(self.proxy.delete_ha_instance,
                           high_availability_instance.HighAvailabilityInstance,
                           True)

    def test_ha_instance_find(self):
        self.verify_find(self.proxy.find_ha_instance,
                         high_availability_instance.HighAvailabilityInstance)

    def test_ha_instance_get(self):
        self.verify_get(self.proxy.get_ha_instance,
                        high_availability_instance.HighAvailabilityInstance)

    def test_ha_instance_update(self):
        self.verify_update(self.proxy.update_ha_instance,
                           high_availability_instance.HighAvailabilityInstance)

    def test_ha_instance_resize(self):
        self._verify2(self._ha_method("resize"), self.proxy.resize_ha_instance,
                      method_args=['value', 'flavor_reference'],
                      method_result=None,
                      expected_args=[self.session, 'flavor_reference'],
                      expected_result=None)

    def test_ha_instance_resize_volume(self):
        self._verify2(self._ha_method("resize_volume"),
                      self.proxy.resize_ha_instance_volume,
                      method_args=['value', 'volume_size'],
                      method_result=None,
                      expected_args=[self.session, 'volume_size'],
                      expected_result=None)

    def test_ha_instance_restart(self):
        self._verify2(self._ha_method("restart"),
                      self.proxy.restart_ha_instance,
                      method_args=['value'],
                      method_result=None,
                      expected_args=[self.session],
                      expected_result=None)

    def test_ha_instance_attach_configuration(self):
        self._verify2(self._ha_method("add_configuration"),
                      self.proxy.add_configuration_to_ha_instance,
                      method_args=['value', 'configuration_id'],
                      method_result=None,
                      expected_args=[self.session, 'configuration_id'],
                      expected_result=None)

    def test_ha_instance_detach_configuration(self):
        self._verify2(self._ha_method("remove_configuration"),
                      self.proxy.remove_configuration_from_ha_instance,
                      method_args=['value'],
                      method_result=None,
                      expected_args=[self.session],
                      expected_result=None)
