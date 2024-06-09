# Deploying Application Infrastructure with MinIO S3 and Tailscale VPN

![Header Image](articles/images/Deploying_Application_Infrastructure_with_MinIO_S3_and_Tailscale_VPN.jpg)

Deploying Application Infrastructure with MinIO S3 and Tailscale VPN
David Cannan
David Cannan
on
DevOps

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
