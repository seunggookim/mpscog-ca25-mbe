def login(create_hits_in_production = False):
    # REF: https://blog.mturk.com/tutorial-mturk-using-python-in-jupyter-notebook-17ba0745a97f

    import boto3, json, xmltodict

    #create_hits_in_production = False
    environments = {
      "production": {
        "endpoint": "https://mturk-requester.us-east-1.amazonaws.com",
        "preview": "https://www.mturk.com/mturk/preview"
      },
      "sandbox": {
        "endpoint": 
              "https://mturk-requester-sandbox.us-east-1.amazonaws.com",
        "preview": "https://workersandbox.mturk.com/mturk/preview"
      },
    }
#    mturk_environment = environments["production"] if create_hits_in_production else environments["sandbox"]
    key = "production" if create_hits_in_production else "sandbox"
    print("CURRENT ENVIRONMENT: %s" %key)
    mturk_environment = environments[key]
    session = boto3.Session(profile_name='mturk')
    client = session.client(
        service_name='mturk',
        region_name='us-east-1',
        endpoint_url = mturk_environment['endpoint'],
    )
    return client
#print(client.get_account_balance()['AvailableBalance'])
#print(client)

#REF: https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_NotifyWorkersOperation.html
