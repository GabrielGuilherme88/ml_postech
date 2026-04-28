from langfuse import Langfuse
from langchain.callbacks.tracing_langfuse import LangfuseCallbackHandler
from langchain_openai import ChatOpenAI
import os
from datetime import timedelta, datetime

class LLMQualityMonitor:
    def __init__(self):
        self.langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "http://localhost:3001")
        )

    def get_langfuse_callback(self):
        return LangfuseCallbackHandler(
            langfuse=self.langfuse,
            trace_name="ana-auditora"
        )

    def get_llm_with_tracing(self, model: str = "gpt-4"):
        return ChatOpenAI(
            model=model,
            callbacks=[self.get_langfuse_callback()]
        )

    def get_trace_stats(self, hours: int = 24):
        traces = self.langfuse.trace.list(
            start_time=datetime.now() - timedelta(hours=hours)
        )
        
        total_traces = len(traces.data)
        avg_latency = sum(t.latency for t in traces.data) / total_traces if total_traces > 0 else 0
        
        return {
            "total_traces": total_traces,
            "avg_latency_ms": avg_latency * 1000,
            "success_rate": self._calculate_success_rate(traces)
        }

    def _calculate_success_rate(self, traces):
        if not traces.data:
            return 0
        successful = sum(1 for t in traces.data if t.status == "success")
        return successful / len(traces.data)

    def get_evaluation_metrics(self, trace_id: str):
        trace = self.langfuse.trace.get(trace_id)
        
        evaluations = trace.evaluations
        
        return {
            "faithfulness": evaluations.get("faithfulness"),
            "relevancy": evaluations.get("relevancy"),
            "hallucination": evaluations.get("hallucination"),
            "version": "1.0.0"
        }

def create_llm_callback():
    monitor = LLMQualityMonitor()
    return monitor.get_langfuse_callback()
