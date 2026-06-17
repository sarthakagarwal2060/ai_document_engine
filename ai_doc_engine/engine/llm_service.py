import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile" # Updated to actively supported Llama 3

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
            
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
        )
        return response.choices[0].message.content

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
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
        )
        return response.choices[0].message.content

    def chat_with_context(self, question, context):
        prompt = f"""
        Answer the developer's question using ONLY the provided documentation context. 
        If the answer is not in the context, say "I cannot find this in the documentation." Do not hallucinate.
        
        CONTEXT:
        {context}
        
        QUESTION: {question}
        """
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
        )
        return response.choices[0].message.content