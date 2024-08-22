# Event-Driven Architecture: MinIO Event Notification Webhooks using Flask

![Header Image](/articles/images/Event-Driven_Architecture__MinIO_Event_Notification_Webhooks_using_Flask.jpg)

Event-Driven Architecture: MinIO Event Notification Webhooks using Flask
David Cannan
David Cannan
on
Events
23 January 2024
LinkedIn
X
Event notifications in MinIO may not seem thrilling at first, but once you harness their power, they illuminate the dynamics within your storage buckets. Event notifications are critical components of a full-fledged, efficient object storage system. Webhooks are my personal
favorite tool for integrating with MinIO
. They are like a Swiss Army knife in the world of events, offering a universal solution to various challenges.
MinIO's user-friendly UI provides seamless service
integrations
, but we're diving deeper in this guide. We're building services from scratch in Python, using their client credentials, to walk you through the nuts and bolts of MinIO integration.
In our exploration, we'll focus on deploying using docker-compose, a method that offers streamlined and efficient orchestration. This approach will involve setting up a cohesive environment for MinIO and Flask, enabling them to interact seamlessly. By integrating the MinIO service with its appropriate credentials and configurations, we aim to create a systematic workflow that effectively demonstrates the practical application of managing and responding to MinIO bucket events.
Once we set up client configurations and define the structure for response data, as always, the real fun begins. This demonstration will highlight several key aspects of how you can connect your MinIO client to a Flask application where the event notification data can further be processed. We want you to feel comfortable in developing your own event-driven systems with MinIO, so utilize the services we've provided in the
blog-assets/flask-webhook-event-notifications
resource hosted on
MinIO’s GitHub Page
.
Prepare to dive into a world where data handling is both an art and a science, made simpler with MinIO. It's an opportunity to innovate, create and revolutionize the way your apps work with data.
MinIO and Integrated Services
MinIO's integration into the
Kubernetes ecosystem
exemplifies its adaptability across various cloud technologies. Webhooks are pivotal, offering developers the flexibility to craft custom integrations, whether for managing data across diverse cloud platforms or for local home lab setups.
This guide goes beyond theoretical concepts, providing you with practical, executable code snippets to build your integrations. It's an invitation to explore the boundless potential of your creativity in leveraging MinIO event notifications.
Laying the Groundwork for a Python Application with Docker
The initial phase of our journey is dedicated to harnessing the power of Docker's containerization to craft a robust Python application environment. Our approach centers around deploying with Docker-compose, a method chosen for its simplicity and effectiveness. This choice is designed to cater to a wide range of developers, prioritizing ease of use and rapid deployment while ensuring a high level of functionality.
Utilizing Docker-compose, we create a user-friendly, configuration-driven setup. This environment is perfect for those seeking quick deployment without sacrificing the depth of their project's capabilities. It provides a straightforward pathway to integrate advanced webhook features and fine-tune MinIO settings, catering to the specific requirements of your project.
Each step we take in setting up this environment is crucial. It's not just about getting the services up and running; it's about understanding and leveraging components to create a comprehensive system. Developing your own systems can be the spark that ignites your innovation, enhancing your overall data management strategy, and eventually turns your raw data into actionable, insightful information.
Deploying MinIO and Integrated Services
Deploy with Docker-Compose: Flask App and MinIO
We will begin by setting up a Python application and its environment. This involves deploying MinIO with docker compose and the services to be integrated. To set up MinIO with a Flask application, we will be using the
git
command to clone the
minio/blog-assets
repository to your local environment:
git clone https://github.com/minio/blog-assets.git

cd flask-webhook-event-notifications

