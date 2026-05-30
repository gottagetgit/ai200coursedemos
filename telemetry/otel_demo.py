import os
import time
import logging 
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-pipeline")
logger.setLevel(logging.INFO)

tracer = trace.get_tracer("ai-pipeline")

def retrieve_documents(query):
    with tracer.start_as_current_span("retrieve_documents") as span:
        span.set_attribute("query.text", query)
        span.set_attribute("db.system", "postgresql")
        logger.info("Starting document retrieval for query: %s", query)
        # Simulate retrieval
        import time; time.sleep(0.05)
        results = ["doc1", "doc2"]
        span.set_attribute("results.count", len(results))
        logger.info("Retrieved %s documents", len(results))
        return results

def generate_response(context, question):
    with tracer.start_as_current_span("generate_response") as span:
        span.set_attribute("model", "gpt-4")
        span.set_attribute("context.length", len(context))
        logger.info("Generating response for question: %s", question)
        import time; time.sleep(0.2)
        answer = "This is the AI-generated answer."
        logger.info("Generated response with length %s", len(answer))
        return answer

def rag_pipeline(question):
    with tracer.start_as_current_span("rag_pipeline") as root_span:
        root_span.set_attribute("question", question)
        logger.info("RAG pipeline started")
        docs = retrieve_documents(question)
        context = " ".join(docs)
        answer = generate_response(context, question)
        root_span.set_attribute("answer.length", len(answer))
        logger.info("RAG pipeline completed successfully")
        return answer
    
print(rag_pipeline("What is Azure Container Apps?"))
print("Trace sent to Application Insights - check in 2-3 minutes.")