resource "aws_internet_gateway" "comp_igw" {
  vpc_id = aws_vpc.ncae_vpc.id
}
