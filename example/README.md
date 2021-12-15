# Examples
NOTE: The limits depend all on your setup and usage of the yaml_folder plugin.  
In this example the inventory structure is "{customer}-{environment}".  
You could also use something like "{product}-{customer}-{environment}" or whatever you like.

## Nextcloud
### Show all hosts
```
[user@rocky-dever example]$ ansible-playbook playbooks/deploy_nextcloud.yml --list-hosts 

playbook: playbooks/deploy_nextcloud.yml

  play #1 (nextcloud_instance): Deploy nextcloud instance       TAGS: []
    pattern: ['nextcloud_instance']
    hosts (2):
      customer_one-prod-nextcloud-nextcloud_instance-nextcloud1
      internal-prod-nextcloud-nextcloud_instance-nextcloud1

  play #2 (nextcloud_apache): Deploy nextcloud apache   TAGS: []
    pattern: ['nextcloud_apache']
    hosts (2):
      internal-prod-nextcloud-nextcloud_apache-apache1
      customer_one-prod-nextcloud-nextcloud_apache-apache1
[user@rocky-dever example]$
```

### Limit to only one environment
```
[user@rocky-dever example]$ ansible-playbook playbooks/deploy_nextcloud.yml --list-hosts --limit 'internal-prod-*'

playbook: playbooks/deploy_nextcloud.yml

  play #1 (nextcloud_instance): Deploy nextcloud instance       TAGS: []
    pattern: ['nextcloud_instance']
    hosts (1):
      internal-prod-nextcloud-nextcloud_instance-nextcloud1

  play #2 (nextcloud_apache): Deploy nextcloud apache   TAGS: []
    pattern: ['nextcloud_apache']
    hosts (1):
      internal-prod-nextcloud-nextcloud_apache-apache1
```

