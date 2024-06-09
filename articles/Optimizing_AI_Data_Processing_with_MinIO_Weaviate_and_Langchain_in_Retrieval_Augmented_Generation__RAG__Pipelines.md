# Optimizing AI Data Processing with MinIO Weaviate and Langchain in Retrieval Augmented Generation (RAG) Pipelines

![Header Image](articles/images/Optimizing_AI_Data_Processing_with_MinIO_Weaviate_and_Langchain_in_Retrieval_Augmented_Generation__RAG__Pipelines.jpg)

Optimizing AI Data Processing with MinIO Weaviate and Langchain in Retrieval Augmented Generation (RAG) Pipelines
David Cannan
David Cannan
on
AI/ML


if os.environ.get("WEAVIATE_API_KEY", None) is None:
raise Exception("Missing `WEAVIATE_API_KEY` environment variable.")


if os.environ.get("WEAVIATE_ENVIRONMENT", None) is None:
raise Exception("Missing `WEAVIATE_ENVIRONMENT` environment variable.")


WEAVIATE_INDEX_NAME = os.environ.get("WEAVIATE_INDEX", "langchain-test")

### Ingestion via WebBasedLoader
# Load
loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
data = loader.load()

### Split text via RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

### Add to vectorDB
# vectorstore = Weaviate.from_documents(
#     documents=all_splits, embedding=OpenAIEmbeddings(), index_name=WEAVIATE_INDEX_NAME
# )
# retriever = vectorstore.as_retriever()

