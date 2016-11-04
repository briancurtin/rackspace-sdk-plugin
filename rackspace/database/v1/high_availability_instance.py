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

from openstack.database.v1 import flavor
from openstack import resource
from openstack import utils
from rackspace.database import database_service


class HighAvailabilityInstance(resource.Resource):
    base_path = 'ha'
    resource_key = 'ha_instance'
    resources_key = 'ha_instances'
    service = database_service.DatabaseService()

    # capabilities
    allow_create = True
    allow_delete = True
    allow_list = True
    allow_retrieve = True
    allow_update = True

    # Properties
    #: Access control lists. *Type: list*
    acls = resource.prop('acls', type=list)
    #: Datastore type and version. *Type: dict*
    datastore = resource.prop('datastore', type=dict)
    #: A dictionary with details on the flavor this server is running.
    #: The dictionary includes a key for the ``id`` of the flavor, as well
    #: as a ``links`` key, which includes a list of relevant links for this
    #: flavor. *Type: flavor.Flavor*
    flavor = resource.prop('flavor', type=flavor.Flavor)
    #: Name of High Availability instance
    name = resource.prop('name')
    #: Networks. *Type: list*
    networks = resource.prop('networks', type=list)
    #: Replica instances. *Type: list*
    replicas = resource.prop('replicas', type=list)
    #: Replica sources. *Type: list*
    replica_source = resource.prop('replica_source', type=list)
    #: The source instance ID for a backup
    source_instance = resource.prop('instance_id')
    #: The state this HA instance is in. Valid values include:
    status = resource.prop('state')
    #: Volumes. *Type: dict*
    volume = resource.prop('volume', type=dict)
    #: The configuration ID for this instance. *Type: string*
    configuration_id = resource.prop('configuration')
    #: The status of scheduled backups. *Type: dict*
    scheduled_backup = resource.prop('scheduled_backup')

    @classmethod
    def _get_create_body(cls, attrs):
        return {'ha': attrs}

    def add_acl(self, session, cidr):
        """Add Access Control List (ACL)

        :param session: The session to use for making this request.
        :param str cidr: Specifies a CIDR notated IPV4 address.
        :type session: :class:`~openstack.session.Session`
        :returns: ``None``
        """
        body = {"address": cidr}
        url = utils.urljoin(self.base_path, self.id, 'acls')
        session.post(url, service=self.service, json=body)

    def delete_acl(self, session, cidr):
        """Delete Access Control List (ACL)

        :param session: The session to use for making this request.
        :param str cidr: Specifies a CIDR notated IPV4 address.
        :type session: :class:`~openstack.session.Session`
        :returns: ``None``
        """
        url = utils.urljoin(self.base_path, self.id, 'acls', cidr)
        session.delete(url, service=self.service)

    def get_acls(self, session):
        """Get Access Control Lists (ACLs)

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :returns: ``dict``
        """
        url = utils.urljoin(self.base_path, self.id, 'acls')
        resp = session.get(url, service=self.service).body
        return resp['acls']

    def get_backups(self, session):
        """Lists backups for the HA instance

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :returns: ``list``
        """
        url = utils.urljoin(self.base_path, self.id, 'backups')
        resp = session.get(url, service=self.service).body
        return resp['backups']

    def add_replica(self, session, name, flavor_reference, volume_size):
        """Add a replica node to the HA group

        For the duration of this action, the HA instance goes into the
        ``ADDING_REPLICA`` state as a result of this action. It switches back
        to ``ACTIVE`` once the operation is complete. Adding a new replica node
        would restart the ``mha`` manager service (which monitors the
        source/replica instances to trigger failover) and the haproxy service
        on the load balancer nodes.

        :param session: The session to use for making this request.
        :param str name: Name of the replica instance.
        :param str flavor_reference: The flavor ID.
        :param str volume_size: The volume size.
        :type session: :class:`~openstack.session.Session`
        :returns: ``None``
        """
        body = {"add_replica": {"replica_details":
                {"volume": {"size": volume_size},
                 "flavorRef": flavor_reference,
                 "name": name}}}
        url = utils.urljoin(self.base_path, self.id, 'action')
        session.post(url, service=self.service, json=body)

    def remove_replica(self, session, replica_id):
        """Remove/detach a replica node from the HA group

        Detaching a replica from the HA setup will cause a MySQL service
        restart on the detached instance.

        For the duration of this action, the HA instance goes into the
        ``REMOVING_REPLICA`` state as a result of this action. It switches back
        to ``ACTIVE`` once the operation is complete. The instance that is
        detached also goes into a ``DETACH_REPLICA`` state when it is being
        disabled as a replica and switches back to ``ACTIVE`` once detached.
        Removing a replica node would restart the ``mha`` manager service
        (which monitors the source/replica instances to trigger failover) and
        the haproxy service on the load balancer nodes.

        :param session: The session to use for making this request.
        :param str replica_id: The attached replica ID to detach.
        :type session: :class:`~openstack.session.Session`
        :returns: ``None``
        """
        body = {"remove_replica": replica_id}
        url = utils.urljoin(self.base_path, self.id, 'action')
        session.post(url, service=self.service, json=body)

    def resize(self, session, flavor_reference):
        """Resize the HA instance

        For the duration of this action, the HA instance goes into a
        ``RESIZING_FLAVOR`` state and switches back to ``ACTIVE`` once the
        action is complete. Resizing the flavor of the HA cluster would restart
        the ``mha`` manager service (which monitors the source/replica
        instances to trigger failover) and the haproxy service on the
        load balancer nodes.

        :param session: The session to use for making this request.
        :param str flavor_reference: The flavor ID.
        :type session: :class:`~openstack.session.Session`
        :returns: ``None``
        """

        body = {'resize': {'flavorRef': flavor_reference}}
        url = utils.urljoin(self.base_path, self.id, 'action')
        session.post(url, service=self.service, json=body)

    def resize_volume(self, session, volume_size):
        """Resize the volume attached to the HA instance

        Only increasing the size is allowed. Resize down is prevented.

        For the duration of this action, the HA instance goes into a
        ``RESIZING_VOLUME`` state and switches back to ``ACTIVE`` once the
        action is complete across the entire HA cluster. Resizing the flavor of
        the HA cluster would restart the ``mha`` manager service (which
        monitors the source/replica instances to trigger failover) and the
        haproxy service on the load balancer nodes.

        :param session: The session to use for making this request.
        :param str volume_size: The volume size.
        :type session: :class:`~openstack.session.Session`
        :returns: ``None``
        """
        body = {'resize': {'volume': volume_size}}
        url = utils.urljoin(self.base_path, self.id, 'action')
        session.post(url, service=self.service, json=body)

    def restart(self, session):
        """Restart the database instance

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :returns: ``None``
        """
        body = {'restart': {}}
        url = utils.urljoin(self.base_path, self.id, 'action')
        session.post(url, endpoint_filter=self.service, json=body)

    def add_configuration(self, session, configuration_id):
        """Adds a specified configuration group to the HA Instance.

        :param session: The session to use for making this request.
        :param str configuration_id: The configuration group ID.
        :type session: :class:`~openstack.session.Session`
        :returns: ``None``
        """
        body = {'ha_instance': {'configuration_id': configuration_id}}
        url = utils.urljoin(self.base_path, self.id)
        session.patch(url, endpoint_filter=self.service, json=body)

    def remove_configuration(self, session):
        """Removes a specified configuration group from the HA Instance.

        :param session: The session to use for making this request.
        :param str configuration_id: The configuration group ID.
        :type session: :class:`~openstack.session.Session`
        :returns: ``None``
        """
        body = {'ha_instance': {'configuration_id': ''}}
        url = utils.urljoin(self.base_path, self.id)
        session.patch(url, endpoint_filter=self.service, json=body)
