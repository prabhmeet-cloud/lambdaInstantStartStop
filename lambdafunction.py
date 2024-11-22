import boto3
from datetime import datetime

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    today = datetime.now().weekday()  # 0 = Monday, 6 = Sunday
    
    # Skip weekends
    if today >= 5:
        print("It's a weekend. No action taken.")
        return
    
    # Determine action: 'start' or 'stop' from event payload
    action = event['action']
    
    # Set the instance state filter based on the action
    if action == 'start':
        state_filter = 'stopped'  # Start only stopped instances
    elif action == 'stop':
        state_filter = 'running'  # Stop only running instances
    
    # Get instances with tag 'environment: DEV' and desired state
    instances = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:environment', 'Values': ['DEV']},
            {'Name': 'instance-state-name', 'Values': [state_filter]}
        ]
    )

    # Extract instance IDs
    instance_ids = [
        instance['InstanceId']
        for reservation in instances['Reservations']
        for instance in reservation['Instances']
    ]

    # Perform action if instances are found
    if instance_ids:
        if action == 'start':
            ec2.start_instances(InstanceIds=instance_ids)
            print(f"Started instances: {instance_ids}")
        elif action == 'stop':
            ec2.stop_instances(InstanceIds=instance_ids)
            print(f"Stopped instances: {instance_ids}")
    else:
        print(f"No instances to {action}.")
