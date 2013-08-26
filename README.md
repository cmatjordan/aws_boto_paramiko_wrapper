aws_boto_paramiko_wrapper
=========================

You don't want to just spin up an ec2 image, you want to do things on it shortly afterwards.  Wrapper module for handling ec2 images and data transfer to them


class wrapper for three functions:
boto to create / terminate ec2 instances
paramiko to sftp to that instance
paramiko to ssh to that instance