docker-compose up
This will clone the
minio/blog-assets
repository from GitHub, navigate to the
/flask-webhook-event-notifications/
directory containing the
docker-compose.yaml
file, and start the MinIO and Flask services.
Directory Structure
This docker-compose structure outlines two services and their respective configuration variables. For visualization purposes, I have provided a tree view of the desired directory structure here:
/flask-webhook-event-notifications
├── Dockerfile
├── app
│       └── main.py
└── docker-compose.yaml
Setting up Webhooks in MinIO
Configuring a webhook in MinIO can be accomplished through various methods ranging from using the user-interface, by using
mc
(the MinIO client utility), or by way of scripting with various programming languages.
MinIO supports a
variety of external services for event notifications
, including:
AMQP (RabbitMQ)
,
MQTT
,
NATS
,
NSQ
,
Elasticsearch
,
Kafka
,
MySQL
,
PostgreSQL
,
Redis
, and
webhook services
.
Setting up MinIO to utilize these
event notifications
involves a series of well-defined steps, ensuring that your MinIO instance not only captures but also effectively communicates important event data as  an interactive, responsive part of your application ecosystem.
Understanding the Data Structure of MinIO Event Notifications
The S3 event notifications from MinIO include a
detailed JSON data structure
, essential for a comprehensive understanding and effective management of events. Below I have listed some of the values found from within the event data:
Key
: The unique identifier of the object in the bucket.
eTag
: The object’s version identifier for integrity and version control.
Size
: The size of the object in bytes, indicating its scale.
Sequencer
: Ensures the events are processed in the exact sequence they occurred.
ContentType
: The media type of the object, specifying how to handle or display the file.
UserMetadata
: User-defined metadata attached to the object, providing additional context.
Bucket Details
:
ARN (Amazon Resource Name)
: The unique identifier for the bucket in AWS.
Name
: The name of the bucket where the object is stored.
OwnerIdentity
: Information about the owner of the bucket.
s3SchemaVersion
: Indicates the version of the S3 event notification schema used.
ConfigurationId
: Identifier for the specific notification configuration that triggered this event.
This structure is particularly effective for
Flask applications
, enabling systematic logging, parsing and analysis of interactions with the MinIO bucket.
Setting Up MinIO for Webhooks and Event-Driven Operations
After deploying the
docker-compose.yaml
outlined above, continue by using the MinIO Client,
mc
, command-line utility. This setup involves creating an alias in MinIO, configuring the endpoint and setting bucket notifications.
We will be working inside of an interactive terminal for the
“minio”
container, which we can spawn by running a single command:
docker exec -it minio /bin/sh
The reason for running our mc commands from within this shell is because the Docker
minio/minio
image already has
mc
installed and ready to go.
Once inside the container’s interactive terminal, the process of configuring MinIO for event notifications using the MinIO Client (mc) involves the following key steps:
Setting Up MinIO Alias
: The first step involves creating an alias for your MinIO server using the MinIO Client (mc). This alias is a shortcut to your MinIO server, allowing you to easily execute further mc commands without repeatedly specifying the server’s address and access credentials. This step  simplifies the management of your MinIO server through the client.
mc alias set myminio http://localhost:9000 minio minio123
Adding the Webhook Endpoint to MinIO
: Configure a new webhook service endpoint in MinIO. This setup is done using either environment variables or runtime configuration settings, where you define important parameters such as the endpoint URL, an optional authentication token for security, and client certificates for secure connections.
mc admin config set myminio notify_webhook:1 endpoint="http://flaskapp:5000/minio-event" queue_limit="10"
Restarting the MinIO Deployment
: Once you have configured the settings, restart your MinIO deployment to ensure the changes take effect.
mc admin service restart myminio
Expect:
Restart command successfully sent to myminio. Type Ctrl-C to quit or wait to follow the status of the restart process....Restarted myminio successfully in 1 seconds
Configuring Bucket Notifications
: The next step involves using the mc event add command. This command is used to add new bucket notification events, setting the newly configured Webhook service as the target for these notifications.
mc event add myminio/mybucket arn:minio:sqs::1:webhook --event put,get,delete
Expect:
Successfully added arn:minio:sqs::1:webhook
List Bucket Subscribed Events
: Run this command to list the event assigned to myminio/mybucket:
minio mc event list myminio/mybucket
Expect:
arn:minio:sqs::1:webhook   s3:ObjectCreated:*,s3:ObjectAccessed:*,s3:ObjectRemoved:*   Filter:
List Bucket Assigned Events (in JSON)
: Run this command to list the event assigned to myminio/mybucket in JSON format:
minio mc event list myminio/mybucket arn:minio:sqs::1:webhook --json
Expect:
{ "status": "success", "id": "", "event": ["s3:ObjectCreated:
","s3:ObjectAccessed:
", "s3:ObjectRemoved:*"], "prefix": "", "suffix": "", "arn": "arn:minio:sqs::1:webhook"}
The Structure of the Event Notification Data Received by Flask
Depending on the services or integration you are building, you may need to identify the event_data from your Flask app, and this requires a good understanding of the data your event provides.
{
"s3": {
"bucket": {
"arn": "arn:aws:s3:::mybucket",
"name": "mybucket",
"ownerIdentity": {
"principalId": "minio"
}
},
"object": {
"key": "cmd.md",
"eTag": "d8e8fca2dc0f896fd7cb4cb0031ba249",
"size": 5,
"sequencer": "17A9AB4FA93B35D8",
"contentType": "text/markdown",
"userMetadata": {
"content-type": "text/markdown"
}
},
"configurationId": "Config",
"s3SchemaVersion": "1.0"
},
"source": {
"host": "127.0.0.1",
"port": "",
"userAgent": "MinIO (linux; arm64) minio-go/v7.0.66 mc/RELEASE.2024-01-11T05-49-32Z"
},
"awsRegion": "",
"eventName": "s3:ObjectCreated:Put",
"eventTime": "2024-01-12T17:58:12.569Z",
"eventSource": "minio:s3",
"eventVersion": "2.0",
"userIdentity": {
"principalId": "minio"
},
"responseElements": {
"x-amz-id-2": "dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8",
"x-amz-request-id": "17A9AB4FA9328C8F",
"x-minio-deployment-id": "c3642fb7-ab2a-44a0-96cb-246bf4d18e84",
"x-minio-origin-endpoint": "http://172.18.0.3:9000"
},
"requestParameters": {
"region": "",
"principalId": "minio",
"sourceIPAddress": "127.0.0.1"
}
}
By following these steps, you can effectively utilize MinIO event notifications, significantly automating data workflow processes. For more detailed guidance and information, please refer to the MinIO documentation on
Bucket Notifications
and
Monitoring Bucket and Object Events
.
If you're interested in setting up
MinIO with PostgreSQL
, take a look at
Streamlining Data Events with MinIO and PostgreSQL
, where I’ve covered MinIO's extensive configuration and management of data events. These configurations range from using the
MinIO Console
for a user-friendly graphical interface to the
mc
command-line tool
for a more detailed, scriptable setup. The blog post further rounds out your understanding of the topic by emphasizing the importance of properly configuring PostgreSQL in the MinIO UI and the significance of restarting the MinIO server for changes to take effect.
Developing a Webhook with Flask to Receive Event Notifications
Following the deployment of our environment, we now shift our focus to the integration of MinIO with Python, a key aspect of our data handling and processing system. This integration is pivotal in creating a cohesive ecosystem, where MinIO can seamlessly collaborate with Flask.
Importing the Necessary Packages
In our demonstration code, we carefully select Python imports to ensure the application's functionality aligns with its intended purpose. The
flask
package creates the web server infrastructure, defining endpoints to handle incoming HTTP requests. Then the application can be coded to handle the MinIO event notifications in any desired manner.
from flask import  Flask, jsonify, request
These imports collectively form the foundation of the application, enabling it to receive and process MinIO event notifications.
Flask Application and Event Handling Endpoint in Python
A Flask application is instantiated, and an endpoint is set up to handle POST requests at the route
/minio-event
. Flask is a micro web framework in Python, ideal for setting up web applications and API endpoints.
app = Flask(__name__)

@app.route('/minio-event', methods=['POST'])
def handle_minio_event():
event_data = request.json
app.logger.info(f"Received MinIO event: {event_data}")
return jsonify(event_data), 200
The
handle_minio_event
function in the Flask app processes POST requests containing MinIO event data, and returns the
event_data
received from the MinIO event notification.
This approach facilitates real-time processing and response to storage events, enabling dynamic interaction between the MinIO storage system and the Flask application.
Integrating Services with MinIO Bucket Events via Python Scripting
This blog post used MinIO and Python in a Docker environment to demonstrate the power and flexibility of MinIO bucket event notifications, and demonstrates a strategic approach for creating scalable, efficient event-driven applications.
The use of Docker, with its containerization technology, stands out for enabling components like MinIO and Flask to work independently yet cohesively. Of course, this containerized cloud-native setup minimizes conflicts and dependencies, highlighting Docker and Docker containers significance in modern software architecture.
In conclusion of our exploration of MinIO webhook event notifications, I am convinced that the synergy of a dynamic programming language and MinIO’s formidable strength presents an unparalleled toolkit. This pairing paves the way for boundless opportunities in application development. It empowers us to not only innovate and streamline but also to expand our capabilities with remarkable efficiency and adaptability.
This guide has demonstrated the simplicity and efficacy of API development using Python, laying a solid foundation for ongoing innovation and meeting ever-changing demands. It underscores the adaptability that is essential for the continued advancement in both data management and the evolution of application development. This approach is not just a methodology; it’s a pathway to future-proofing our technological endeavors.
