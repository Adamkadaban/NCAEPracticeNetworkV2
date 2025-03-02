# RangePrivateInternalSecurityGroup
# RangeJumpBoxSecurityGroup

resource "aws_security_group" "jumpbox_sg" {
  description = "Allow traffic to the jumpbox"
  vpc_id      = aws_vpc.ncae_vpc.id

  # Range jumpbox security group
  # Range jumpbox allow outbound
  egress {
    from_port   = "0"
    to_port     = "0"
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Range allow jumbox ssh from internet
  # Range jumpbox security group
  ingress {
    from_port   = "22"
    to_port     = "22"
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "internal_sg" {
  description = "Allow all traffic from jumpbox to team sg"
  vpc_id      = aws_vpc.ncae_vpc.id

  # Range Allow internal traffic
  # Range private internal security group
  ingress {
    from_port   = "0"
    to_port     = "0"
    protocol    = "-1"
    cidr_blocks = ["192.168.${var.team_number}.0/24"]
  }

  # Range Allow private outbound
  # Range private internal security group
  egress {
    from_port   = "0"
    to_port     = "0"
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Range allow all traffic from jumpbox
  # Range jumpbox security group
  ingress {
    from_port = "0"
    to_port   = "0"
    protocol  = "-1"

    # TODO: IS THIS RIGHT? CHECK THIS
    security_groups = [aws_security_group.jumpbox_sg.id]
  }
}
