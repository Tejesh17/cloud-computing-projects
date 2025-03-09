import boto3

resource = boto3.resource('ec2')
client = boto3.client('ec2')

def createInstance(name):
	try:
		instance = resource.create_instances(
			ImageId='ami-00ff4892e079a85a7',
			InstanceType='t2.micro',
			MaxCount=1,
			MinCount=1,
		)
		if(len(instance)> 0):
			client.create_tags(
				Resources = [instance[0].id],
				Tags = [
					{
						'Key': 'Name',
						'Value': name
					}
				]
			)
			return instance[0].id
		else:
			print("Something went wrong\n")
			return
	except Exception as e:
		print(e)

def listInstances():
	instances = client.describe_instances()
	i = 1
	print("EC2 Instances:")
	try:
		for instance in instances['Reservations']:
			if(instance["Instances"][0]["State"]["Name"] == "running"):
				print(f'{i}: Image ID- {instance["Instances"][0]['ImageId']}, Instance ID- {instance["Instances"][0]['InstanceId']}')
				i+=1
		print("\n")
	except :
		print("Something went wrong\n")


def stopInstance(instanceIDs):
	client.stop_instances(InstanceIds=instanceIDs, DryRun=False)

def terminateInstance(instanceIDs):
	try:
		client.terminate_instances(
			InstanceIds=instanceIDs,
		)
	except Exception as e:
		print("error terminating instance " + e)