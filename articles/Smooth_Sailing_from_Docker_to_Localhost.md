# Smooth Sailing from Docker to Localhost

![Header Image](/articles/images/Smooth_Sailing_from_Docker_to_Localhost.jpg)

Smooth Sailing from Docker to Localhost
David Cannan
David Cannan
on
Docker
8 December 2023
LinkedIn
X
Imagine you're developing on your laptop, using Docker to containerize your applications for consistency and ease of deployment. Your current project involves using MinIO for object storage, and you've set it up beautifully in Docker. But here's the twist: your workflow requires MinIO to interact with a Flask application running on your localhost for processing events and executing functions (referred to as
Event Notifications
and
Object Lambdas
in MinIO's context).
One of the common hurdles you might encounter in this setup is a networking-related error, typically manifesting as “
error (flask-notification:webhook): dial tcp 127.0.0.1:5000”
...
This error is indicative of a fundamental networking misalignment between the Docker container where MinIO is running and the Flask application hosted on your localhost. Essentially, when MinIO inside Docker tries to send event notifications to the Flask app, it attempts to connect to localhost:5000. However, within the Docker context, localhost refers to the Docker container itself, not the host machine where your Flask app is running. This results in MinIO attempting to establish a connection with a service on localhost:5000 inside its container, where no such service exists, leading to the connection being refused.
This scenario underscores the need for a clear understanding of Docker networking, particularly how localhost is interpreted differently inside a Docker container.
This guide will subsequently delve into effective strategies to realign this communication, ensuring that MinIO inside Docker can successfully send event notifications to the Flask app running on your host machine. By addressing this challenge, we create a development environment that closely simulates a production setup, improving the reliability and effectiveness of your workflow.
This walkthrough will guide you through the process of setting up this environment. We'll start by setting up MinIO within Docker, ensuring it's configured correctly to emit events. Then, we'll move on to the Flask application, designed to respond to these events. The crucial part of this guide will focus on enabling communication between the MinIO container and the Flask app running on your localhost. We'll tackle common hurdles such as Docker networking, address resolution and data consistency.
By the end of this guide, you'll have a functional local development setup where
MinIO events trigger actions in your Flask app
, mimicking a production-like environment on your laptop. This scenario is not just about making things work; it's about creating a development environment that's as close to production as possible, enhancing the reliability of your development and testing processes.
Understanding Docker Networking in Local Dev Strategies
As we progress towards integrating our Flask application, it's imperative to first comprehend a crucial aspect of Docker networking - the communication dynamics between Docker containers and the host machine. This knowledge is particularly indispensable for developers orchestrating local development environments, such as on laptops, where there is a need for Docker containers and host services, like our Flask application, to interact without hiccups.
The term '
localhost
' within the context of a Docker container has a unique implication. Contrary to its usual reference to the host machine, inside a Docker container, 'localhost' points to the container itself. This distinction is of paramount importance, especially when Dockerized services, such as MinIO, attempt to reach services on the host machine.
To illustrate this point, let's consider an error scenario as shown in the following image:
MinIO Event Notification Error Demo: “error (flask-notification:webhook): dial tcp 127.0.0.1:5000: connect: connection refused”
When MinIO, running inside a Docker container, fails to connect to the localhost – in this case, the Flask app on the host.
The connection error we encountered in our Docker-MinIO screenshot, characterized by the message
(flask-notification:webhook): dial tcp 127.0.0.1:5000: connect: connection refused
, initially appears complex. However, a closer analysis reveals its underlying cause. The segment flask-notification:webhook identifies the source of the issue – it's MinIO’s mechanism to interact with our Flask application. The phrase
dial tcp 127.0.0.1:5000
signifies MinIO's effort to establish a TCP connection with the Flask app, presumably located at
localhost:5000
. The critical part,
connection refused
, indicates that MinIO is unable to access the Flask app at the specified address, underscoring a fundamental challenge in containerized networking.
To correct this, a clear and direct communication pathway between MinIO and Flask is essential. For scenarios where Flask is hosted on the same machine but external to Docker, the solution involves configuring MinIO to connect to
host.docker.internal:5000
. This special DNS address acts like a direct line, enabling MinIO within its container to reach out to the Flask application on the host.
This offers a solution for Mac and Windows users through
host.docker.internal
, a DNS name that allows containers to correctly reference the host, thus facilitating the desired interaction between containerized services and host-based applications. Understanding and utilizing this Docker feature is critical for ensuring that local development setups mirror production environments as closely as possible, thereby enhancing development reliability and efficiency.
Overview of Assets
The foundation of our guide lies in the prepared assets available at the
GitHub minio/blog-assets repository
in the
docker_to_localhost
directory. Here I have provided the source code for anything discussed in this guide, at the heart of this repository, you'll find:
README File:
This
README.md
contains the relevant commands to preform the actions taken in Smooth Sailing from Docker to Localhost(this article).
Flask App Files
: This
main.py
file constitutes the Flask application, serving as a crucial component in our setup. It is tailor-made to interact efficiently with the MinIO service.
Docker File for Flask App
: This
dockerfile
is the blueprints for creating your Docker container. It defines the environment in which your Flask applications will be built and ran, ensuring consistency across different setups.
Docker Compose File
: Acting as the orchestrator, this
docker-compose.yaml
define how multiple containers (like MinIO and Flask) coexist and communicate within your Docker environment.
Deploying Flask App for MinIO Event Handling
In the context of integrating a Flask application with a Dockerized MinIO service, let's delve into the configuration of the Flask app. Specifically, I've set up a Flask endpoint with an identifier of
“flask-minio-event”
that is intended to serve as the receiver for MinIO's webhook events via
http://host.docker.internal:5000/minio_event
, as highlighted in the following screenshot:
Below is the code for our demonstration Flask App that runs on our local machine and serves out a route of
/minio_event
on
port 5000
:
from flask import Flask, request, jsonify
import logging
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
logging.basicConfig(level=logging.INFO)
I
@app.route('/minio_event', methods=['POST'])
def log_bucket_event():
"""
Logs events received from MinIO to the Python logger.
"""
event_data = request.json
logging.info(f"Event received: {event_data}")
return jsonify({'message': 'Event logged successfully'})

