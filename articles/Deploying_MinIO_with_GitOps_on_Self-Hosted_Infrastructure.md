# Deploying MinIO with GitOps on Self-Hosted Infrastructure

![Header Image](articles/images/Deploying_MinIO_with_GitOps_on_Self-Hosted_Infrastructure.jpg)

Deploying MinIO with GitOps on Self-Hosted Infrastructure
David Cannan
David Cannan
on
DevOps

# Download the runner package
curl -o actions-runner-linux-arm64-<RUNNER_VERSION>.tar.gz -L <https://github.com/actions/runner/releases/download/v><RUNNER_VERSION>/actions-runner-linux-arm64-<RUNNER_VERSION>.tar.gz

# Extract the runner package
tar xzf ./actions-runner-linux-arm64-<RUNNER_VERSION>.tar.gz

# Configure the runner
./config.sh --url <https://github.com/><GITHUB_USERNAME>/<GITHUB_REPO> --token <GITHUB_TOKEN>
Example of code provided by GitHub
Make sure to ensure
<RUNNER_VERSION>
,
<YOUR_USERNAME>
,
<YOUR_REPO>
, and
<YOUR_TOKEN>
with the actual version number, your GitHub username, your repository name, and the token provided by the GitHub UI, respectively.
Interactive Test Run
Initially, start the runner using the provided script to confirm its successful setup and readiness to process jobs.
# Start the runner interactively

./run.sh
Execute run script
Executing ./run.sh command
These commands establish the connection between the self-hosted runner and the GitHub repository, setting the stage for executing CI/CD workflows directly from the Docker Swarm leader.
Creating a Systemd Service for the Runner
With the runner configured, the next step is to operationalize it, ensuring it can handle workflow executions seamlessly. Starting the runner interactively tests its functionality, while creating a Systemd service ensures its persistence and resilience.
Example github-runner.service file
1. Create the Systemd Service File
This step involves creating a systemd service file to manage the GitHub Actions runner as a service, ensuring it starts automatically and remains running.
Create a new service file using your preferred text editor, like nano or vim:
sudo nano /etc/systemd/system/github-runner.service
Creating service file
Insert the following content, adjusting paths as necessary:
[Unit]
Description=GitHub Actions Runner
After=network.target

[Service]
ExecStart=/home/<USER>/action-runner/run.sh
User=<USER>
WorkingDirectory=/home/<USER>/action-runner
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
Example service file contents
Replace
<USER>
with the username of the account under which you've installed the runner.
2. Enable and Start the Service
After saving and closing the service file, reload systemd to recognize the new service, enable it to start at boot, and then start the service immediately:
sudo systemctl daemon-reload
sudo systemctl enable github-runner.service
sudo systemctl start github-runner.service
3. Verify the Service Status
To ensure the GitHub Actions runner service is active and running, execute the following command:
sudo systemctl status github-runner.service
Successful creation of github-runner.service
You should see output indicating that the service is active. If there are any issues, the output will also include error messages that can help in troubleshooting.
Successful connected self-hosted runner
From the GitHub Actions tab, select the Runners tab, this will bring up two “tabs”. Select Self-hosted runners to view your configured Repository runner.
Deploying MinIO on Docker Swarm with Self-Hosted Runner
When adapting GitHub Actions workflows for execution on a self-hosted runner, particularly one tailored for a Docker Swarm infrastructure like "rpi-swarm", it is essential to design the workflow to leverage the unique environment fully. This means not just running tests, but also deploying real applications like MinIO, a high-performance distributed object storage server. Below is an example of how to configure a GitHub Actions workflow to deploy MinIO on your "rpi-swarm" runner, demonstrating the runner's capability to handle more complex CI/CD tasks like deploying services with the use of Docker and Docker Compose.
Create a file in your repository under
.github/workflows
directory, for example,
.github/workflows/deploy-minio-on-rpi-swarm.yml
, and insert the following workflow configuration:
name: Deploy MinIO on RPI Swarm

on:
push:
branches:
- main
pull_request:

jobs:
deploy-minio:
name: Deploy MinIO to RPI Swarm
runs-on: [self-hosted, rpi-swarm]

steps:
- name: Check out repository code
uses: actions/checkout@v2

- name: Load Docker Compose File
run: |
echo "Loading Docker Compose for MinIO Deployment..."
docker-compose -f docker-compose.yml config

- name: Deploy MinIO Stack
run: |
echo "Deploying MinIO on RPI Swarm..."
docker stack deploy -c docker-compose.yml minio_stack

- name: Verify Deployment
run: |
echo "Verifying MinIO Deployment..."
docker service ls | grep minio_stack
This workflow exemplifies how to utilize a GitHub Actions self-hosted runner for deploying applications like MinIO to a Docker Swarm setup, demonstrating the runner's ability to facilitate complex CI/CD tasks beyond simple tests.
name:
Identifies the workflow, here named "Deploy MinIO on RPI Swarm".
on:
Defines the trigger events for the workflow, set to activate on pushes to the
main
branch and on pull requests.
jobs:
Contains the jobs to be executed by the workflow, with a single job named "deploy-minio" in this example.
runs-on:
Directs the job to execute on your self-hosted runner tagged with "rpi-swarm", ensuring the workflow leverages the specific environment of your Docker Swarm.
steps:
Lists the sequence of operations the job will perform:
Check out repository code:
Fetches the codebase onto the runner using
actions/checkout@v2
.
Load Docker Compose File:
Prepares the Docker Compose file for deployment, useful for verifying the file's syntax and outputting the effective configuration.
Deploy MinIO Stack:
Utilizes Docker Compose to deploy MinIO as a stack to the Docker Swarm, showcasing the self-hosted runner's capability to handle Docker Swarm deployments.
Verify Deployment:
Confirms the MinIO stack deployment by listing Docker services and filtering for the MinIO stack, ensuring that the deployment was successful.
Elevating Deployment Practices with MinIO and GitOps
Underscoring MinIO’s dedication to refining storage solutions for contemporary applications, merging seamlessly with the evolution brought about by GitHub self-hosted runners in the CI/CD arena. Embracing GitOps principles places MinIO at the vanguard of a strategic pivot towards more self-reliant, secure, and efficient deployment workflows, significantly enhancing the developer experience.
The flexibility that GitOps introduces into application development is another sphere where MinIO’s capabilities shine brightly. Developers find themselves well-equipped to refine application layers and deploy microservices with assurance, utilizing MinIO for streamlined data storage and management. This structured and automated method accelerates development, fortifying the resilience and scalability of applications. The incorporation of GitHub Actions and self-hosted runners smoothens the deployment across various settings, fully leveraging MinIO’s object storage strengths.
We encourage our fellow developers and engineers to dive into this journey with us, explore the potentials, and share their insights and queries. For deeper conversations, collaborations, or queries, feel free to reach out to us on the
