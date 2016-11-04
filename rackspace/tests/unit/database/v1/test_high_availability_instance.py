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

import mock
import testtools

from rackspace.database.v1 import high_availability_instance

CIDR = '5.6.7.8/9'
REPLICA_NAME = 'Roy Batty'
UUID = 'xxxxxxxx-xxxx-Mxxx-Nxxx-xxxxxxxxxxxx'
CONFIG_UUID = 'yyyyyyyy-yyyy-Myyy-Nyyy-yyyyyyyyyyyy'
FLAVOR_REFERENCE = '2'
VOLUME_SIZE = 1

EXAMPLE = {
    "acls": [
        {"address": "10.0.0.0/0"},
        {"address": "1.2.3.4/5"}
    ],
    "datastore": {
        "version": "5.6",
        "type": "MYSQL"
    },
    "id": UUID,
    "name": "Deckard",
    "networks": ["servicenet", "public"],
    "replicas": [{
            "volume": {"size": VOLUME_SIZE},
            "flavorRef": FLAVOR_REFERENCE,
            "name": REPLICA_NAME}
    ],
    "replica_source": [{
        "volume": {
            "size": VOLUME_SIZE},
        "flavorRef": FLAVOR_REFERENCE,
        "name": "Tyrell"}
    ],
    "configuration_id": CONFIG_UUID,
    "scheduled_backup": {
        "enabled": True
    }
}


