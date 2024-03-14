# Innovating S3 Bucket Retrieval: Langchain Community S3 Loaders with OpenAI API






Innovating S3 Bucket Retrieval: Langchain Community S3 Loaders with OpenAI API


































































 


Customer Login





Product




MinIO Enterprise Object Store
Overview
Features


Replication
Encryption
Object Immutability
Identity + Access Mgt
Information Lifecycle
Versioning
Key Management Server


Console
Catalog
Firewall
Cache
Observability
S3 Compatibility




MinIO for Public Cloud

                            AWS
                        

                            GCS
                        

                            Azure
                        
MinIO for Private Cloud

                            OpenShift
                        

                            SUSE Rancher
                        

                            Tanzu
                        
MinIO for Baremetal

                            Linux and Windows
                        




                            Erasure Code Calculator
                        


                            Reference Hardware
                        






Solutions




AI Storage
Object storage is powering the AI revolution. Learn how MinIO
                    is leading the AI storage market through performance at
                    scale.


Modern Datalakes
Modern, multi-engine datalakes depend on object stores that
                    deliver performance at scale. Learn more about this core MinIO
                    use case.


Hybrid Cloud
Effective multi-cloud storage strategies rely on utilizing
                    architecture and tools that can function seamlessly across
                    diverse environments.


Splunk
Find out how MinIO is delivering performance at scale for
                    Splunk SmartStores.


Snowflake
Query and analyze multiple data sources, including streaming
                    data, residing on MinIO with the Snowflake Data Cloud. No need
                    to move the data, just query using SnowSQL.


SQL Server
Discover how to pair SQL Server 2022 with MinIO to run queries
                    on your data on any cloud - without having to move it.


HDFS Migration
Modernize and simplify your big data storage infrastructure
                    with high-performance, Kubernetes-native object storage from
                    MinIO.


VMware
Discover how MinIO integrates with VMware across the portfolio
                    from the Persistent Data platform to TKG and how we support
                    their Kubernetes ambitions.


Veeam
Learn how MinIO and Veeam have partnered to drive performance
                    and scalability for a variety of backup use cases.


Commvault
Learn how Commvault and MinIO are partnered to deliver
                    performance at scale for mission critical backup and restore
                    workloads.


Integrations
Browse our vast portfolio of integrations.






Community




GitHub
Join our GitHub open source community: explore, experiment, ask questions, and contribute.


Slack Channel
The MinIO Community Slack provides an open forum for discussing topics related to MinIO. All support is provided on a best-effort basis.





Docs


Blog


Resources


Training


Partner


Pricing

Download

 












    Search

    


Topics

All
Architect's Guide
Operator's Guide
Best Practices
AI/ML
Modern Data Lakes
Performance
Kubernetes
Integrations
Benchmarks
Security
Multicloud






Try the ErasureCode Calculatorto configure yourusable capacity
Try Now


 



Innovating S3 Bucket Retrieval: Langchain Community S3 Loaders with OpenAI API



                David Cannan
                

        David Cannan
        


 

    on
        AI/ML
30 January 2024
 





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
        



In the rapidly evolving world of data storage and processing, combining efficient cloud storage solutions with advanced AI capabilities presents a transformative approach to handling vast volumes of data. This article demonstrates a practical implementation using MinIO, Langchain and OpenAI’s GPT-3.5 model, focusing on summarizing documents stored in MinIO buckets.The Power of MinIOMinIO is open-source, high-performance object storage that is fully compatible with the Amazon S3 API. Known for its scalability, MinIO is ideal for storing unstructured data such as photos, videos, log files, backups and container images. It’s not just about storage; MinIO also offers features like data replication, lifecycle management and high availability, making it a top choice for modern cloud-native applications.Integrating Langchain and OpenAILangchain, a Python-based tool, facilitates the interaction between document loaders and AI models. In our use case, we combine Langchain with OpenAI’s gpt-3.5-turbo-1106 model to summarize documents from MinIO buckets. This setup exemplifies how AI can extract essential information from extensive data, simplifying data analysis and interpretation. For additional information and supporting materials related to this article such as notebooks and loaded documents, please visit the MinIO Github repository in the langchain-s3-minio directory.Installing LangchainBefore diving into the implementation, ensure you have Langchain installed. Install it via pip:pip install --upgrade langchain

This will encapsulate all the required libraries we will be using for our S3 loaders and OpenAI model.Step 1: Langchain S3 Directory and File LoadersInitially, we focus on loading documents using Langchain's S3DirectoryLoader and S3FileLoader. These loaders are responsible for fetching multiple and single documents from specified directories and files in MinIO buckets.MinIO Configurations and Langchain S3 File Loaderfrom langchain_community.document_loaders.s3_file import S3FileLoader

# MinIO Configuration for the public testing server
endpoint = 'play.min.io:9000'
access_key = 'minioadmin'
secret_key = 'minioadmin'
use_ssl = True

# Initialize and load a single document
file_loader = S3FileLoader(
    bucket='web-documentation',
    key='MinIO_Quickstart.md',
    endpoint_url=f'http{"s" if use_ssl else ""}://{endpoint}',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    use_ssl=use_ssl
)

document = file_loader.load()Python Langchain Example - S3 File LoaderLangchain S3 Directory Loader:from langchain_community.document_loaders.s3_directory import S3DirectoryLoader

