Kentik_gcp_integration
=========

A role for automating integration of GCP with Kentik.
This role:
- enables log flow for passed subnets (assumes subnets exist)
- creates topic for this logs
- creates sink for them
- creates subscription
- add permission for kentik to use said subscription

Requirements
------------

- python >= 2.6
- gcloud -> tested using Google Cloud SDK 312.0.0
- service account in order to access GCP

All dependencies are installed as first step of the role.
That includes:
- requests >= 2.18.4
- google-auth >= 1.3.0

Role Variables
--------------

```YAML
kentik_gcp_integration_subscription_name: kentik-export-subscription
kentik_gcp_integration_topic: kentik-export-topic
kentik_gcp_integration_sink_name: kentik-export-sink 

# Required to be defined
kentik_gcp_integration_project: 
kentik_gcp_integration_subnets:
  - name: some name
    region: some region
kentik_gcp_integration_service_account_file: 
```

### Google Cloud Platform Credentials
Role uses gcp_ ansible modules which need to be authorized in order to work.
Following variables are used

```YML
kentik_gcp_integration_project: 
kentik_gcp_integration_service_account_file: 
```

for more information refer to doc [here](https://docs.ansible.com/ansible/latest/scenario_guides/guide_gce.html)

Example Playbook
----------------

```YAML
---
- hosts: 127.0.0.1
  gather_facts: false
  connection: local
  pre_tasks:
# Adds kentik to subnet-1
# Assuming subnet-1 exists
  - name: get current gcloud project
    shell: gcloud config get-value project
    register: output
    changed_when: false

  roles:
    - role: roles/kentik_gcp_integration
      vars:
        kentik_gcp_integration_project: "{{ output.stdout }}"
        # file with keys for gcp
        kentik_gcp_integration_service_account_file: "{{ lookup('env', 'GCP_SERVICE_ACCOUNT_FILE') }}"
        kentik_gcp_integration_subnets:
        - name: subnet-1
          region: us-east1
        - name: subnet-2
          region: us-east4
```

License
-------

MIT