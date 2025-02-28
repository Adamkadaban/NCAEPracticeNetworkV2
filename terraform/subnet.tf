resource "aws_subnet" "team_subnet" {
  availability_zone = "${var.region}a"
  vpc_id            = aws_vpc.ncae_vpc.id
  cidr_block        = "192.168.${var.team_number}.0/24"
}

resource "aws_subnet" "public_subnet" {
  availability_zone       = "${var.region}a"
  cidr_block              = "192.168.99.0/24"
  vpc_id                  = aws_vpc.ncae_vpc.id
  map_public_ip_on_launch = "true"
}
