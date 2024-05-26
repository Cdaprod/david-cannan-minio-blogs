# Deploying Application Infrastructure with MinIO S3 and Tailscale VPN

Deploying Application Infrastructure with MinIO S3 and Tailscale VPN
David Cannan
David Cannan
on
DevOps
10 May 2024
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
In modern IT operations, Artificial Intelligence for IT Operations (AI-Ops) is transforming data management by automating tasks with advanced algorithms. MinIO and Tailscale together offer a secure, scalable, and effective infrastructure for application-layer development. Tailscale, with its WireGuard-based overlay VPN network, provides end-to-end encryption and seamless integration with identity providers, simplifying access control for securely managing connections.
Both MinIO and Tailscale are Docker and Kubernetes native. MinIO, a perfect S3-compatible object storage solution, offers a high-performance, scalable system that seamlessly integrates into cloud-native environments. Tailscale, an ideal overlay networking solution, uses its infrastructure-agnostic VPN service to establish a secure, zero-trust network architecture, making application layer development simple and protected.
For organizations using MinIO's S3-compatible storage, Tailscale's network tunnels ensure secure access to MinIO buckets from any location, providing a protected path across the internet. The reduced latency and high reliability from Tailscale's VPN service make it particularly useful for securely linking diverse environments.
In the following sections you will learn how to deploy a MinIO server with Tailscale running as a sidecar with Docker. This configuration provides the flexibility to serve your MinIO server securely within your private network or expose it publicly through Tailscale Funnel. You'll gain insights into setting up the Tailscale sidecar to manage secure networking, configuring MinIO for optimal object storage, and how to leverage Tailscale's advanced features like Funnel to safely and efficiently route traffic, offering you full control over private and public access.
Tailscale’s Seamless Integration
Authenticating with
Tailscale VPN
enables you to generate different keys for access, such as a secret API key or an OAuth client ID and Secret. For this demonstration, we will generate an OAuth key. The use of OAuth provides a more persistent authorization, which is ideal for networking MinIO in our setup. This approach ensures a more stable and secure connection, leveraging OAuth’s robust authentication framework to manage access efficiently.
The Tailscale cert command helps obtain TLS certificates to secure your internal services through HTTPS. Here’s what you need to know:
Tailscale Cert Usage:
The tailscale cert command is used to get a TLS certificate for a specific domain within your tailnet. However, the command requires the service to be running as a node within your Tailscale network. To enable this for Docker, ensure your Tailscale container has the right permissions and is fully authenticated with an OAuth client secret or API key. The certificate will then be provisioned through the Let's Encrypt CA.
OAuth and Tags:
If using an OAuth client secret instead of an API key, the container must be correctly tagged for identification. This is set using the
TS_EXTRA_ARGS
environment variable. The OAuth approach enables automatic authentication with tailscale up, allowing your containers to obtain their certificates and operate on the network.
Contain your excitement: A deep dive into using Tailscale with Docker
.
Network Configuration:
Since we’re using
network_mode: service
, the Tailscale container should act as a sidecar, managing traffic for the MinIO container. Make sure that MinIO is configured to use Tailscale's IP range, and the
TS_SERVE_CONFIG
points to the right internal IP or DNS entry.
Using Tailscale with Docker · Tailscale Docs
.
By ensuring your Tailscale container is fully authenticated and properly configured, you should be able to serve MinIO via HTTPS successfully. Check Tailscale's blog for further details on setting up TLS certificates correctly
Provision TLS certificates for your internal Tailscale services
.
Our directory structure conveyed in the following block represents a structure where we can interact with our services and review the corresponding data for each in their respective directories
.
├── docker-compose.yaml
├── minio
│   └── data (MinIO’s Persistent Directory)
└── tailscale
    ├── config
    │   └── minio.json (Tailscale Serve’s Configuration File)
    └── state (Tailscale’s Persistent Directory)
