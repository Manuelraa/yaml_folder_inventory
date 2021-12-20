# Examples
NOTE: The limits depend all on your setup and usage of the yaml_folder plugin.  
In this example the inventory structure is "{customer}-{environment}".  
You could also use something like "{product}-{customer}-{environment}" or whatever you like.

NOTE: parsed.json is manually created from `ansible-inventory --list` output.

NOTE: .localhost domains get resolved to "::1" aka localhost on my host

## Ansible all
```
[user@rocky-dever example]$ ansible all --list-hosts
  hosts (8):
    internal-prod-nextcloud-apache-web1
    internal-prod-nextcloud-server-server1
    external-prod-nextcloud-apache-web1
    external-prod-nextcloud-server-server1
    internal-simu-haproxy-haproxy-db1
    internal-simu-haproxy-haproxy-db2
    external-prod-haproxy-haproxy-db1
    external-prod-haproxy-haproxy-db2
```

## Nextcloud
### Show all hosts
```
[user@rocky-dever example]$ ansible-playbook playbooks/deploy_nextcloud.yml --list-hosts

playbook: playbooks/deploy_nextcloud.yml

  play #1 (nextcloud:&server): Deploy nextcloud instance        TAGS: []
    pattern: ['nextcloud:&server']
    hosts (2):
      external-prod-nextcloud-server-server1
      internal-prod-nextcloud-server-server1

  play #2 (nextcloud:&apache): Deploy nextcloud apache  TAGS: []
    pattern: ['nextcloud:&apache']
    hosts (2):
      external-prod-nextcloud-apache-web1
      internal-prod-nextcloud-apache-web1
```

### Limit to only one environment
```
[user@rocky-dever example]$ ansible-playbook playbooks/deploy_nextcloud.yml --list-hosts --limit 'internal-prod-*'

playbook: playbooks/deploy_nextcloud.yml

  play #1 (nextcloud:&server): Deploy nextcloud instance        TAGS: []
    pattern: ['nextcloud:&server']
    hosts (1):
      internal-prod-nextcloud-server-server1

  play #2 (nextcloud:&apache): Deploy nextcloud apache  TAGS: []
    pattern: ['nextcloud:&apache']
    hosts (1):
      internal-prod-nextcloud-apache-web1
```

## Haproxy
```
[user@rocky-dever example]$ ansible-playbook playbooks/deploy_haproxy.yml

PLAY [Deploy haproxy servers] ***************************************************************************************************************************************************************

TASK [Print backend_servers] ****************************************************************************************************************************************************************
ok: [internal-simu-haproxy-haproxy-db1] => {
    "backend_servers": [
        "cool-app1.simu.internal.example.localhost",
        "cool-app3.simu.internal.example.localhost",
        "cool-app2.simu.internal.example.localhost",
        "cool-app4.simu.internal.example.localhost"
    ]
}
ok: [internal-simu-haproxy-haproxy-db2] => {
    "backend_servers": [
        "cool-app2.simu.internal.example.localhost",
        "cool-app4.simu.internal.example.localhost",
        "cool-app1.simu.internal.example.localhost",
        "cool-app3.simu.internal.example.localhost"
    ]
}
ok: [external-prod-haproxy-haproxy-db1] => {
    "backend_servers": [
        "cool-app1.prod.external.example.localhost",
        "cool-app3.prod.external.example.localhost",
        "cool-app2.prod.external.example.localhost",
        "cool-app4.prod.external.example.localhost"
    ]
}
ok: [external-prod-haproxy-haproxy-db2] => {
    "backend_servers": [
        "cool-app2.prod.external.example.localhost",
        "cool-app4.prod.external.example.localhost",
        "cool-app1.prod.external.example.localhost",
        "cool-app3.prod.external.example.localhost"
    ]
}

TASK [Print global haproxy group var] *******************************************************************************************************************************************************
ok: [internal-simu-haproxy-haproxy-db1] => {
    "haproxy_global_variable": "VARIABLE IS NOT DEFINED!"
}
ok: [internal-simu-haproxy-haproxy-db2] => {
    "haproxy_global_variable": "VARIABLE IS NOT DEFINED!"
}
ok: [external-prod-haproxy-haproxy-db1] => {
    "haproxy_global_variable": "VARIABLE IS NOT DEFINED!"
}
ok: [external-prod-haproxy-haproxy-db2] => {
    "haproxy_global_variable": "VARIABLE IS NOT DEFINED!"
}

TASK [Print haproxy group var which is defined in each customer folder] *********************************************************************************************************************
ok: [internal-simu-haproxy-haproxy-db1] => {
    "haproxy_customer_variable": "Variable set in inventory/internal/haproxy.yml"
}
ok: [internal-simu-haproxy-haproxy-db2] => {
    "haproxy_customer_variable": "Variable set in inventory/internal/haproxy.yml"
}
ok: [external-prod-haproxy-haproxy-db1] => {
    "haproxy_customer_variable": "Variable set in inventory/external/haproxy.yml"
}
ok: [external-prod-haproxy-haproxy-db2] => {
    "haproxy_customer_variable": "Variable set in inventory/external/haproxy.yml"
}

PLAY RECAP **********************************************************************************************************************************************************************************
external-prod-haproxy-haproxy-db1 : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
external-prod-haproxy-haproxy-db2 : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
internal-simu-haproxy-haproxy-db1 : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
internal-simu-haproxy-haproxy-db2 : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```
