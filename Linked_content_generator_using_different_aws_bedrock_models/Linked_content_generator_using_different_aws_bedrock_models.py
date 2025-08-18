import os
import json
import boto3
from botocore.config import Config
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class LinkedinPostGenerator:
    
    def __init__(self):
        self.session= boto3.Session(
                aws_access_key_id=os.getenv('aws_access_key'),
                aws_secret_access_key=os.getenv('aws_secret_key'),
                region_name='us-east-1'
            )
    
    def invoking_model(self,user_input):
        try:
            bedrock = self.session.client(
                'bedrock-runtime',
                config=Config(retries={"max_attempts": 10, "mode": "standard"},read_timeout=300)
            )
            
            model_id = os.getenv('model_id')
            
            system_prompt = self.fetch_prompt()
            
            request_body  = {
                "anthropic_version":"bedrock-2023-05-31",
                "max_tokens":2000,
                "system": system_prompt,
                "messages": [
                    {
                        'role': 'user',
                        'content': [{'type':'text','text': user_input}]
                    }
                ]
            }
            
            llm_response = bedrock.invoke_model(
                modelId = model_id,
                contentType = "application/json",
                accept= "application/json",
                body= json.dumps(request_body)
            )
            
            response = json.loads(llm_response['body'].read())
            
            print('response: ',response)
            
            extract_response = response.get('content')[0].get('text').strip()
            
            final_response = json.loads(extract_response)
            
            # print("Final response: ",final_response)
            
            self.upload_file_to_s3(final_response)
            
            return final_response
        
        except Exception as e:
            print("Error occured",e)
            return {
                'contents': 'No contents',
                'hash_tags': ['No hashtags']
            }
    
    
    def upload_file_to_s3(self,response):
        s3 = self.session.client('s3')
        
        try:
            content = response.get('content','')
            hash_tags = response.get('hash_tags',[])
            file_name = response.get('file_name','')
            timestamp = datetime.now().strftime("%Y_%m_%d_%H:%M:%S")
            
            format_hash_tags= "\n"*3+' '.join(hash_tags)
            
            if content and hash_tags and file_name:
                bucket_name = 'my-genaiproject-buckets'
                file_key = f'linkedin-post-generator/{file_name}-{timestamp}.txt'
                s3.put_object(Bucket=bucket_name, Key=file_key, Body=content+format_hash_tags)
                
                print(f"Uploaded the object successfully: {file_key}")
        
        except Exception as e:
            print(f"Error occured in upload_file_to_s3 function: {e}")
    
    def fetch_prompt(self):
        prompt = """
            <SystemPrompt>
                <Role>
                    You are a LinkedIn technical influencer with 20 years of experience in content preparation.
                </Role>
                
                <Instructions>
                    1. Analyze the user's content preparation topic.
                    2. Create unique and easily understandable content that appeals to both technical and non-technical audiences.
                    3. Structure the content with appropriate points, headings, bullet points, and emojis where suitable.
                    4. Generate relevant and highly discoverable hashtags related to the user's topic.
                    5. Return all responses in JSON format.
                    6. Format the content value as a single paragraph using proper markdown formatting without any escape characters.
                    7. Provide hashtags as a clean list of strings without escape characters.
                    8. file_name value i will create the new object in s3 bucket. Based on the user query give the correct file name. Only give the file name don't give the any file extension.
                </Instructions>
                
                <ResponseFormat>
                    {
                        "content": "generated content",
                        "hash_tags": ["hashtags as list of strings"],
                        "file_name": "file name should be based on the user query"
                    }
                </ResponseFormat>
                
            </SystemPrompt>
            """
        return prompt


    def main(self):
        print("I'm 🤖 Linkedin post content and hash tag generator")
        print('\n'+"="*60)
        
        while True:
            user_input= input('\n'+"Enter your topic (or type exit): ")
            if user_input.lower()=='exit':
                print("\n"+"Thank you to interacting with me, I'm ready to help you to generate the content and hast tag for your linkeding post topic")
                break
            else:
                response = self.invoking_model(user_input)
                print(f"\n Content: {response.get('content')}")
                print(f"\n HashTags: {response.get('hash_tags')}")
            

if __name__ == "__main__":
    lpg=LinkedinPostGenerator()
    lpg.main()