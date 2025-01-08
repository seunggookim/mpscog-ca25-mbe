import mturkapi, csv

# Set Subject and Message to send:
Subject = "SUBJECT GOES HERE"
MessageText = "MESSAGES\nGO\nHERE."

# Connect to MTURK API:
client = mturkapi.login(True)

# Read worker IDs to send it to:
with open('workersToNotify_1.csv') as myfile:
    reader = csv.reader(myfile)
    WorkerIds = list(reader)
    WorkerIds = [x[0] for x in WorkerIds]
    WorkerIds.remove('workerID')
    print('# of workerIDs: %i' %(len(WorkerIds)))
# SEND:
client.notify_workers(Subject=Subject, MessageText=MessageText, WorkerIds=WorkerIds)
