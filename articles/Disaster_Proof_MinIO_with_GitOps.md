# Disaster Proof MinIO with GitOps

Disaster Proof MinIO with GitOps
David Cannan
David Cannan
on
DevOps
19 March 2024
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
Imagine you've spent countless hours perfecting your
Docker Swarm setup
, carefully crafting each service, and tuning your CI/CD pipelines for seamless automation. Now, picture this finely tuned system being reset to square one, not by a critical failure or a security breach, but by the innocent curiosity of a datacenter engineer pressing the magical
"factory reset"
on hardware. This is not the opening of a DevOps horror story, but rather a testament to the resilience and rapid recovery enabled by a well-designed repository and the principles of GitOps.
In this article, we will delve into how automation and redundancy, which are at the heart of DevOps, proved to be the saviors in a situation where a reset could have spelled disaster. I will share how a combination of Docker, GitHub Actions, and MinIO, coupled with an unexpected real-world trial, underscored the importance of a reliable and repeatable build and deployment process.
Through this experience, we will explore the power of version-controlled configurations and the foresight to push images to multiple registries, ensuring that even in the face of a complete system wipe, recovery is but a few commands away. Join me as we explore the depths of resilience in DevOps, illustrating how you, too, can armor your systems against the surprises life might throw your way.
Screenshot - Figure 1: Docker’s factory reset dialog box
The Importance of Redundancy and Automation
Redundancy and automation serve as foundational pillars in modern DevOps practices, essential for maintaining continuity and ensuring high availability. The strategic decision to dual-push Docker images to both
Docker Hub
and the
GitHub Container Registry
(GHCR.io) was driven by a calculated approach to risk management and accessibility.
Docker Hub
, as the primary artifact registry, offers extensive integration and public visibility, which is used for broad distribution and collaboration. It stands as the go-to registry for immediate artifact retrieval and deployment. However, relying on a single registry is a vulnerability; any service disruption can halt deployments and updates, leading to potential downtime.
In contrast,
GHCR.io
provides a secure, private storage solution for Docker images by default, aligning with the need for controlled access to certain deployment artifacts. This registry becomes a strategic backup, ensuring that even if Docker Hub is compromised or becomes unavailable, there's an immediate fallback option without any disruption to the CI/CD pipelines.
The automation of image pushes to both registries via GitHub Actions. It ensures that the latest builds are always available for deployment from either source, effectively safeguarding against service interruptions. This methodical redundancy is not about creating unnecessary copies but about preparing for contingencies with minimal recovery time.
Building on GitHub, where the repositories reside, the logic behind pushing to both registries concurrently is straightforward: It provides a seamless, automated way to maintain a private backup of all images while keeping the public registry up-to-date. This dual approach is a proactive measure—a well-designed DevOps process must include strategic redundancy at its core.
Repo Enhancements for Resiliency
In pursuit of a resilient DevOps environment, continuous improvement is crucial. The enhancements made to the original repository were both reflective and preemptive, aimed at not just addressing the recovery needs but also at streamlining the process for any future deployment needs.
First, the workflow configurations underwent refinement, with each job and step defined to ensure efficiency and reliability. To this end, the
.github/workflows
directory was enriched with new workflows for multi-platform builds, which extended the automation capabilities of the repository. This setup not only facilitates consistent deployments but also ensures that the latest versions of applications are ready to be pulled from either Docker Hub or GHCR.io.
Screenshot - Figure 2: Screenshot of the GitHub repository created to prioritize CI/CD in my local environment
In the
cda-deploy-to-swarm
repository, the structure was carefully crafted to enable quick navigation and ease of use. The directory includes:
The .github/workflows folder, which houses the CI/CD automation scripts. Here, YAML files define the actions that run on pushes and pull requests, encompassing the build and push operations as well as the deployment orchestration.
The minio directory contains the custom configurations and Docker Compose files tailored for the MinIO service, allowing for a swift and standardized setup of object storage capabilities.
The nginx directory is set up with configurations for deploying the NGINX web server, instrumental for handling HTTP requests and serving as a reverse proxy.
The weaviate directory, which includes the necessary elements to deploy the Weaviate vector search engine, leveraging Docker Compose for service definition and deployment.
Central to the repository's root is the
docker-compose.yaml
file, which defines the multi-container application services and ties the individual components together in a cohesive whole.
Each improvement and structural decision was made with the goal of creating a repository that not only bounces back from disruptions but also serves as a modular, scalable foundation for deploying services within a Docker Swarm environment. The clarity and organization of the repository's structure are instrumental in this, allowing for quick identification of components and configurations, thereby reducing recovery time and facilitating efficient management of the deployment process. For details on the specific files mentioned throughout this article, visit the MinIO
blog-assets
repository.
Efficient CI/CD with GitHub Actions and Docker Compose
Within our DevOps workflow, GitHub Actions play a pivotal role in automating the build process of our Docker images, including our custom MinIO and Weaviate services. These actions are configured to trigger on specific events, such as a push to the main branch, ensuring that every change is seamlessly integrated into our deployment pipeline.
Here’s how the process unfolds:
GitHub Actions Workflow:
Upon a commit to the repository, our GitHub Actions workflows are initiated. These workflows contain jobs to build Docker images using our custom Dockerfiles and push them to the registries. These images are tagged appropriately, for instance,
cdaprod/cda-minio:latest
.
Docker Compose for Deployment:
Following the build and push process, the
docker-compose.yaml
file comes into play for deployment. It is configured to pull the latest images from the registry for service deployment within the Docker Swarm environment.
The
docker-compose.yaml
file contains service definitions like this:
version: '3.8'

