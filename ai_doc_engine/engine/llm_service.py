import os
import groq
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        # Support either a comma-separated list of keys or a single key
        keys_env = os.getenv("GROQ_API_KEYS")
        if keys_env:
            keys = [k.strip() for k in keys_env.split(",") if k.strip()]
        else:
            single_key = os.getenv("GROQ_API_KEY")
            keys = [single_key] if single_key else []
            
        if not keys:
            raise ValueError("No GROQ_API_KEY or GROQ_API_KEYS found in environment variables.")
            
        # Initialize a pool of clients
        self.clients = [Groq(api_key=key) for key in keys]
        self.current_client_index = 0
        self.model = "llama-3.3-70b-versatile" # Updated to actively supported Llama 3

    def _execute_with_fallback(self, prompt):
        """Attempts the Groq request, falling back to the next API key if it fails."""
        last_exception = None
        
        for _ in range(len(self.clients)):
            client = self.clients[self.current_client_index]
            try:
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model,
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"⚠️ Groq API key failed (Index {self.current_client_index}). Error: {e}", flush=True)
                last_exception = e
                # Rotate to the next API key in the pool
                self.current_client_index = (self.current_client_index + 1) % len(self.clients)
                print(f"🔄 Switching to next Groq API key (Index {self.current_client_index})...", flush=True)
                
        # If we loop through all keys and they all fail, raise the final error
        raise RuntimeError(f"All {len(self.clients)} Groq API keys failed! Last error: {last_exception}")

    def generate_documentation(self, unit):
        if isinstance(unit, str):
            code_snippet = unit
            prompt = f"""
            You are an expert technical writer. Generate comprehensive Markdown documentation for the following code.
            Include: Purpose, Parameters, Return values, Side effects, Usage examples, and Edge cases.
            
            CODE:
            {code_snippet}
            """
        else:
            prompt = f"""
            You are an expert technical writer. Generate comprehensive Markdown documentation for this specific code unit.
            
            Name: {unit.name}
            Type: {unit.unit_type}
            Return Type: {unit.return_type or 'None'}
            Parameters: {unit.parameters}
            Existing Docstring: {unit.docstring or 'None'}
            
            CODE:
            {unit.raw_code}
            
            Please output a professional Markdown documentation block including: 
            Purpose, Detailed Parameters, Return values, and Usage examples.
            """
        return self._execute_with_fallback(prompt)

    def detect_staleness_and_draft(self, old_doc, patch):
        prompt = f"""
        Analyze this Git patch and the existing documentation.
        1. Classify the documentation staleness severity: [BROKEN, POTENTIALLY_OUTDATED, REVIEW_RECOMMENDED, SAFE].
        2. If not SAFE, draft an updated version of the documentation.
        
        PATCH:
        {patch}
        
        OLD DOC:
        {old_doc}
        
        Return format:
        SEVERITY: <classification>
        UPDATED_DOC: <markdown>
        """
        return self._execute_with_fallback(prompt)

    def chat_with_context(self, question, context):
        prompt = f"""
        You are a helpful coding assistant. 
        Answer the developer's question based strictly on the provided documentation context below.
        If the context does not contain the answer, say "I cannot find this in the documentation."
        
        CONTEXT:
        {context}
        
        QUESTION: {question}
        """
        return self._execute_with_fallback(prompt)