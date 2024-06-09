# Streamlining Data Events with MinIO and PostgreSQL

Streamlining Data Events with MinIO and PostgreSQL
David Cannan
David Cannan
on
Events
16 January 2024
Share:
Linkedin
X (Twitter)
Reddit
Copy Article Link
Email Article
Follow:
LinkedIn
X
Reddit
This tutorial will teach you how to  set up and manage data events, also referred to as bucket or object events, between MinIO and PostgreSQL using Docker and Docker Compose.
You’re probably already leveraging MinIO events to communicate with external services,  and now you'll enhance your data handling capabilities by automating and streamlining data event management with PostgreSQL. This article is tailored for those with a basic understanding of MinIO, PostgreSQL, and Docker, offering a hands-on approach to deploying a cohesive environment where MinIO and PostgreSQL work in unison.
Let’s dive into deploying these services with Docker Compose and explore the practical applications of publishing events from MinIO to PostreSQL.
Prerequisites
:
Docker and Docker Compose installed
Basic knowledge of MinIO, PostgreSQL, and Docker
Access to a MinIO UI or command-line interface with Docker
MinIO and Integrated Services
Kubernetes-native MinIO
seamlessly integrates
with a wide range of cloud-native technologies. This guide will leverage MinIO’s native support for services like Postgres, Redis, Kafka, and others. These integrations are essential for fluid data management across diverse cloud environments.
We're going to use Docker Compose to create a user-friendly, configuration-driven setup.  This tutorial provides a straightforward pathway to integrate advanced notification features and fine-tune MinIO settings, catering to the specific requirements of your project.
Practical Applications in Data Management
The integration of MinIO with PostgreSQL, as demonstrated, opens a plethora of practical applications in various fields:
Data Analytics and Reporting
: Automatically capture data changes in MinIO buckets and use PostgreSQL for analytics and generating insights.
Backup and Recovery:
Implement robust data backup solutions by tracking every change in the data stored in MinIO.
Event-Driven Applications:
Develop applications that respond to data changes in MinIO, like triggering processes or alerts when new data is uploaded.
Compliance and Auditing:
Maintain logs of data access and changes for compliance with regulatory standards.
This setup is especially useful in environments where real-time data tracking is crucial, such as in financial services, healthcare, and e-commerce.
Deploying the MinIO & PostgreSQL Services
Setting up Event Notifications in MinIO
Event notifications in MinIO are configured through various methods ranging from using the user-interface, by running command line utilities and by way of scripting with various programming languages and SDKs. Let's take a look at the pros and cons of each:
The MinIO Console
: This approach offers a user-friendly, graphical interface, allowing you to visually manage the webhook settings.
MinIO's mc command line tool
: For those who prefer a command-line interface, MinIO provides the mc command tool, which allows detailed and scriptable configuration of webhooks.
Code and Scripting
: With Bash and Python scripting, this method offers a high degree of flexibility and automation in the setting up of webhooks.
The following describes how to  deploy and connect MinIO and PostgreSQL using two different methods: the MinIO Console and the mc command-line client utility. Both methods focus on configuring MinIO to send bucket event notifications straight to a PostgreSQL database, ensuring real-time data synchronization and streamlined workflows.
Deploy with Docker-Compose: MinIO + Postgres
We will begin by setting up MinIO and its environment along with a PostgreSQL database. This involves deploying a Docker Compose file if you  do not already have these services running.
We will use the docker-compose YAML file below to deploy and start MinIO and PostgreSQL using Docker Compose.
version: '3.8'
services:
  minio:
    container_name: minio
    image: minio/minio
    environment:
      MINIO_ACCESS_KEY: minio
      MINIO_SECRET_KEY: minio123
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"

    volumes:
      - minio_data:/data

  postgres:
    container_name: postgres
    image: postgres:alpine
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  minio_data:
  postgres_data:
