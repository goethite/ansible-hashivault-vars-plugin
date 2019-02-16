# Ansible Vars Plugin for Hashicorp Vault Credential Precendence Resolution


test dump playbook using a vars plugin:
```bash
$ VAULT_TOKEN=root \
  VAULT_ADDR=http://192.168.0.69:8300 \
  ANSIBLE_SSH_ARGS="" \
  ANSIBLE_VARS_PLUGINS=./vars_plugins \
  ansible-playbook -i hosts dump.yml
```
