# Ansible Vars Plugin for Hashicorp Vault Credential Precendence Resolution

**Project migrated to [hashivault_vars](https://github.com/goethite/hashivault_vars).**

This is a proof-of-concept for the [gostint](https://goethite.github.io/gostint/)
project.

An Ansible Vars Plugin for Hashicorp Vault to lookup credentials/secrets,
injecting these into the playbook run (e.g. `ansible_user`, `ansible_password`,
etc).

Root path in vault:

* `/secret/ansible/`

Precendence (applied top to bottom, so last takes precendence):
* Groups:
  * `/secret/ansible/groups/all`
  * `/secret/ansible/groups/ungrouped`
  * `/secret/ansible/groups/your_inv_item_group`
  * ...

* Hosts/Domains:
  * `/secret/ansible/{connection}/domains/com`
  * `/secret/ansible/{connection}/domains/example.com`
  * `/secret/ansible/{connection}/hosts/hosta.example.com`

where `{connection}` is `ansible_connection`, e.g.: "ssh", "winrm", ...
(this plugin attempts to make assumptions where `ansible_connection` is not
set)

All values retrieved from these paths are mapped as ansible variables,
e.g. `ansible_user`, `ansible_password`, etc.

The layered lookups are merged, with the last taking precendence over
earlier lookups.

Lookups to the vault are cached for the run.

### A test dump playbook using a vars plugin:
```bash
$ VAULT_TOKEN=root \
  VAULT_ADDR=http://192.168.0.69:8300 \
  ANSIBLE_SSH_ARGS="" \
  ANSIBLE_VARS_PLUGINS=./vars_plugins \
  ansible-playbook -i hosts dump.yml
```