This docker-compose structure outlines two services and their respective configuration variables, as well as persistent volumes and network port forwarding for each.
When configuring the PostgreSQL connection in MinIO, include the user and password in the connection string. For instance, your connection string in the MinIO configuration might look like:
connection_string="user=myuser password=mypassword host=postgres dbname=postgres port=5432 sslmode=disable"
. This ensures that MinIO can successfully connect and authenticate with the PostgreSQL database.
Creating a Table for our Bucket Events in PostgreSQL
Before setting up our Flask application to record and process event notifications from the MinIO bucket, we first need to establish a proper database structure in PostgreSQL. This involves creating a dedicated table to log these events.
Creating the ‘Events’ Table in PostgreSQL
Begin by accessing your PostgreSQL container. This can be done by executing the “docker exec” command. Next, you need to create the
‘events’
table. This table is designed to store various details about each event. Execute this command in the PostgreSQL container:
docker exec postgres psql -U myuser -d postgres -c "DROP TABLE IF EXISTS events; CREATE TABLE events (key TEXT PRIMARY KEY, value JSONB);"
After creating the table, exit the PostgreSQL container by typing exit in the command prompt:
We're ready to log and analyze interactions with the MinIO bucket using events to systematically track events like file uploads, modifications or deletions within the bucket.
Setting Up Event Notifications with Local PostgreSQL Server
To set up event notifications in MinIO with a PostgreSQL server that's running on the host machine in a Docker environment, use
host.docker.internal
as the host in your connection string. This special DNS name resolves to the internal IP address used by the host. This setup is detailed in my previous article
From Docker to Localhost
.
If postgres was running on localhost, your connection string would be:
connection_string="user=myuser password=mypassword host=host.docker.internal dbname=postgres port=5432 sslmode=disable"
This approach is crucial for ensuring MinIO within a Docker container can communicate effectively with PostgreSQL running on your host machine.
The MinIO UI and
mc
: A Dual Approach for Enhanced Data Management
In the realm of cloud storage and data management, flexibility and control are paramount. MinIO addresses this need through its dual approach: the intuitive
MinIO Console (UI)
and the powerful
mc
(MinIO Client) Command-Line Interface (CLI)
. This tutorial includes instructions for using both so you can choose whichever element of this versatile and comprehensive toolset you prefer.
MinIO UI:
The graphical user interface is user-friendly and perfect for those who prefer a visual approach to configuration and management. It allows you to easily navigate through buckets, set up event notifications, and monitor your storage. The UI is especially beneficial for quick setups and for users who are more comfortable with a point-and-click environment.
mc
Command-Line Tool
: On the other hand, the
mc
CLI offers granular control over your MinIO instance. It is a potent tool for scripting, automation, and detailed configuration. This interface is ideal for advanced users who require precise control over their storage, networking and data management tasks. The CLI facilitates complex tasks like batch operations, scripting for automated backups and direct manipulation of objects across various environments.
By leveraging both the UI and CLI, MinIO users can enjoy the best of both worlds: ease of use and advanced control, ensuring a highly efficient and flexible data management experience.
Let's take a look at the different methods for managing data events.
Using the MinIO UI
Configuring PostgreSQL in MinIO User-Interface:
Open a browser and go to "
http://localhost:9001
". Log in using the MinIO credentials created during installation. Navigate to the event notification settings in the MinIO Console, click
Add Event Destination
and select PostgreSQL as the service.
As seen in the screenshot below, enter an Identifier of
“minio-postgres-demo”
for the bucket event we wish to create and then continue to configure the required parameters.
By assigning the “
Connection String
”, as we outlined in the earlier, we are able to set our Postgres container as the host; and likewise add the
“table”
name
“events”
as the destination’s table name.
The process of setting up the PostgreSQL service endpoint involves either using environment variables or setting runtime configuration settings. After these settings are specified, the MinIO server needs to be restarted for them to take effect. This is because MinIO loads its configuration at startup, and changes made in the UI need a restart to be recognized and implemented by the system.
Restart the MinIO Server:
It's important to note that simply configuring the settings in the UI does not automatically trigger a restart of the MinIO service. Therefore, after completing the UI configuration for PostgreSQL event notifications, you should use the command with the
docker exec minio
prefix, to manually restart your MinIO deployment. This step ensures that your configuration changes are picked up and the event notifications start functioning as expected.
docker exec minio mc admin service restart
Creating the Bucket:
To effectively use the event notifications in MinIO with PostgreSQL, first create a bucket in the MinIO deployment. This bucket is where all the events that you wish to monitor will occur. For the purpose of this guide, we will name this bucket
“test”
. This name should be consistent with the naming used in the event notification configuration to ensure proper functionality.
Subscribe to the Bucket Notification Events:
Once our Bucket Event has been successfully created we can proceed to the bucket for which we are subscribing to the events. The following screenshot subscribes a bucket named
“test”
to the
“minio-postgres-demo”
event, which will be targeted at our PostgreSQL deployment. Here you can specify any prefix or suffix as well select which type of event you want to subscribe to.
In our next screenshot of the MinIO UI we can see that the
“test”
bucket has been successfully subscribed to the “event” we created earlier.
Using the mc Command-Line Utility
The CLI-centric approach of using mc provides a robust and efficient means to integrate MinIO with PostgreSQL, enhancing the overall data workflow and management in cloud storage operations. It's particularly beneficial for those who prefer a combination of automation/scripting and manual control in managing cloud storage and data processes.
After deploying the
docker-compose.yaml
outlined above, continue by using the MinIO Client, mc, command-line utility. This setup involves creating an alias in MinIO, configuring the PostgreSQL endpoint, and setting bucket notifications.
We will be working inside of an interactive terminal for the
“minio”
container, which we can spawn by running a single command:
docker exec -it minio /bin/sh
The reason for running our mc commands from within this shell is because the Docker
minio/minio
image already has
mc
installed and ready to go.
Configure MinIO to send event notifications directly to the PostgreSQL database from within the MinIO container
Once inside the container, we have access to the mc utility, allowing us to continue with the steps to configure MinIO to send events directly to PostgreSQL.
Set up an alias for your MinIO instance. This simplifies future commands:
mc alias set myminio http://localhost:9000 minio minio123
Create the "test" bucket to monitor:
mc mb myminio/test
Configure the MinIO instance to connect to your PostgreSQL database for event notification:
mc admin config set myminio notify_postgres:minio-postgres-demo connection_string="user=myuser password=mypassword host=postgres dbname=postgres port=5432 sslmode=disable" table="events" format="namespace"
Restart the MinIO service to apply the new configuration:
mc admin service restart myminio
Set up event notifications for specific bucket operations like PUT, GET, and DELETE:
mc event add myminio/test arn:minio:sqs::minio-postgres-demo:postgresql --event put,get,delete
For more detailed instructions and information, you can refer to the MinIO documentation on
Bucket Notifications
and
Monitoring Bucket and Object Events
.
Verifying the Setup
After setting up the event notifications in MinIO and creating the necessary
"events"
table in PostgreSQL, it's crucial to verify that everything is functioning correctly, for example, that MinIO is correctly sending event data to PostgreSQL whenever there are operations (like PUT, GET, DELETE) on the specified bucket.
Let's confirm that the event data is being logged as expected.
First, create a scenario that should trigger an event notification. For example, upload a file to the MinIO bucket you've set up for notifications. This action should generate an event that will be sent to the PostgreSQL database.
Create "sample.txt" file and copy it to "myminio/test" bucket:
echo "Sample Content" > sample.txt
mc cp sample.txt myminio/test/
Exit the “docker exec” interactive shell with “exit”:
exit
Connect to your PostgreSQL container using the “docker exec postgres” to query the
events
table using psql:
docker exec postgres psql -U myuser -d postgres -c "SELECT * FROM events;"
This SQL command will display the contents of the
"events"
table. Look for the recent entry corresponding to the file upload event. The output should show a row with details about the event you triggered in MinIO. Check for fields like
"test/sample.txt"
,
"eventName"
,
"bucket"
,
"object"
,
"key"
, and any other relevant details that confirm the event was logged correctly. If you see the expected data, this confirms that MinIO is successfully sending event notifications to PostgreSQL.
If you don't see the expected event data in the PostgreSQL table, ensure that the MinIO bucket event notification is correctly set up, the PostgreSQL table schema matches what MinIO is sending, and that network connectivity between MinIO and PostgreSQL is functioning correctly.
By following these steps, you can effectively verify that your integration of MinIO with PostgreSQL is working as intended. This process is crucial to ensure that your data event management is accurate and reliable.
Data Events and Data Management
The journey through setting up and leveraging the MinIO and PostgreSQL integration showcases MinIO's robustness and versatility in handling cloud storage and data management. Whether through the graphical ease of the MinIO UI or the comprehensive control offered by the
mc
CLI, MinIO ensures that your data management strategies are not only efficient but also seamlessly integrated with modern database solutions like PostgreSQL.
As you continue to explore the capabilities of MinIO, remember that the system’s flexibility is designed to cater to a wide range of use cases and scenarios. For those looking to delve deeper into technicalities or explore more advanced configurations, the MinIO documentation on Bucket Notifications and Monitoring Bucket and Object Events is an invaluable resource. Embrace the power of MinIO and PostgreSQL to enhance your cloud storage solutions and data management practices.
Best of luck implementing these strategies in your projects, and remember, the team at MinIO is always here to support your journey in data event management!
Previous Post
Next Post
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