if __name__ == '__main__':
port = int(os.getenv('FLASK_PORT', 5000))
debug_mode = os.getenv('FLASK_DEBUG', 'False') == 'True'
app.run(host='0.0.0.0', port=port, debug=debug_mode)
In the previous section, we explored how Docker containers interpret 'localhost', which is a significant consideration in ensuring that the Flask app correctly receives notifications from a Dockerized MinIO instance.
This Flask application in more specific detail, is configured to receive and log events from MinIO. The endpoint /minio_event is set up to listen for POST requests, which are expected to be the event notifications from MinIO. Note that the application runs on port 5000 and is configured to be accessible from all network interfaces (0.0.0.0), which is crucial for receiving requests from MinIO running inside a Docker container.
Deploying MinIO Container with Docker Networking
Deploying the MinIO container to interact with localhost services like a Flask API requires a specific Docker network configuration. This setup is crucial for enabling seamless communication between the container and your local machine, particularly for local development or testing scenarios.
To achieve this, the MinIO container must be configured to use the host's network. This approach allows the container to directly interact with services running on the host machine, such as a Flask application. It's especially beneficial in development environments where the Flask app needs to access or store data in MinIO.
The command for this configuration is straightforward yet powerful:
docker run --name minio --network="host" minio/minio server /data
Using the
--network="host"
option removes the complexities of Docker's default network bridging and port forwarding. It's a simpler, more direct way to ensure that the MinIO container can access any service running on localhost, not just limited to the Flask app. This makes the MinIO container versatile for a variety of local services, streamlining the development and testing processes.
Deploying MinIO and Flask App Containers with Docker-Compose
You can use Docker networking features, such as a custom network or Docker Compose, to facilitate communication between containers. By placing both containers on the same network, they can communicate using their container names as hostnames.
Example using Docker Compose to facilitate the communication between a MinIO container named minio, and a Flask app container named flaskapp specified below as services:
version: '3.8'
services:
minio:
image: minio/minio
command: server /data
ports:
- "9000:9000"
extra_hosts:
- "host.docker.internal:host-gateway"
networks:
- mynetwork

