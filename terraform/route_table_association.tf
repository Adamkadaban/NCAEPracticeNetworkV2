resource "aws_route_table_association" "public_rtb_assoc" {
  route_table_id = aws_route_table.public_rtb.id
  subnet_id      = aws_subnet.public_subnet.id
}

resource "aws_route_table_association" "team_rtb_assoc" {
  route_table_id = aws_route_table.team_rtb.id
  subnet_id      = aws_subnet.team_subnet.id
}
