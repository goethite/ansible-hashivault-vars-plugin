# Ansible Vars Plugin for Hashicorp Vault Credential Precendence Resolution

This is a proof-of-concept for the [gostint](https://goethite.github.io/gostint/)
project.

An Ansible Vars Plugin for Hashicorp Vault to lookup credentials/secrets,
injecting these into the playbook run (e.g. `ansible_user`, `ansible_password`,
etc).

Root path in vault:

* /secret/ansible/

Precendence (applied top to bottom, so last takes precendence):
* Groups:
  * /secret/ansible/groups/all
  * /secret/ansible/groups/ungrouped
  * /secret/ansible/groups/your_inv_item_group
        ...

* Hosts/Domains:
  * /secret/ansible/domains/com
  * /secret/ansible/domains/example.com
  * /secret/ansible/hosts/hosta.example.com

All values retrieved from these paths are mapped as ansible variables,
e.g. `ansible_user`, `ansible_password`, etc.

The layered lookups are merged, with the last taking precendence over
earlier lookups.

Lookups are not yet cached for the run (TODO).

### A test dump playbook using a vars plugin:
```bash
$ VAULT_TOKEN=root \
  VAULT_ADDR=http://192.168.0.69:8300 \
  ANSIBLE_SSH_ARGS="" \
  ANSIBLE_VARS_PLUGINS=./vars_plugins \
  ansible-playbook -i hosts dump.yml
```
