# Vulnerable Network for Cyber Defense Competition practice 
Terraform and Ansible to deploy an all-linux vulnerable network to practice for NCAE CyberGames

## Requirements

- `jq`
- `terraform`
- aws credentials (most likely in `~/.aws`)

## Architecture

This project uses:
- Terraform to deploy the infrastructure
- Ansible roles to configure the systems:
  - `common`: System misconfigurations and vulnerabilities
  - `users`: Interesting user accounts
  - `kali`: Offensive security tools
  - `web`: Web server configuration

## Steps

1. Deploy the network

```
cd terraform
terraform apply -var="team_number=1" -auto-approve
```

2. Copy files onto the jumpbox

```bash
scp -r -i jumpbox-1-key.pem ../playbook.yml ../roles ../inventory.ini ../ansible.cfg *.pem admin@$(terraform output jumpbox_ip | jq -r):/home/admin
```

3. SSH into jumbox and configure files

```bash
ssh -i jumpbox-1-key.pem admin@$(terraform output jumpbox_ip | jq -r)
sudo su
cd ~
mv /home/admin/*
chmod +x *.pem
```

4. Configure inventory

Make sure `invenntory.ini` is using the correct subnets

5. Run playbook

```
ansible-playbook playbook.yml
```

## Role Customization

The roles are designed to be modular and configurable:

- Edit role defaults in `roles/*/defaults/main.yml` to change variables
- Add or remove tasks in `roles/*/tasks/` 
- Modify templates in `roles/*/templates/`
