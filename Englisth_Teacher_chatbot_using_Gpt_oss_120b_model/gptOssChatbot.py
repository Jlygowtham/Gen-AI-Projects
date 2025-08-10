from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class GptOssChatbot:
    def __init__(self):
        self.model='openai/gpt-oss-120b'
        self.api_key=os.getenv('api_key')
        self.client=OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=self.api_key
        )
        self.conversation_history=[{'role': 'assistant', 'content': """
                      #Role:
                         You are a 16 years of experience in the field of english.
                      
                      #Objective:
                         You will receive the user queries for any doubts regrading in the english grammars, literatures, sentence correction and etc.
                      
                      #Context:
                         Don't Give a answers for the questions which are not related to the english. If user asks that give a message like tell the dynamic message you are only here to help you with english.
                      
                      #Instructions:
                         1. Be polite and respectful.
                         2. Be accurate and correct.
                         3. Be helpful and informative.
                         4. Don't hallucination yourself, give a correct response with clear examples.
                         5. If user asks any real time or analogy examples, give a good and easy to understand examples.
                         6. Don't give a answers which are not related to the question. I user asks the question not related to english, give a message like "Sorry, I am a english chatbot, I can only answer the questions related to english. Please ask a question related to english."
             """}]
        
        self.tokens_history=[]
    
    def llm_invoking(self,user_input):
        
        self.conversation_history.append({'role': 'user', 'content': user_input})
        
        llm_response=self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation_history,
            max_tokens=4000,
            temperature=0.7
        )
        
        input_tokens = llm_response.usage.prompt_tokens
        output_tokens=llm_response.usage.completion_tokens
        total_tokens=llm_response.usage.total_tokens
        
        tokens_data = f"input tokens: {input_tokens} | output tokens: {output_tokens} | total tokens: {total_tokens}"
        self.tokens_history.append({'user_query':user_input,'model_conumption':tokens_data})
        
        response = llm_response.choices[0].message.content
        
        self.conversation_history.append({'role':'assistant','content':response})
        
        return response
        
        
    
    def main(self):
        print("🤖 I am English Teacher Bot")
        print("You can ask me any questions related to english")
        print('\n'+"="*60)
        print("""
These futures are available in this bot:
1. You can ask me any questions related to english grammar, literature, sentence correction and etc.
2. If you want to see the conversation history, type "history".
3. If you want to see the tokens history, type "tokens".
4. If you want to exit the bot, type "exit" or "quit".
""")  
        print('\n'+"="*60)
        
        
        while True:
            user_input=input("\n"+"👤 You: ")
            if user_input.lower() in ['quit','exit']:
                print('\n'+"Thank you for Interactive with me")
                break
            
            elif user_input.lower()=='history':
                print('\n'+"Conversation History:")
                for message in self.conversation_history:
                    role=message.get('role')
                    content = message.get('content')
                    print(f"role: {role}")
                    print(f"content: {content}")
                    print(" ")
            
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