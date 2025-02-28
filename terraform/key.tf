resource "tls_private_key" "jumpbox" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "tls_private_key" "kali" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "tls_private_key" "team" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "jumpbox-key" {
  key_name   = "jumpbox-${var.team_number}-key"
  public_key = tls_private_key.jumpbox.public_key_openssh

  provisioner "local-exec" {
    command = "echo '${tls_private_key.jumpbox.private_key_pem}' > ./jumpbox-${var.team_number}-key.pem && chmod 600 ./jumpbox-${var.team_number}-key.pem"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "rm -f ./jumpbox-*.pem"
  }
}

resource "aws_key_pair" "kali-key" {
  key_name   = "kali-${var.team_number}-key"
  public_key = tls_private_key.kali.public_key_openssh

  provisioner "local-exec" {
    command = "echo '${tls_private_key.kali.private_key_pem}' > ./kali-${var.team_number}-key.pem && chmod 600 ./kali-${var.team_number}-key.pem"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "rm -f ./kali-*-key.pem"
  }
}

resource "aws_key_pair" "team-key" {
  key_name   = "team-${var.team_number}-key"
  public_key = tls_private_key.team.public_key_openssh

  provisioner "local-exec" {
    command = "echo '${tls_private_key.team.private_key_pem}' > ./team-${var.team_number}-key.pem && chmod 600 ./team-${var.team_number}-key.pem"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "rm -f ./team-*-key.pem"
  }
}
