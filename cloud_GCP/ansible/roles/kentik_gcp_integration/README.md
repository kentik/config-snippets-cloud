Kentik_gcp_integration
=========

A brief description of the role goes here.

Requirements
------------

All dependencies are installed as first step of role

- python >= 2.6
- requests >= 2.18.4
- google-auth >= 1.3.0

Role Variables
--------------

### Google Cloud Platform Credentials
Role uses gcp_ ansible modules which need to be authorized in order to work.
Following variables are used

```YAML
auth_kind:
service_account_email:
service_account_file:
project:
scopes:
```

Modules themselves can also use environmental variables

```sh
GCP_AUTH_KIND
GCP_SERVICE_ACCOUNT_EMAIL
GCP_SERVICE_ACCOUNT_FILE
GCP_SCOPES
```

for more information refer to doc ![here](https://docs.ansible.com/ansible/2.9/scenario_guides/guide_gce.html)

Example Playbook
----------------

```YAML
state: [WIP]
```

License
-------

MIT

Author Information
------------------

CodiLime Ltd. 

https://codilime.com/