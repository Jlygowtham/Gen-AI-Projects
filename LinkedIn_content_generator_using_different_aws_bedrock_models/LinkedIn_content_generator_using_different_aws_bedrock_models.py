import os
import json
import boto3
from botocore.config import Config
from dotenv import load_dotenv
from datetime import datetime
import streamlit as st

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
            
            print('llm response: ',response)
            
            extract_response = response.get('content')[0].get('text').strip()
            
            final_response = self.formatting_response(extract_response)
            
            print("Final response: ",final_response)
            
            if isinstance(final_response,dict):
                final_response['file_key'] = self.upload_file_to_s3(final_response)
                
            
            return final_response
        
        except Exception as e:
            print("Error occured",e)
            return 'I am unable to generate the content and hashtags for your linkedin post topic'
            
    
    def formatting_response(self,response):
        try:
            
            if response.startswith('```json'):
                response = response[7:].strip()
                print("Removed ```json prefix")
            elif response.startswith('```'):
                response = response[3:].strip()
                print("Removed ``` prefix")
            if response.endswith('```'):
                response = response[:-3].strip()
                print("Removed ``` prefix")
                
            response = json.loads(response)
            return response
                
                
        except Exception as e:
            print(f"Error occured in formatting_response function: {e}")
            return 'I am unable to generate the content and hashtags for your linkedin post topic'
    
    
    def upload_file_to_s3(self,response):
        s3 = self.session.client('s3')
        
        try:
            print("Enter the upload_file_to_s3 function")
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
                return file_key
        
        except Exception as e:
            print(f"Error occured in upload_file_to_s3 function: {e}")
    
    def fetch_prompt(self):
        prompt = """
            <SystemPrompt>
                <Role>
                    You are a LinkedIn technical influencer with 20 years of experience in content preparation.
                </Role>
                
                <Instructions>
                    1. Examine the user's specified topic for content creation.
                    2. Develop engaging, accessible content that appeals to both technical and general audiences.
                    3. Format content using clear structure: organize with headings, bullet points, and emojis only where necessary for enhanced readability.
                    4. Create high-impact, searchable hashtags that align with the topic.
                    5. Output all results in valid JSON format only.
                    6. Present content as a single, well-formatted markdown paragraph without escape characters.
                    7. Return hashtags as a clean string array. Use this exact JSON structure: 
                    {'content': 'markdown contents', 'hash_tags': [list of hashtags], 'filename': 'file name'}
                    8. Generate a descriptive filename based on the user's query for S3 bucket storage. Provide only the filename without any file extension.
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
        st.set_page_config(page_title="LinkedIn Content & Hashtag Generator using AWS Bedrock Claude Sonnet 4", page_icon="🤖")
        
        if 'welcome_message' not in st.session_state:
            st.session_state['welcome_message'] = False
        
        user_topic = st.chat_input("Tell me your topic - I'll craft your LinkedIn post!")
        
        if not st.session_state['welcome_message'] and not user_topic:
        
            st.title("🤖 AI-Powered LinkedIn Content & Hashtag Generator with AWS Bedrock Claude Sonnet 4")
            st.write("""
                    Key Features:
                    
                    **Smart Content Creation**: Generate unique, engaging LinkedIn posts for maximum audience appeal.
                    
                    **Intelligent Hashtags**: Create highly discoverable and relevant hashtags to boost visibility.
                    
                    **Premium AI Technology**: Powered by AWS Bedrock's Claude Sonnet 4 for high-quality content.
                    
                    **Automated Cloud Storage**: Converts content to text files and uploads to AWS S3.
                    
                    **Dynamic File Management**: Creates unique, topic-based file names for organized storage.
                    
                    **Instant Download**: Download your generated content and hashtags as a ready-to-use text file.
                """)
            
        
        
        if user_topic:
            st.session_state['welcome_message'] = True
            
            user_message = st.chat_message('user')
            user_message.write(user_topic)
            
            
            with st.chat_message('assistant'):
                with st.spinner('Generating the LinkedIn content...'):
                    llm_response = self.invoking_model(user_topic)
                
                if isinstance(llm_response,dict):
                    print(f"\n Content: {llm_response.get('content')}")
                    print(f"\n HashTags: {llm_response.get('hash_tags')}")
                    
                    content = llm_response.get('content')
                    hash_tags = llm_response.get('hash_tags')
                    file_key = llm_response.get('file_key')
                    
                    format_hash_tags= ' '.join(f'**{hash_tag}**' for hash_tag in hash_tags)
                    
                    st.markdown(content)
                    st.markdown(format_hash_tags)
                    
                    if content and hash_tags and file_key:
                        _,col2=st.columns([3,1])
                        with col2:
                            st.download_button(
                                    label='Download File',
                                    data = content+'\n'*3+format_hash_tags,
                                    file_name=file_key,
                                    on_click="ignore",
                                    type='primary',
                                    icon=":material/download:"
                                )
                
                else:
                    print(f"llm response after invoking: {llm_response}")
                    st.write(llm_response)
                
            

if __name__ == "__main__":
    lpg=LinkedinPostGenerator()
    lpg.main()
        