# Initialize and load documents
directory_loader = S3DirectoryLoader(
    bucket='web-documentation',
    prefix='',
    endpoint_url=f'http{"s" if use_ssl else ""}://{endpoint}',
    aws_access_key_id=access_key, 
    aws_secret_access_key=secret_key, 
    use_ssl=use_ssl
)

documents = directory_loader.load()Python Langchain Example - S3 Directory LoaderStep 2: Summarizing with OpenAIAfter loading the documents, we use OpenAI's GPT-3.5 model (which are included in the Langchain library via ChatOpenAI) to generate summaries. This step illustrates the model's capability to understand and condense the content, providing quick insights from large documents. To access the OpenAI API, you can acquire an API key by visiting the OpenAI platform. Once you have the key, integrate it into the code below, to harness the power of GPT-3.5 for document summarization.Code Example for Document Summarization:from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
import os

# Set your OpenAI API key
os.environ['OPENAI_API_KEY'] = 'your-openai-api-key'
model = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106")

prompt = ChatPromptTemplate.from_template(
    "Summarize the following document '{document_name}':{context}Please provide the summary and key points."
)

loaded_documents = [documents, document]  # From S3 Loaders
flattened_documents = [doc for sublist in loaded_documents for doc in sublist] 

for loaded_document in flattened_documents:
    document_text = loaded_document.page_content
    document_name = getattr(loaded_document, 'name', 'Unknown Document')  # Assuming each document has a 'name' attribute
    chain = (
        RunnableLambda(lambda x: {"context": document_text, "document_name": document_name})
        | prompt
        | model
        | StrOutputParser()
    )
    summary = chain.invoke(None)
    print("Summary:", summary)
Python Langchain Example - Summarizing Documents with OpenAI APIBelow is the output from running this demo, and is a result of integrating LangChain with OpenAI’s GPT-3.5 and MinIO S3 storage; the output has been shortened for demonstrative purposes:Summary: The document is a quickstart guide for MinIO, a high-performance object storage system that is compatible with Amazon S3. It explains how to run MinIO on bare metal hardware or in containers. For Kubernetes environments, it recommends using the MinIO Kubernetes Operator. The key points are:

- MinIO is a high-performance object storage system.
- It is released under the GNU Affero General Public License v3.0.
- MinIO is API compatible with Amazon S3.
- It can be used to build high-performance infrastructure for machine learning, analytics, and application data workloads.
- The guide provides quickstart instructions for running MinIO on bare metal hardware or in containers.
- For Kubernetes environments, the MinIO Kubernetes Operator is recommended.Response from OpenAI APIThis method highlights an interesting way to load documents from S3 storage into an LLM using the Langchain framework to process them, while OpenAI’s GPT-3.5 model generates a concise summary and key points of the MinIO_Quickstart.md which is fetched from the play.min.io server. The use of AI to analyze and condense extensive documentation, provides users with a quick and thorough understanding of essential aspects like installation, server configuration, SDKs and other MinIO features. It showcases the capability of AI in extracting and presenting critical information from comprehensive data sources.Loading Documents from MinIO Buckets with LangchainThe integration of MinIO, Langchain and OpenAI offers a compelling toolset for managing large data volumes. While Langchain's S3 loaders, S3DirectoryLoader and S3FileLoader, play an important role in retrieving documents from MinIO buckets, they are solely for loading data into Langchain. These loaders do not perform actions related to uploading data into buckets. For tasks like uploading, modifying or managing bucket policies, the MinIO Python SDK is the appropriate tool. This SDK provides a comprehensive set of functionalities for interacting with MinIO storage, including file uploads, bucket management and more. For additional information, please see Quickstart Guide — MinIO Object Storage for Linux, Python Client API Reference — MinIO Object Storage for Linux.While Langchain streamlines the process of fetching and processing data using AI models, the heavy lifting of data management within the MinIO buckets is dependent on the MinIO Python SDK. This is an important distinction that must be understood by developers and data engineers building efficient, AI-integrated storage solutions. For a thorough understanding of MinIO's capabilities and how to utilize its Python SDK for various storage operations, refer to MinIO's official documentation.By using MinIO object storage as the primary data repository for AI and ML processes, you can simplify your data management pipeline. MinIO excels as a one-stop solution for storing, managing, and retrieving large datasets, which is crucial for effective AI and ML operations. This streamlined approach reduces complexity and overhead, potentially accelerating insights by ensuring swift access to data.For those interested in delving deeper into the integration of MinIO with Langchain to enhance LLM tool-use, the article “Developing Langchain Agents with MinIO SDK for LLM Tool-Use” offers a comprehensive exploration of the subject.Good luck in your development endeavors! We hope MinIO continues to play a key role in your AI/ML journey. Reach out to us on Slack and share your insights and discoveries!




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











MinIO Enterprise Cache: A Distributed DRAM Cache for Ultra-Performance

Keith Pijanowski
Mar 12, 2024








Dynamic ETL Pipeline: Hydrate AI with Web Data for MinIO and Weaviate using Unstructured-IO

David Cannan
Feb 27, 2024








Developing Langchain Agents with the MinIO SDK for LLM Tool-Use

David Cannan
Feb 20, 2024



















© 2014-2024 MinIO, Inc.
Privacy Policy
License Compliance







COMPANY
About
Partners
Pricing
Logo


CONTACT





 






 

                            275 Shoreline Dr, Ste 100,
                            Redwood City, CA 94065,
                            United States
                        





Sign up for MinIO Updates
















Join us on Slack







 
Get a Quote


1

Select Plan


Standard

Enterprise




2

Choose Capacity




TB





3



* Name



* Business Email







Submit
