vectorstore = Weaviate.from_existing_index(WEAVIATE_INDEX_NAME, OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

### RAG prompt
template = """Answer the question based only on the following context:
{context}
Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

### RAG pipeline
model = ChatOpenAI()
chain = (
RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
| prompt
| model
| StrOutputParser()
)

# Add typing for input
class Question(BaseModel):
__root__: str

chain = chain.with_types(input_type=Question)
Original LangChain Weaviate RAG Script
Integration of MinIO SDK Within LangChain-Weaviate RAG Pipeline
The above code is our starting point and gives us a canvas on which to convey several of the more simplified integration points.
Initialization and Setup
Begin by setting up the
MinIO client
, this setup is foundational, as it supports the entire data management process within the RAG pipeline.
from minio import Minio

# Initialize the MinIO client with appropriate access credentials
minio_client = Minio(
"play.min.io:443",
access_key="minioadmin",
secret_key="minioadmin",
secure=True
)
Connecting to play.min.io:443 server via minio_client
Modifying Data Ingestion
Instead of using the default
WebBaseLoader
for data ingestion, transition to a direct data retrieval method from MinIO. This change simplifies the data access process, which is critical for enhancing the pipeline's efficiency from the very beginning.
from io import BytesIO

# Define a function to fetch data directly from a MinIO bucket
def fetch_data_from_s3(bucket_name, object_name):
response = minio_client.get_object(bucket_name, object_name)
data = BytesIO(response.read())
response.close()
return data.getvalue().decode('utf-8')


# Example usage
bucket_name = "hydrate-bucket"
object_name = "urls.txt"
data = fetch_data_from_s3(bucket_name, object_name)
Fetch data from bucket snippet
For further demonstration of hydrating data for MinIO Python SDK and Weaviate... see notebook in blog-assets repository
here
.
Processing and Storing Split Data
After retrieving the raw data, use the `
RecursiveCharacterTextSplitter
` from LangChain to segment the data into manageable chunks, preparing it for deeper analysis and processing.
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Split the retrieved data into smaller text chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

# Store the processed data splits back into MinIO for easy retrieval and further use
def store_data_in_s3(bucket_name, object_name, content):
content_bytes = content.encode('utf-8')
minio_client.put_object(bucket_name, object_name, BytesIO(content_bytes), len(content_bytes))

# Example of storing each split in MinIO
for index, split in enumerate(all_splits):
store_data_in_s3("clean-bucket", f"split_{index}.txt", split)
Saving-splits snippet
For further demonstration of saving-splits with MinIO Python SDK, see notebook in blog-assets repository
here
.
Retrieving and Utilizing RAG Prompts
Retrieve the necessary
RAG prompts
from MinIO, which are essential for directing the AI model's response generation in the RAG pipeline.
# Fetch the RAG prompt stored in a MinIO bucket
# Function to retreive rag-prompt.txt from prompt-bucket

def get_prompt_from_minio(client, bucket_name, object_name):
"""
Retrieve a text file from a specified MinIO bucket and return its content as a string.
:param client: Minio client instance
:param bucket_name: Name of the MinIO bucket
:param object_name: Object name in the bucket (e.g., 'rag-prompt.txt')
:return: Content of the prompt as a string
"""
try:
# Get object data from the specified bucket
response = client.get_object(bucket_name, object_name)
data = response.read()  # Read data from the response
prompt_content = data.decode('utf-8')  # Decode bytes to string
return prompt_content
except Exception as e:
print(f"Failed to retrieve prompt: {e}")
return None


# Usage
prompt = get_prompt_from_minio(minio_client, "prompt-bucket", "rag-prompt.txt")

if prompt:
print(f"Retrieved prompt content: {prompt}")
else:
print("No content retrieved.")
Prompt-retrieval snippet
For further demonstration of prompt-retrieval with MinIO Python SDK, see notebook in blog-assets repository
here
.
Executing RAG Process Chain
With all elements in place, below is an example of
RetrievalQA chain
to execute the RAG process using the configured LangChain framework, leveraging the retriever and the language model to generate contextually relevant answers.
from langchain.chains import RetrievalQA


# Setup the RetrievalQA chain with the language model and the vector store retriever
qa_chain = RetrievalQA.from_chain_type(
llm,
retriever=vectorstore.as_retriever(),
chain_type_kwargs={"prompt": prompt}
)


# Execute the RAG process with a sample query
question = "What are the approaches to Task Decomposition?"
result = qa_chain({"query": question})
print(result["result"])
RetrievalQA chain snippet
Because of the infrastructure provided by MinIO, there are endless possibilities for the development of custom integrated AI and MinIO can provide. This approach highlights MinIO's versatile role in the RAG pipeline and its potential to streamline operations, offering a practical and efficient solution for managing the lifecycle of AI-driven data processing and content generation tasks.
Evaluation of a MinIO Integrated RAG Pipeline
A refined RAG pipeline leveraging MinIO, Weaviate, and LangChain benefits significantly from a detailed and methodical evaluation process. Here's how we can streamline this approach:
Ragas Framework Application
Ragas serves as the core of our evaluation, providing comprehensive metrics for both retrieval and generation:
Context Relevancy & Recall:
Ensures the information retrieved is comprehensive and pertinent to the query.
Answer Faithfulness & Relevancy:
Verifies that the generated answers are factually accurate and directly address the questions posed.
Ragas's LLM-driven evaluation offers a harmonized score, reflecting overall QA performance. Its nuanced use of LLMs includes parsing answers into verifiable statements against the context, comparing predicted potential questions to actual questions for relevancy, and ensuring all supporting information is present in the retrieved context.
Continuous Evaluation with LangSmith
LangSmith enhances Ragas by providing:
A platform for creating and managing test datasets and running evaluations.
Tools for visualizing and analyzing results, making Ragas metrics transparent and actionable.
Facilities for augmenting evaluation with real-world data, adding test examples from production logs.
Together, these tools allow for an iterative and dynamic evaluation approach, enabling real-time insights and continuous improvement of the RAG pipeline.
This evaluation strategy underscores the pipeline's functionality and adaptability, aiming to maintain a robust and efficient system. With a focus on performance metrics and continuous assessment, it offers a pathway for sustained refinement and optimization of the integrated RAG pipeline
Further Exploration into RAG and AI
For delving deeper into the understanding of Retrieval-Augmented Generation (RAG), and related technologies, I’ve compiled the following resources that I found helpful in my own exploration:
Hugging Face's RAG Documentatio
n
:
Detailed documentation on RAG models provided by Hugging Face.
RAG Evaluation with Ragas and LangSmith
:
A guide to evaluating RAG systems using Ragas and LangSmith.
Retrieval-Augmented Generation for Large Language Models: A Survey
:
A survey paper on the advancements in combining retrieval mechanisms with large language models.
Retrieval-Augmented Generation for AI-Generated Content: A Survey
:
This paper provides a comprehensive examination of RAG systems' effectiveness in generating AI content.
ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems
:
ARES finetunes language models to autonomously assess RAG systems, reducing dependency on human annotations.
RaLLe: A Framework for Developing and Evaluating Retrieval-Augmented Large Language Models
:
RaLLe provides tools for building and testing R-LLMs, enhancing the transparency and optimization of the retrieval and generation process.
Final Thoughts: Enhancing AI Workflows with MinIO
As we explored the integration of MinIO with Retrieval-Augmented Generation (RAG) pipelines and Weaviate vector storage using Langchain, it's clear that this combination offers significant enhancements to AI data processing. By leveraging MinIO's robust storage capabilities, alongside Weaviate's efficient vector storage and the flexible Langchain framework, we can streamline workflows and manage data more effectively throughout its lifecycle.
The integration’s impact extends beyond current enhancements, opening up new avenues for innovation within the broader AI landscape. It promises to expand the capabilities of AI systems, especially in generating nuanced, contextually rich responses that could become more commonplace. This ongoing evolution and refinement of tools are set to not only streamline existing processes but also pave the way for new breakthroughs in AI applications.
For those keen to dive deeper into the burgeoning world of RAG technologies and their applications, engage with us on
