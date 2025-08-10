from openai import OpenAI
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

class GptOssChatbot:
    def __init__(self):
        self.model='openai/gpt-5-chat'
        self.client=OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=""
        )
        
        self.tokens_history=[]
        
    def fetchPrompts(self,prompt_name):
        if prompt_name=='chunk_summary':
            chunk_summary_prompt = [{'role': 'assistant', 'content': """
                            #Role:
                                You are an expert Summarizer with 10 years of experience delivering accurate, insightful summaries.
                            
                            #Objective:
                                Your goal is to summarize each incoming content chunk individually and concisely.
                            
                            #Context:
                                Do not hallucinate. Preserve meaning, nuance, and important insights. 
                            
                            #Note:
                                Do not give the previous chunks summary. Give only for user provied chunk.
                            
                            #Instructions:
                                1. You will receive content in multiple chunks, each labeled with a chunk number.
                                2. For each chunk received, produce a clear, well-structured summary with a heading and bullet points.
                                3. Keep each chunk summary around 50–150 words unless the user specifies a different length; if unspecified, default to 100–200 words.
                                4. Ensure summaries are meaningful, accurate, and do not omit key points for each summary.
                                5. Only summarize chunks that have been provided. Do not produce an overall summary yet.
                                6. Do not give the previous chunk or chunks summary. Give only for user provied chunk.
                    """}]
            return chunk_summary_prompt
        
        else:
            overall_summary_prompt = [{'role': 'assistant', 'content': """
                            #Role:
                                You are an expert summarizer with 10 years of experience integrating multi-part content.
                            
                            #Objective:
                                Your goal is to produce a concise, insightful overall summary of the entire content after all chunk summaries have been provided.
                            
                            #Context:
                                Do not hallucinate. Preserve meaning, nuance, and important insights.
                            
                            #Instructions:
                                1. Produce a final overall summary (~200 words unless the user specifies a different length; if unspecified, default to 100–200 words).
                                2. Ensure summaries are meaningful, accurate, and do not omit key points.
                                3. Capture key arguments, evidence, contrasts, and conclusions from across all chunks.
                                4. Do not repeat the individual chunk summaries; synthesize them into a cohesive whole.
                                5. For final summary produce a clear, well-structured summary with a heading and bullet points.
                    """}]
            return overall_summary_prompt
        
    def content_splitter(self,text):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_text(text)
        
        print(f"Length of chunks: {len(chunks)}")
        return chunks
    
    def llm_invoking(self,user_input):
        final_chunk_text=self.content_splitter(user_input)
        prompt = self.fetchPrompts('chunk_summary')
        
        chunk_summary=[]
        
        for i,chunk in enumerate(final_chunk_text,1):
            prompt.append({'role':'user','content':f"Chunk: {i} | Content: {chunk}"})
            
            # print("\n"+f"Chunk {i}")
            
            llm_response=self.client.chat.completions.create(
                model=self.model,
                messages=prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            input_tokens = llm_response.usage.prompt_tokens
            output_tokens=llm_response.usage.completion_tokens
            total_tokens=llm_response.usage.total_tokens
            
            tokens_data = f"input tokens: {input_tokens} | output tokens: {output_tokens} | total tokens: {total_tokens}"
            self.tokens_history.append({'Chunk':chunk,'model_conumption':tokens_data})
            
            response = llm_response.choices[0].message.content
            
            
            chunk_summary.append(response)
            
            prompt.pop(1)
            
        
        final_summary_response = self.final_summary_invoking(chunk_summary)
        
        return final_summary_response
    
    def final_summary_invoking(self,chunk_summary):
        print("Finall summary invoking....................")
        
        content = "\n".join(chunk_summary)
        prompt = self.fetchPrompts('overall_summary')
        
        prompt.append({'role':'user','content':f"All chunk summarize: {content}"})
            
        llm_response=self.client.chat.completions.create(
            model=self.model,
            messages=prompt,
            max_tokens=3000,
            temperature=0.7
        )
        
        input_tokens = llm_response.usage.prompt_tokens
        output_tokens=llm_response.usage.completion_tokens
        total_tokens=llm_response.usage.total_tokens
        
        tokens_data = f"input tokens: {input_tokens} | output tokens: {output_tokens} | total tokens: {total_tokens}"
        self.tokens_history.append({'Chunk':"All chunks",'model_conumption':tokens_data})
        
        response = llm_response.choices[0].message.content
        
        return response
            
    
    def main(self):
        print("🤖 I am Summarize Bot")
        print("You can ask me any questions related to english")
        print('\n'+"="*60)
        print("""
These futures are available in this bot:
1. You can summarize the any content with insightful, meaningful summary for your content.
2. If you want to close the conversation, type 'quit' or 'exit'.
""")  
        print('\n'+"="*60)
        
        
        while True:
            user_input=input("\n"+"👤 You: ")
            if user_input.lower() in ['quit','exit']:
                print('\n'+"Thank you for Interactive with me")
                break
            
            
            elif user_input.lower()=='tokens':
                print('\n'+"Tokens History:")
                for tokens in self.tokens_history:
                    user_query=tokens.get('user_query')
                    model_conumption=tokens.get('model_conumption')
                    print(f"user query: {user_query}")
                    print(f"model consumption: {model_conumption}")
                    print(" ")
            
            else:
                response =self.llm_invoking(user_input)
                print('\n'+f"🤖 Assistant: {response}")
                
                
if __name__ == "__main__":
    chatbot = GptOssChatbot()
    chatbot.main()