flaskapp:
image: python:3.9 # Use an official Python image
command: >
sh -c "pip install Flask
&& FLASK_APP=main.py FLASK_RUN_HOST=0.0.0.0 flask run" # Install Flask and run the app
volumes:
- ./app:/app # Mount your Flask app directory
working_dir: /app # Set working directory to your app directory
ports:
- "5000:5000"
depends_on:
- minio
networks:
- mynetwork

networks:
mynetwork:
driver: bridge
This setup maps host.docker.internal to the host machine's IP address, allowing containers to access services on the host by adding the extra_hosts parameter. This setup allows MinIO to recognize host.docker.internal as the host machine, bridging the container-to-host communication gap. It's a smart workaround for a common Docker challenge, ensuring that MinIO can connect to services on the host, such as our Flask app.
Additionally by including the Flask installation in the docker-compose file we will make the app listen on 0.0.0.0. This change is vital for accessibility from other containers and the host, broadening the communication scope of our Flask app. It’s an essential step for setups where Flask might also be containerized.
The depends_on directive in the Flask service ensures an orderly startup sequence. By starting the Flask app only after MinIO is operational, we avoid potential timing issues. This arrangement mimics production environments where service dependencies are carefully managed, adding robustness to our local development setup.
💡
These examples are tailored for a Dockerized MinIO setup, ensuring effective communication with services running on the host. Be mindful of the security implications, especially when adjusting network settings or exposing ports, and choose the solution that aligns with your security and architectural requirements.
Both methods will allow the MinIO service to communicate with your Flask application, depending on whether the Flask app is running on the host or inside another Docker container.
Seamless Integration in a Dockerized World
We've journeyed through the nuances of Docker networking, unraveling how to efficiently bridge Docker containers with localhost environments so a Dockerized MinIO service can effectively communicate with a Flask application running on your host machine. These insights are crucial for developers looking to harness the power of Docker without compromising on the flexibility and convenience of local development.
Understanding Docker networking is more than a technical necessity; it's a step toward mastering containerized environments. The ability to set up and manage these interactions is a requirement in today's cloud-native development landscape. Whether you're developing on a laptop or deploying on a global scale, these skills ensure your applications remain robust, scalable, and secure.
It's important to understand and implement best practices when developing cloud-native software. The Docker ecosystem is ever-evolving. You can quickly tap into the latest and greatest cloud-native technologies with an architecture based on containers and object storage. Stay curious and keep exploring.
MinIO enables this exploration. Containerized, Kubernetes-native and S3 API compatible, MinIO frees you to write code that runs anywhere, consistently and reliably.
Good luck on your journey with Docker and MinIO. May your development be robust, your solutions secure, and your learning continuous. If you have any questions we’re here to help, at
hello@min.io
or by joining the
Slack community
.
S3 Select
Security
Modern Data Lakes
Apache Presto
SQL
Performance
S3
Brand/Design
Golang
Programming
Cloud Computing
Microservices
Docker
AWS
Kubernetes
Apache Spark
Open Source
Benchmarks
Integrations
SUBNET
Edge Computing
Sidekick
Secure-by-Design
Splunk
Veeam
Intel
Apache Nifi
Immutability
Software Defined Storage
VMware
Apache Arrow
Hybrid Cloud
Red Hat OpenShift
Multicloud
Scalability
Cloud Field Day
Cloud Native
Apache Kafka
Architect's Guide
Awards
Operator's Guide
Security Advisory
AI/ML
AGPLv3
Apache Hadoop
SFD
Azure
GCP
Observability
Analytics
R
H20
DirectPV
DevOps
Apache Iceberg
Apache Hudi
YouTube Summaries
EKS
Elastic Load Balancers
CI/CD
Object Storage
Compliance
opentelemetry
BC/DR
Storage Newsletter Predictions
Best Practices
Dremio
New MinIO Features
partners
Small Files
Databases
DuckDB
PostgreSQL
Delta Lake
Cloud Repatriation
Python
Object Lambdas
Data Pipelines
Cloud Operating Model
Webhook
ClickHouse
Vector Database
Events
Value Engineering
Change Data Capture
Enterprise Object Store
GitOps
Case Study
Equinix
Certifications
Snowflake
Repatriation
Migration