services:
  minio:
    image: cdaprod/cda-minio:latest
    # Other configurations ...

 weaviate:
    image: cdaprod/cda-weaviate:latest
    # Other configurations ...

 nginx:
    image: cdaprod/cda-nginx:latest
    # Other configurations ...

networks:
  app_network:
    driver: overlay

# Other definitions like volumes and secrets…
This approach significantly simplifies our deployment strategy by decoupling the image building and service deployment processes. It also means we do not need multiple docker-compose files for different environments or scenarios.
By utilizing this CI/CD strategy, we are able to maintain a single source of truth for our service definitions and ensure that our deployment process is as streamlined and efficient as possible. Our deployment becomes a matter of a self-hosted runner, executing a
docker-compose up command
from our GitHub Actions Workflow, with Docker Compose handling the rest—pulling the latest images, starting up the services, and ensuring they are configured exactly as we have defined.
Illustrating Custom Image Builds with MinIO
To further elucidate our CI/CD pipeline’s build process, let’s take a closer look at the customization of our MinIO service image. Our GitHub Actions workflows are responsible for building this image, based on the official
minio/minio:latest
, with additional configurations tailored to our requirements.
Here’s the
/minio/Dockerfile
that outlines the build steps:
# Start with the official MinIO image as a base
ARG BASE_IMAGE=minio/minio:latest
FROM $BASE_IMAGE


# Copy over the custom entrypoint script
COPY entrypoint.sh /entrypoint.sh
# Ensure the script is executable
RUN chmod +x /entrypoint.sh


# Expose the ports MinIO will use
EXPOSE 9000 9001


# Use the custom entrypoint script to start MinIO
ENTRYPOINT ["/entrypoint.sh"]
Builds MinIO container, configuring it via an entrypoint bash script
Enhancing Customization with an Entrypoint Script
The customization process doesn’t end with the
Dockerfile
. To fully tailor our MinIO service to our operational needs, we leverage an
entrypoint.sh
script. This script acts as the command center at container startup, executing predefined commands that configure the MinIO instance beyond its default settings.
The beauty of using an
entrypoint.sh
script lies in its ability to perform runtime configurations. These are crucial for setting up our environment dynamically, ensuring that our MinIO service is not just a vanilla deployment but one that is customized for our use case.
This approach of combining a
Dockerfile
with an
entrypoint.sh
script allows us to construct containers that are not just built with our applications and services in mind but are also ready to operate within our unique ecosystem the moment they are deployed.
#!/bin/sh
set -e

