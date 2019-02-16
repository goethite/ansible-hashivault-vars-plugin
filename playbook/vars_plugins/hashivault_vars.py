from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import urllib3
import base64
from pretty_json import format_json
import os
import socket
import hvac
from ansible.inventory.group import Group
from ansible.inventory.host import Host
from ansible.plugins.vars import BaseVarsPlugin
from ansible.utils.vars import combine_vars
from ansible.errors import AnsibleInternalError

DOCUMENTATION = '''
    vars: hashivault_vars
    version_added: "2.7"
    short_description: Lookup secrets/creds in Hashicorp Vault in group/domain/host precedence order
'''

urllib3.disable_warnings()  # suppress InsecureRequestWarning


class VarsModule(BaseVarsPlugin):
    """
    Hashicorp Vault Vars Plugin.

    Root path in vault:
        /secret/ansible/

    Precendence (applied top to bottom, so last takes precendence):
        Groups:
            /secret/ansible/groups/all
            /secret/ansible/groups/ungrouped
            /secret/ansible/groups/your_inv_item_group
            ...

        Hosts/Domains:
            /secret/ansible/domains/com
            /secret/ansible/domains/example.com
            /secret/ansible/hosts/hosta.example.com

    All values retrieved from these paths are mapped as ansible variables,
    e.g. ansible_user, ansible_password, etc.

    The layered lookups are merged, with the last taking precendence over
    earlier lookups.

    Lookups are cached for the run.
    """

    def __init__(self):
        super(BaseVarsPlugin, self).__init__()

        self.v_client = hvac.Client(
            url=os.environ['VAULT_ADDR'],
            token=os.environ['VAULT_TOKEN'],
            # verify=os.environ['VAULT_SKIP_VERIFY'] != '1'
            )
        assert self.v_client.is_authenticated()

    # See https://stackoverflow.com/questions/319279/how-to-validate-ip-address-in-python
    def _is_valid_ipv4_address(self, address):
        try:
            socket.inet_pton(socket.AF_INET, address)
        except AttributeError:  # no inet_pton here, sorry
            try:
                socket.inet_aton(address)
            except socket.error:
                return False
            return address.count('.') == 3
        except socket.error:  # not a valid address
            return False
        return True

    def _is_valid_ipv6_address(self, address):
        try:
            socket.inet_pton(socket.AF_INET6, address)
        except socket.error:  # not a valid address
            return False
        return True

    def _is_valid_ip_address(self, address):
        if self._is_valid_ipv4_address(address):
            return True
        return self._is_valid_ipv6_address(address)

    def _read_vault(self, folder, entity):
        result = self.v_client.read(
            path='secret/ansible/%s/%s' % (folder, entity)
        )
        # print("result:", format_json(result))
        if not result:
            return {}
        return result["data"]

    def _get_vars(self, data, entity, cache):
        folder = ""
        if isinstance(entity, Group):
            folder = "groups"
        elif isinstance(entity, Host):
            if self._is_valid_ip_address(str(entity)):
                folder = "hosts"
            else:
                parts = str(entity).split('.')
                # print("parts: %s", parts)
                if len(parts) == 1:
                    folder = "hosts"
                elif len(parts) > 1:
                    folder = "domains"
                    parts.reverse()
                    prev_part = ""
                    for part in parts:
                        lookup_part = part + prev_part
                        if lookup_part == str(entity):
                            folder = "hosts"
                        # print("lookup part: %s in %s/" % (lookup_part, folder))
                        data = combine_vars(
                            data, self._read_vault(folder, lookup_part))
                        prev_part = '.' + part + prev_part
                    return data
                else:
                    raise AnsibleInternalError(
                        "Failed to extract host name parts, len: %d", len(parts))

        else:
            raise AnsibleInternalError(
                "Unrecognised entity type encountered in hashivault_vars plugin: %s", type(entity))

        # print("folder: %s" % (folder))
        return combine_vars(data, self._read_vault(folder, entity))

    def get_vars(self, loader, path, entities, cache=True):
        if not isinstance(entities, list):
            entities = [entities]
        # print("entities: %s" % (entities))
        # print("entities: %s" % (dir(entities[0])))
        # print("entities: %s" % (type(entities[0])))

        super(VarsModule, self).get_vars(loader, path, entities)

        data = {}

        for entity in entities:
            data = self._get_vars(data, entity, cache)

        # print("returning:", format_json(data))

        return data