Example Directory Structure
Environment Variables
Setting environment variables with export involves assigning values using
export VAR_NAME="value"
via the command-line so they are accessible within the current shell session. However, these variables become visible in plain text via inspection commands like ps or docker inspect. To protect sensitive data, consider secure alternatives such as encrypted vaults or secrets management services, especially for production systems.
export TS_AUTHKEY=”<auth_or_oauth_key>”

export MINIO_ROOT_USER=”<minio_root_user>”

export MINIO_ROOT_PASSWORD=”<minio_root_password>”

export TS_CERT_DOMAIN=”<tailnet-name>.ts.net”
Example Variables
To protect sensitive data, consider secure alternatives such as encrypted vaults or secrets management services, especially for production systems.
Docker Compose Setup
For deploying MinIO and Tailscale, a practical Docker Compose setup is critical for understanding how the service configurations are implemented.
The basic concept we want to convey in our Docker Compose is considering our services (which are normally isolated containers) under the guise of docker networking. By adding
network_mode: service:{name}
as a parameter within our Docker Compose file, we then can specify the Tailscale service’s hostname and encapsulate them together.
Here’s an example configuration that emphasizes Tailscale’s integration and security:
docker-compose.yaml
version: '3.8'
services:
  minio-ts:
    hostname: minio-ts
    container_name: minio-ts
    image: tailscale/tailscale:latest
    environment:
      - TS_AUTHKEY=${TS_AUTHKEY}?ephemeral=false
      - TS_STATE_DIR=/var/lib/minio-ts
      - TS_SERVE_CONFIG=/config/minio-serve-config.json
      - TS_EXTRA_ARGS=--advertise-tags=tag:infra 
    volumes:
      - /dev/net/tun:/dev/net/tun
      - ${PWD}/tailscale/state:/var/lib/tailscale
      - ${PWD}/tailscale/config:config
    cap_add:
      - net_admin
      - sys_module
    restart: unless-stopped

  minio:
    image: minio/minio:latest
    container_name: minio
    environment:
      - MINIO_ROOT_USER=${MINIO_ROOT_USER}
      - MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}
    command: server /data --address ":9000" --console-address ":9001"
    volumes:
      - ${PWD}/minio/data:/data
    restart: unless-stopped
    depends_on: minio-ts
    network_mode: service:minio-ts

volumes:
  minio-ts:
    local
  minio:
    local