# Start MinIO in the background
minio server /data --console-address ":9001" &

# Wait for the MinIO server to start
sleep 5

# Configure MinIO with the mc (MinIO Client) tool
mc alias set myminio http://localhost:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

# Before creating buckets, check if they already exist
if ! mc ls myminio/weaviate-backups; then
  mc mb myminio/weaviate-backups
fi

if ! mc ls myminio/cda-datasets; then
  mc mb myminio/cda-datasets
fi

# Keep the container running
tail -f /dev/null
Starts MinIO Console, sets mc alias, and create buckets if not found
The
Dockerfile
specifies the official MinIO image as the base and then adds our custom
entrypoint.sh
script. This script is crucial as it runs additional commands to configure MinIO after it starts, such as creating necessary buckets using the MinIO Client (
mc
).
During the image build phase triggered by our workflows, we use this
Dockerfile
to create a
cdaprod/cda-minio:latest
image. This image encapsulates our custom settings and scripts, which the
docker-compose.yaml
file will later use to deploy the MinIO service in our Docker Swarm.
The distinction between
minio/minio:latest
and
cdaprod/cda-minio:latest
is minimal. While the former is the unaltered base image from MinIO’s official Docker Hub repository, the latter is our customized version, built and maintained through our CI/CD workflows, ensuring that any specific configurations and scripts are baked into the image we deploy.
Deep Dive into Workflows
Two GitHub Actions workflows, Build and Push Docker Images and Deploy Services, constitute the core automation mechanism in the repository. Here's an expanded explanation of each.
Build and Push Docker Images Workflow
This workflow is triggered on any push or
pull_request
to the
main
branch to ensure that the latest code commits result in updated Docker images.
name: Build and Push Docker Images

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}

    - name: Build and push custom MinIO image
      uses: docker/build-push-action@v3
      with:
        context: ./minio
        file: ./minio/Dockerfile
        push: true
        tags: cdaprod/cda-minio:latest
        platforms: linux/amd64,linux/arm64

    - name: Build and push custom Weaviate image
      uses: docker/build-push-action@v3
      with:
        context: ./weaviate
        file: ./weaviate/Dockerfile
        push: true
        tags: cdaprod/cda-weaviate:latest
        platforms: linux/amd64,linux/arm64
Builds containerized images and pushes to Docker Hub
The job build-and-push executes on the latest Ubuntu runner provided by GitHub Actions. The workflow comprises of the following steps:
Checkout code:
The
actions/checkout@v3
action is used to clone the repository so that the workflow can access its contents.
Setup Docker Buildx:
The
docker/setup-buildx-action@v2
is employed to install and configure Buildx, which extends Docker with the ability to build multi-platform images, more advanced build metrics, and different output options while leveraging Docker's buildkit library.
Login to Docker Hub:
This step logs into Docker Hub using the
docker/login-action@v2
, referencing
DOCKERHUB_USERNAME
and
DOCKERHUB_TOKEN
secrets for authentication. These secrets are securely stored in the repository settings and not exposed in the workflow file.
Build and push custom MinIO image:
Utilizes
docker/build-push-action@v3
to build the MinIO image from the specified
Dockerfile
within the minio context directory. It is tagged and then pushed to Docker Hub, ensuring the image is available for deployment. The platforms argument specifies the CPU architectures the image should support, ensuring compatibility across different hardware setups.
Build and push custom Weaviate image:
Similarly, this step is for building and pushing the Weaviate image with appropriate tagging and multi-architecture support.
Screenshot - Figure 3: Successful Build and Push Docker Images Workflow Execution.
Deploy Services Workflow
This deployment workflow is required for the “continuous deployment” aspects of the CI/CD pipeline, kicking into action when the
Build and Push Docker Images
workflow completes successfully on the main branch.
name: Deploy Services

