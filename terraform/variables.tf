variable "team_number" {
  description = "Team number for this network"
  type        = number
}

#variable "team_numbers" {
#  description = "List of team numbers"
#  type        = list(number)
#  default     = [1] # Add more teams here
#}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "debian_ami" {
  description = "AMI ID for Debian Instances"
  type        = string
  default     = "ami-0057260feaab58d28"
}

variable "ubuntu_ami" {
  description = "AMI ID for Ubuntu Instances"
  type        = string
  default     = "ami-0dba2cb6798deb6d8"
}

variable "centos_ami" {
  description = "AMI ID for CentOS Instances"
  type        = string
  default     = "ami-0705f7887207411ca"
}

variable "windows2022_ami" {
  description = "AMI ID for Windows Server 2022 Instances"
  type        = string
  default     = "ami-015f002db921fbf07"
}

variable "opnsense_ami" {
  description = "AMI ID for OPNSense Instances"
  type        = string
  default     = "ami-00e5812396dc365ac"
}

variable "kali_ami" {
  description = "AMI ID for Kali Instances"
  type        = string
  default     = "ami-02be3d7604aff56a7"
}

variable "rocky_ami" {
  description = "AMI ID for Rocky instances"
  type        = string
  default     = "ami-011ef2017d41cb239"
}
