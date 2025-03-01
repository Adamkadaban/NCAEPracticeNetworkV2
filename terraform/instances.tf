# VPN for each team
resource "aws_instance" "jumpbox" {
  ami                         = var.debian_ami
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.public_subnet.id
  key_name                    = "jumpbox-${var.team_number}-key"
  vpc_security_group_ids      = [aws_security_group.jumpbox_sg.id]
  associate_public_ip_address = true

  root_block_device {
    volume_size = 32
    volume_type = "gp3"
  }

  user_data = <<-EOF
              #!/bin/bash
              apt update -y && apt install pipx -y
              pipx install --include-deps ansible-core==2.16
              pipx inject ansible-core argcomplete
              pipx inject ansible-core passlib
              pipx ensurepath
              EOF
}

# Kali for attacker

resource "aws_instance" "kali_attacker" {
  private_ip                  = "192.168.${var.team_number}.10"
  ami                         = var.kali_ami
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.team_subnet.id
  key_name                    = "kali-${var.team_number}-key"
  vpc_security_group_ids      = [aws_security_group.internal_sg.id]
  associate_public_ip_address = false

  root_block_device {
    volume_size = 64
    volume_type = "gp3"
  }
}
# Linux (Debian, Ubuntu, CentOS) for each team

## Debian (Backup) will be for them to back stup up
resource "aws_instance" "debian_backup" {
  private_ip                  = "192.168.${var.team_number}.11"
  ami                         = var.debian_ami
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.team_subnet.id
  key_name                    = "team-${var.team_number}-key"
  vpc_security_group_ids      = [aws_security_group.internal_sg.id]
  associate_public_ip_address = false

  root_block_device {
    volume_size = 32
    volume_type = "gp3"
  }
}

## Ubuntu (Database) will have SSH, HTTP, ICMP
resource "aws_instance" "ubuntu_db" {
  private_ip                  = "192.168.${var.team_number}.12"
  ami                         = var.ubuntu_ami
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.team_subnet.id
  key_name                    = "team-${var.team_number}-key"
  vpc_security_group_ids      = [aws_security_group.internal_sg.id]
  associate_public_ip_address = false

  root_block_device {
    volume_size = 32
    volume_type = "gp3"
  }
}

## CentOS (Fileshare) will have SSH, FTP, ICMP
resource "aws_instance" "centos_fileshare" {
  private_ip                  = "192.168.${var.team_number}.13"
  ami                         = var.centos_ami
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.team_subnet.id
  key_name                    = "team-${var.team_number}-key"
  vpc_security_group_ids      = [aws_security_group.internal_sg.id]
  associate_public_ip_address = false

  root_block_device {
    volume_size = 32
    volume_type = "gp3"
  }
}

resource "aws_instance" "debian_web" {
  private_ip                  = "192.168.${var.team_number}.14"
  ami                         = var.debian_ami
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.team_subnet.id
  key_name                    = "team-${var.team_number}-key"
  vpc_security_group_ids      = [aws_security_group.internal_sg.id]
  associate_public_ip_address = false

  root_block_device {
    volume_size = 32
    volume_type = "gp3"
  }
}

resource "aws_instance" "rocky_workstation" {
  private_ip                  = "192.168.${var.team_number}.15"
  ami                         = var.rocky_ami
  instance_type               = "t2.small"
  subnet_id                   = aws_subnet.team_subnet.id
  key_name                    = "team-${var.team_number}-key"
  vpc_security_group_ids      = [aws_security_group.internal_sg.id]
  associate_public_ip_address = false

  root_block_device {
    volume_size = 32
    volume_type = "gp3"
  }

  user_data = <<-EOF
              #!/bin/bash
              sudo dnf update -y
              sudo dnf install python3 -y
              EOF
}