on:
  workflow_run:
    workflows: ["Build and Push Docker Images"]
    branches: [main]
    types:
      - completed
  workflow_dispatch:

jobs:
  deploy:
    runs-on: self-hosted
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Docker Hub
        uses: docker/login-action@v1
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Deploy to Docker Swarm
        run: |
          docker stack deploy -c docker-compose.yaml cda_stack
Deploys using docker-compose.yaml after successful “Build and Push Docker Images” workflow
Checkout Repository:
Similar to the build workflow, it starts by checking out the code.
Setup Docker Buildx:
Though Buildx setup is not utilized for deployments, it's included for consistency and future use if multi-node builds become necessary in the stack deployment process.
Log in to Docker Hub:
Secures a login to Docker Hub to ensure that the runner can pull the required images for deployment without any hitches.
Deploy Application Stack:
This crucial step uses the single
docker-compose.yaml
to deploy the complete application stack. It combines service definitions and configurations for MinIO, Weaviate, and NGINX into one unified deployment command. Environment variables and secrets are managed securely within GitHub secrets.
The deploy workflow turns the code changes into live services, with handling sensitive data through GitHub secrets. It showcases the ability to deploy complex service stacks, adhering to the principles of infrastructure as code, and it's designed to evolve as the application infrastructure grows.
Screenshot - Figure 4: showcases the Deploy Services workflow’s successful activation, following the build process.
Screenshot - Figure 4 showcases the passing Status Badges of the workflow’s, following the build processes and deployment.
A Proactive Approach to DevOps Resilience
In the world of DevOps, the robustness of a system is often only highlighted during times of crisis. A recent event demonstrated the strength embedded within our practices; a system-wide reset inadvertently initiated, bringing down all running services. Far from a catastrophe, this became a prime opportunity to validate the resilience of the infrastructure we advocate for at MinIO.
Crafted with foresight, our repository's structure utilized Docker Compose and GitHub Secrets to orchestrate our service environment. This strategic setup simplified the restoration process, transforming what could have been a complex recovery into a series of simple, automated steps:
Initialization:
Our self-hosted runner, already configured for such contingencies, was initiated, establishing the foundation for recovery.
Synchronization:
The latest service code was fetched directly from our repository, guaranteeing that only the most current configurations were in play.
Configuration:
Environment variables, securely stored as GitHub Secrets, were seamlessly integrated, bypassing the need for manual setup.
Orchestration:
The deployment of services was automated through a Docker Compose execution, led by a GitHub Actions workflow, reinstating the full suite of services with precision.
In this demonstration of IaC, our services were restored to their operational state swiftly, underlining the efficacy of our DevOps methodologies.
Key Insights for Building Resilient Systems
The swift recovery from an unexpected system reset underscores several insights integral to modern software development and deployment:
Automation is Paramount:
Automating recovery processes minimizes downtime and eliminates human error, allowing for a swift and sure response to system failures.
Unified Source of Truth:
GitOps consolidates infrastructure and application management, streamlining change tracking and enabling effortless rollbacks when necessary.
Designing for Durability:
Resilience in infrastructure is intentional, crafted through diligent planning and implementation of CI/CD and IaC best practices.
At MinIO, these principles are not just theoretical—they are practical measures embedded in our workflow, ensuring that our systems and services are resilient by design. For developers and DevOps professionals, the message is clear:
investing in these practices is investing in the future stability and success of your infrastructure
. Our collective experience speaks volumes about our capacity to manage disruptions with grace and efficiency.
By codifying our infrastructure and treating it with the same care and attention as our application code, we can dramatically reduce the time and effort required to rebuild and redeploy our services in the face of disasters. Moreover, we have emphasized the importance of thorough documentation and regular, automated backups. While a strong CI/CD pipeline can facilitate rapid recovery, it is not a substitute for maintaining comprehensive documentation and reliable backups of our code, configuration, and data.
Reach out to us on
Slack
and drop us a message. Let’s continue this conversation together!
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