docker-compose.yaml
Docker Compose “network_mode” Parameter
By setting
network_mode: service:minio-ts
, we can effectively place our container in the network namespace of another container, specifically the one named in minio-ts. This means the container inherits the network stack of the target service, including IP addresses and port settings.
In our example, minio will share the network stack of the
minio-ts
service, allowing it to communicate over the Tailscale network without additional network configuration.
Serving and Funneling MinIO with Tailscale
Tailscale’s Serve and Funnel features simplify the traditional complexities associated with exposing services across networks.
Serve
allows internal services to be accessible within your Tailscale network, streamlining how you connect to resources like development servers without complex configurations.
Funnel
extends this accessibility to the internet, offering a secure way to expose services externally without direct exposure, protecting them behind Tailscale’s robust security measures.
This integration dramatically simplifies operations, reducing the need for traditional reverse proxies and manual SSL management, making network management more secure and manageable.
Let’s Encrypt with Tailscale
To enable the Tailscale HTTPS proxying feature for your MinIO service, the tailscale cert command is essential. It helps obtain TLS certificates through Let's Encrypt, ensuring that your MinIO instance can be securely accessed over HTTPS. Here are the steps you'll need to follow:
Admin Console Setup
In the Tailscale admin console, enable HTTPS certificates and ensure
MagicDNS
is active. This will link your tailnet's name to the certificates
Enabling HTTPS · Tailscale Docs
.
To generate a TLS certificate for MinIO, the tailscale cert command requires access to the environment that is running Tailscale. However, since your MinIO container uses
network_mode: service:minio-ts
, it's effectively sharing the network stack of the
minio-ts
container.
Docker Exec into Tailscale’s Service
Exec into the Tailscale Container
Access the Tailscale environment by using the Docker exec command. This will allow you to interact directly with the Tailscale CLI in the container.
Run this command to access the Tailscale container:
docker exec -it minio-ts /bin/sh
Generate the Certificate
Once inside the Tailscale container, use the tailscale cert command to generate a certificate for the MinIO service. Be mindful that the hostname remains consistent and does not change, as this might affect certificate matching
Tailscale + Fly + SSL - Tailscale
.
To generate a TLS certificate using tailscale cert, you will need to run the command specifying the precise domain name without using wildcards. Here’s an example command:
tailscale cert <subdomain>.<service-hostname>.<your-tailnet.ts.net>
Example command:
tailscale cert minio-ts.tailnet.ts.net
Example command to generate certificate.
Ensure that the domain name matches the DNS name within your tailnet.
Important Notes
TLS Certificate:
Make sure that the generated certificate is then used by your MinIO service.
Permissions:
Ensure that the Tailscale service has appropriate permissions set up via API key or OAuth to create the certificates.
Configure the MinIO Container
In your
TS_SERVE_CONFIG
(
minio.json
), ensure that the proxy settings align with your MinIO container's internal ports, typically 9000 or 9001. Make sure that the Tailscale service and MinIO are correctly linked via networking.
Tailscale simplifies network configurations using the
TS_CERT_DOMAIN
variable (this is knows as the “tailnet”) in the sample
TS_SERVE_CONFIG
JSON file, which automates TLS certificate issuance for domains managed by Tailscale’s HTTPS proxying feature. This eliminates the need for traditional proxies like Nginx for SSL/TLS termination, streamlining secure communications setup.
TS_SERVE_CONFIG
{
    "TCP": {
        "443": {
            "HTTPS": true
        }
    },
    "Web": {
        "minio.{TS_CERT_DOMAIN}:443": {
            "Handlers": {
                "/": {
                    "Proxy": "http://127.0.0.1:9001"
                }
            }
        }
    },
    "AllowFunnel": {
        "minio.{TS_CERT_DOMAIN}:443": false
    }
}
Example TS_SERVE_CONFIG - JSON file
The
TS_SERVE_CONFIG
file provided above effectively demonstrates how to configure Tailscale to serve a local web service, such as a MinIO instance, over HTTPS through Tailscale's secure networking infrastructure. Here’s a breakdown of the Tailscale Serve configuration:
TCP Block
This section indicates that TCP port 443 (which is standard for HTTPS traffic) is set up to handle HTTPS traffic. This setup is crucial for encrypting the data transmitted between clients and the server.
Web Block
The
"minio.{TS_CERT_DOMAIN}:443"
entry specifies that requests to this domain at port 443 are to be handled by the defined rules within.
The
"Handlers"
section contains paths and corresponding actions. Here, the root path ("/") is configured to proxy requests to
http://127.0.0.1:9001
, which should be the local address where your MinIO console service is running. This redirection allows Tailscale to securely expose the local service as if it were running directly on the specified domain.
AllowFunnel Block:
This setting controls whether the service can be accessed via Tailscale’s Funnel feature, which makes local services available on the internet. The setting
"minio.{TS_CERT_DOMAIN}:443": false
explicitly denies internet-wide exposure for the service, restricting it to Tailscale network access only.
If you are publicly exposing your server to the web then set
“AllowFunnel”
to
true
.
Tailscale Funnel
extends the accessibility of local services to the public internet allowing for the creation of
DNS Records via Cloudflare
, creating secure and encrypted pathways for services like webhooks or web apps, directly from your hardware. The AllowFunnel setting in Tailscale’s configuration enables this feature, ensuring services are both accessible and secure according to your network policies.
Limitations of Funneling
Tailscale Funnel has specific limitations that impact its usage.
First, DNS names are restricted to the tailnet's domain, meaning each node is only accessible via a DNS name like
node-name.tailnet-name.ts.net
.
Second, Funnel can only listen on ports 443 (standard HTTPS), 8443, and 10000. Third, it exclusively works over TLS-encrypted connections, ensuring that all traffic routed through Funnel remains securely encrypted.
Additionally, traffic routed through Funnel is subject to bandwidth limits, which are currently non-configurable. Lastly, on macOS, due to app sandbox limitations, file and directory serving is limited to the open-source variant of Tailscale. Further details about Tailscale Funnel's limitations and usage can be found in
Tailscale's official documentation
.
Review Security Settings
It is essential to always double-check that Tailscale's settings and MinIO's security parameters are configured to align with your organization's security standards.
For further details on enabling HTTPS certificates in Tailscale, consult the official documentation
Provision TLS certificates for your internal Tailscale services
.
Integrating Tailscale with MinIO enhances your data security further, ensuring that every access to your storage buckets is authenticated and encrypted, aligning with the best practices in cybersecurity.
Implementing MinIO with Tailscale simplifies secure networking but requires precise configuration. Challenges like enabling consistent access across teams, maintaining certificate validity, and balancing public/private exposure are solved with Tailscale's features:
Funnel allows controlled public exposure of services, enabling secure access from the internet without complex firewall configurations.
OAuth integration provides a unified authentication mechanism, ensuring consistent access control across teams and environments.
API keys enable programmatic management of Tailscale settings, automating tasks like certificate renewal to maintain validity.
Proper configuration of these features helps ensure seamless integration and reliable operation of the MinIO-Tailscale setup.
Best Practices
Authentication
Use OAuth keys for persistent authorization to enable stable, long-term access.
Manage sensitive credentials like API keys and OAuth secrets via secure vaults or secrets management systems.
Regularly rotate and update credentials to maintain security and prevent unauthorized access.
Network Configuration
Review Tailscale's IP range and ensure it aligns with MinIO's network settings for proper connectivity.
Maintain the TS_SERVE_CONFIG file to handle traffic routing efficiently and securely.
Use meaningful, standardized naming conventions for Tailscale devices and subnets to keep the network organized and manageable as it scales.
Load Balancing
Implement Tailscale's access control rules to distribute network load effectively across nodes, ensuring reliable performance.
Monitor network traffic and resource usage with tools like Prometheus or Grafana to identify bottlenecks and optimize load balancing settings.
Regularly review and adjust load balancing configurations to adapt to changing usage patterns and maintain a responsive user experience.
Overlay Networking with Tailscale
By combining MinIO's high-performance, S3-compatible object storage with Tailscale's secure, zero-trust networking, organizations can create a powerful and flexible foundation for their initiatives. This setup enables businesses to securely manage and analyze operational data across diverse environments, from on-premises data centers to public cloud platforms.
The seamless integration of MinIO and Tailscale, along with their cloud-native architecture and robust feature sets, empowers teams to harness the full potential of application layer operations. With streamlined data access, granular control over network policies, and strong encryption built-in, this infrastructure stack provides the performance, security, and scalability needed to support the most demanding workloads.
As object-storage continues to evolve and mature, the MinIO-Tailscale combination offers a future-proof foundation for innovation. By adopting best practices around authentication, network configuration, and load balancing, organizations can ensure their infrastructure remains reliable, efficient, and secure as they navigate the challenges and opportunities ahead.
Whether you're just starting your AI development journey or looking to optimize your existing setup, deploying MinIO with Tailscale is a smart choice. With the right configuration and a commitment to operational excellence, this powerful duo can help you unlock the full value of your data and drive success in the era of intelligent, automated IT operations.
For additional support or to connect with the community, feel free to join the conversation in the
MinIO Slack
channel, where experts share insights and answer questions about deploying, managing, and optimizing MinIO.
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
