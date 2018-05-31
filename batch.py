#!/usr/bin/env python

import boto3
import pickle

from config import load_config
from benchmark import generate_tests

#Sends the job to amazon batch
def create_job(name, queue, definition, size, s3_bucket, s3_folder, vcpus = 1, memory = 1024):

    batch = boto3.client('batch')

    batch.submit_job(jobName=name,
                     jobQueue=queue,
                     arrayProperties={"size":size},
                     jobDefinition=definition,
                     containerOverrides={"vcpus":vcpus,"memory":memory,
                     "environment":[{"name":"S3_BUCKET","value":s3_bucket},{"name":"S3_FOLDER","value":s3_folder}]})

def benchmark():
    
    #Load config
    config = load_config()
    job_def = config["job_definition_id"]
    job_queue_id = config["job_queue_id"]
    job_name = config["job_name"]
    s3_bucket = config["s3_bucket_root"]
    s3_folder = config["s3_folder"]

    #Define batch resources
    vcpus = 4
    memory = 4096

    #Generate combinations
    s3 = boto3.resource('s3')
    with open("tests.dat", "wb") as f:
        tests = generate_tests()
        size = len(tests)
        pickle.dump(tests, f)
    with open("tests.dat", "rb") as f:
        s3.Bucket(s3_bucket).put_object(Key=s3_folder+"tests.dat", Body = f)

    
    create_job(job_name, job_queue_id, job_def, 2, s3_bucket, s3_folder, vcpus, memory)

if __name__ == '__main__':
    benchmark()