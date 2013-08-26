from boto import ec2
from boto.ec2.connection import EC2Connection
from boto.ec2.address import Address
import paramiko
import time, os, glob, math, sys

class instance:

        def __init__(self, access_key, secret_key, ip_address=None):
                #save my ec2 connection info
                self.access_key = access_key
                self.secret_key = secret_key
                self.ec2conn = EC2Connection(access_key, secret_key)


                self.sshconn = None

                #match up the ip with an instance, if there is one
                if ip_address is not None:
                        self.ip_address = ip_address

                        self.instance_name = None

                        reservations = self.ec2conn.get_all_instances()
                        #find our instance, and check to see if its state is running
                        instance_list = [i for r in reservations for i in r.instances]
                        for i in instance_list:
                                if i.__dict__['ip_address'] is not None: #you can'te encode a nonetype, so you have to check this first.  silly python.
                                        if i.__dict__['ip_address'].encode('ascii', 'ignore') == self.ip_address:
                                                self.instance_name = i.__dict__['id']
                                                print self.instance_name

                        if self.instance_name is None:
                                print "there is no image at that ip address"


                        public_dns = "ec2-%s-%s-%s-%s.compute-1.amazonaws.com" % (self.ip_address.split('.')[0], self.ip_address.split('.')[1], self.ip_address.split('.')[2], self.ip_address.split('.')[3])
                        
                        
                        
        def new_instance(self, size, ami_name, sec_group, key_name):
                #save for later
                self.sec_group = [sec_group] #yes it has to be an array
                self.key_name = key_name


                #pull the machine image down using the name given
                image_list = self.ec2conn.get_all_images()
                self.image_exists = False
                for image in image_list:
                        if image.name == ami_name:
                                self.image_exists = True
                                self.ami = image.id


                if self.image_exists == False:
                        print "there is no image associated with your account named %s" % ami_name

                #spin up the instance
                self.inst = self.ec2conn.run_instances(self.ami, key_name=self.key_name, instance_type=size, security_groups=self.sec_group)

                self.instance_name = str(self.inst.instances[0]).split(':')[-1]



                running = False #assume it's not running
                while running==False:
                        #wait a moment
                        time.sleep(10)
                        #get all the instances
                        reservations = self.ec2conn.get_all_instances()
                        #find our instance, and check to see if its state is running
                        instance_list = [i for r in reservations for i in r.instances]
                        for i in instance_list:
                                #print i.__dict__.keys()
                                if i.__dict__['id']==self.instance_name:
                                        if str(i.__dict__['_state'])[:7]=='running': #just check the first seven characters, since amazon adds some trailing chars and they're not always the same

                                                print "Instance %s is %s" % (self.instance_name, i.__dict__['_state'])
                                                running=True
                                        else:
                                                print "Instance %s is %s.  Please wait one moment..." % (self.instance_name, i.__dict__['_state'])


                #assign an elastic ip
                new_addy = self.ec2conn.allocate_address()
                new_addy.associate(instance_id=self.instance_name)
                self.ip_address = str(new_addy).split(':')[-1]


                public_dns = "ec2-%s-%s-%s-%s.compute-1.amazonaws.com" % (self.ip_address.split('.')[0], self.ip_address.split('.')[1], self.ip_address.split('.')[2], self.ip_address.split('.')[3])
                self.public_dns = public_dns.encode('ascii', 'ignore')

                for i in range(7):
                        print "your image is active, and it will be accessible in %s minutes" % str(3-i/2)
                        time.sleep(30)



        def connect(self, user, key_path):

                self.user = user

                self.sshconn = paramiko.SSHClient()
                self.sshconn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.sshconn.connect(hostname=self.ip_address, username=self.user, key_filename=key_path)

        def command(self, command):
                pass



        def put(self, fileNames, localPath=None, remotePath=None):

                if self.sshconn is None:
                        print "you need to initiate a connection before running this function"


                #set the default toPath, since we can't actually use self in the function call line defaults
                if remotePath is None:
                        remotePath = "/home/%s/" % self.user

                if localPath is None:
                        localPath = "%s/" % os.getcwd()

                ftp = self.sshconn.open_sftp()


                #get all the desired files
                #upload them to the home directory
                for putfile in fileNames:
                        print "uploading %s%s...." % (localPath, putfile)
                        try:
                                ftp.put("%s%s" % (localPath, putfile), "%s%s" % (remotePath, putfile))
                        except:
                                "couldn't upload %s%s" % (localPath, putfile)

                print "uploads complete"


        def get(self, fileNames, localPath=None, remotePath=None):

                if self.sshconn is None:
                        print "you need to initiate a connection before running this function"


                #set the default toPath, since we can't actually use self in the function call line defaults
                if remotePath is None:
                        remotePath = "/home/%s/" % self.user

                if localPath is None:
                        localPath = "%s/" % os.getcwd()

                ftp = self.sshconn.open_sftp()



                #get all the desired files
                #upload them to the home directory
                for getfile in fileNames:
                        print "downloading %s%s...." % (remotePath, getfile)
                        try:
                                ftp.get("%s%s" % (remotePath, getfile), "%s%s" % (localPath, getfile))
                        except:
                                "couldn't download %s%s" % (remotePath, getfile)

                print "downloads complete"


        def terminate_instance():
                pass
