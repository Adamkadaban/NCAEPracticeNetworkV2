output "jumpbox_ip" {
    value = aws_instance.jumpbox.public_ip
    description = "Public IP address of the jumpbox"
}