class TestHA(testtools.TestCase):
    def test_basic(self):
        sot = high_availability_instance.HighAvailabilityInstance()
        self.assertEqual('ha', sot.base_path)
        self.assertEqual('ha_instance', sot.resource_key)
        self.assertEqual('ha_instances', sot.resources_key)
        self.assertEqual("cloudDatabases", sot.service.service_name)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = high_availability_instance.HighAvailabilityInstance(EXAMPLE)
        self.assertEqual(EXAMPLE['acls'], sot.acls)
        self.assertEqual(EXAMPLE['datastore'], sot.datastore)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['networks'], sot.networks)
        self.assertEqual(EXAMPLE['replicas'], sot.replicas)
        self.assertEqual(EXAMPLE['replica_source'], sot.replica_source)
        self.assertEqual(EXAMPLE['configuration_id'], sot.configuration_id)
        self.assertEqual(EXAMPLE['scheduled_backup'], sot.scheduled_backup)

    def test_create_json_is_overridden(self):
        resp = mock.Mock()
        resp.json = mock.Mock(return_value={'ha_instance': {}})
        resp.headers = {'location': 'foo'}

        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)

        sot = high_availability_instance.HighAvailabilityInstance()
        sot.name = 'foo'
        sot.create(sess)

        body = {"ha": {"name": "foo"}}
        sess.post.assert_called_with("ha", endpoint_filter=sot.service,
                                     json=body)

    def test_add_acl(self):
        response = mock.Mock()
        response.body = ''
        sess = mock.Mock()
        sess.post = mock.Mock()
        sess.post.return_value = response
        sot = high_availability_instance.HighAvailabilityInstance(EXAMPLE)

        self.assertEqual(None, sot.add_acl(sess, CIDR))

        body = {"address": CIDR}
        url = ("ha/%s/acls" % sot.id)
        sess.post.assert_called_with(url, service=sot.service, json=body)

    def test_delete_acl(self):
        response = mock.Mock()
        response.body = ''
        sess = mock.Mock()
        sess.delete = mock.Mock()
        sess.delete.return_value = response
        sot = high_availability_instance.HighAvailabilityInstance(EXAMPLE)

        self.assertEqual(None, sot.delete_acl(sess, CIDR))

        url = ("ha/%s/acls/%s" % (sot.id, CIDR))
        sess.delete.assert_called_with(url, service=sot.service)

    def test_get_acls(self):
        response = mock.Mock()
        response.body = {"acls": [{"address": "10.0.0.0/0"},
                                  {"address": "1.2.3.4/5"}]}
        sess = mock.Mock()
        sess.get = mock.Mock()
        sess.get.return_value = response
        sot = high_availability_instance.HighAvailabilityInstance(EXAMPLE)

        self.assertEqual(response.body['acls'], sot.get_acls(sess))

        url = ("ha/%s/acls" % sot.id)
        sess.get.assert_called_with(url, service=sot.service)

    def test_add_replica(self):
        response = mock.Mock()
        response.body = ''
        sess = mock.Mock()
        sess.post = mock.Mock()
        sess.post.return_value = response
        sot = high_availability_instance.HighAvailabilityInstance(EXAMPLE)

        self.assertEqual(None, sot.add_replica(
            sess, REPLICA_NAME, FLAVOR_REFERENCE, VOLUME_SIZE))

        body = {"add_replica": {"replica_details":
                {"volume": {"size": VOLUME_SIZE},
                 "flavorRef": FLAVOR_REFERENCE,
                 "name": REPLICA_NAME}}}
        url = ("ha/%s/action" % sot.id)
        sess.post.assert_called_with(url, service=sot.service, json=body)

    def test_remove_replica(self):
        response = mock.Mock()
        response.body = ''
        sess = mock.Mock()
        sess.post = mock.Mock()
        sess.post.return_value = response
        sot = high_availability_instance.HighAvailabilityInstance(EXAMPLE)

        self.assertEqual(None, sot.remove_replica(sess, UUID))

        body = {"remove_replica": UUID}
        url = ("ha/%s/action" % sot.id)
        sess.post.assert_called_with(url, service=sot.service, json=body)

    def test_resize(self):
        response = mock.Mock()
        response.body = ''
        sess = mock.Mock()
        sess.post = mock.Mock()
        sess.post.return_value = response
        sot = high_availability_instance.HighAvailabilityInstance(EXAMPLE)

        self.assertEqual(None, sot.resize(sess, FLAVOR_REFERENCE))

        body = {'resize': {'flavorRef': FLAVOR_REFERENCE}}
        url = ("ha/%s/action" % sot.id)
        sess.post.assert_called_with(url, service=sot.service, json=body)

    def test_resize_volume(self):
        response = mock.Mock()
        response.body = ''
        sess = mock.Mock()
        sess.post = mock.Mock()
        sess.post.return_value = response
        sot = high_availability_instance.HighAvailabilityInstance(EXAMPLE)

        self.assertEqual(None, sot.resize_volume(sess, VOLUME_SIZE))

        body = {'resize': {'volume': VOLUME_SIZE}}
        url = ("ha/%s/action" % sot.id)
        sess.post.assert_called_with(url, service=sot.service, json=body)

    def test_action_restart(self):
        response = mock.Mock()
        response.json = mock.Mock(return_value='')

        sess = mock.Mock()
        sess.post = mock.Mock(return_value=response)

        sot = high_availability_instance.HighAvailabilityInstance(EXAMPLE)

        self.assertIsNone(sot.restart(sess))

        url = ("ha/%s/action" % sot.id)
        body = {'restart': {}}
        sess.post.assert_called_with(url, endpoint_filter=sot.service,
                                     json=body)

    def test_add_configuration(self):
        response = mock.Mock()
        response.json = mock.Mock(return_value='')

        sess = mock.Mock()
        sess.post = mock.Mock(return_value=response)

        sot = high_availability_instance.HighAvailabilityInstance(EXAMPLE)
        self.assertIsNone(sot.add_configuration(sess, 'config_id'))

        url = ("ha/%s" % sot.id)
        body = {'ha_instance': {'configuration_id': 'config_id'}}
        sess.patch.assert_called_with(url, endpoint_filter=sot.service,
                                      json=body)

    def test_remove_configuration(self):
        response = mock.Mock()
        response.json = mock.Mock(return_value='')

        sess = mock.Mock()
        sess.post = mock.Mock(return_value=response)

        sot = high_availability_instance.HighAvailabilityInstance(EXAMPLE)
        self.assertIsNone(sot.remove_configuration(sess))

        url = ("ha/%s" % sot.id)
        body = {'ha_instance': {'configuration_id': ''}}
        sess.patch.assert_called_with(url, endpoint_filter=sot.service,
                                      json=body)
