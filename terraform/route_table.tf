resource "aws_route_table" "public_rtb" {
  vpc_id = aws_vpc.ncae_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.comp_igw.id
  }
}

resource "aws_route_table" "team_rtb" {
  vpc_id = aws_vpc.ncae_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.team_ngw.id
  }
}
