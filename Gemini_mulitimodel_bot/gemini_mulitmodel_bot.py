from PIL import Image
from google import genai
import json

class GeminiBot:
    def __init__(self):
        self.client = genai.Client(api_key="")

    def model_invoking(self,user_input,image=None):
        try:
            system_prompt="""
                #Role:
                    You are a helpful AI assistant who was trained on a wide range of topics and can assist users with their queries.
                
                #Objective:
                    You will receive a user query or image and provide a relevant response based on the input.
                
                #Context:
                    Don't hallucinate. Preserve meaning, nuance, and important insights.
                
                #Instructions:
                    1. If the user query is a text, analyze it and provide the correct information.
                    2. If the user query is an image, analyze the image and provide a relevant response.
                    3. In image data, give a response as 100 to 200 words with correct insights. Don't hallucinate, extract the correct information from the image. If user wants to know in some parts of the image, give a response with correct insights.
                    4. In text data, Give a correct response with bullet points and headings if needed. If it is not needed don't give a bullet points or headings.
                
                #Response Format:
                    'response': 'Your response here' (It is string response for the user query you will send the space, heading, sub heading, bullet points if needed but not a key value pairs)
            """
            
            if image is not None and image.endswith(('.png','.jpg','jpeg','webp')):
                image = Image.open(image)
                response = self.client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=[image, user_input],
                    config=genai.types.GenerateContentConfig(max_output_tokens=500, temperature=0.7, system_instruction=system_prompt,response_mime_type="application/json")
                )
            else:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"User query: {user_input}",
                    config=genai.types.GenerateContentConfig(max_output_tokens=2000, temperature=0.7,system_instruction=system_prompt,response_mime_type="application/json")
                )
            
            
            response_text = response.text.strip()
            
            if response_text.startswith('```'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
                
            try:
                parsed_response = json.loads(response_text)
                return parsed_response.get('response', 'No response generated.')
            except json.JSONDecodeError:
                return response_text
            
        except Exception as e:
            print("Error invoking mode: ", str(e))
            return "I am not able to process your request at the moment. Please try again later."

    def main(self):
        print("🤖 I am Gemini Bot")
        print("You can ask me any questions or provide an image for analysis.")
        print('\n' + "=" * 60)
        print('\n'+"""These features are available in this bot:
              
1. You can ask me any questions related to various topics.
2. You can provide an image for analysis.
3. You can ask me to summarize a text.
4. You can ask me to generate a text based on a prompt.
5. You can ask me to translate a text from one language to another.
6. You can ask me to generate a text based on a prompt and an image.
""")
        print('\n'+"""
1. If you want to upload the image, choose the type as image and give the prompt for what you want to know about the image.
2. If you want to ask a question, choose the type as text and give your query or what you want to know.
3. If you want to exit the bot, type 'exit' or 'quit'.
""")
        print('\n' + "=" * 60)

        while True:
            type_input= input("Choose the type (text/image) or quit: ").strip().lower()
            if type_input not in ['text', 'image', 'exit', 'quit']:
                print("Invalid type. Please choose 'text' or 'image'.")
                continue
            
            elif type_input.lower() in ['exit','quit']:
                print("Thank you for interacting with me!")
                break
            
            elif type_input=='image':
                image_path= input("Enter the image path: ").strip()
                user_input = input("Your query about the image: ").strip()
                response = self.model_invoking(user_input, image=image_path)
                print("Bot: ", response)
                print('\n'+"="*60)
            else:
                user_input=input("Ask anything: ").strip()
                if not user_input:
                    print('Please provide me a valid input.')
                    continue
                response = self.model_invoking(user_input)
                print("Bot: ",response)
                print('\n'+"="*60)
                
                
                
if __name__ == "__main__":
    bot = GeminiBot()
    bot.main()