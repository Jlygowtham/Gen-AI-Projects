import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate

def summarize_webpage(web_url):
    try:
        # 1. Load the web content
        loader = WebBaseLoader(web_path=web_url)
        documents = loader.load()
        
        print(f"Web documents: {documents}")
        
        # 2. Split the documents into chunks
        
        text_splitter = CharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
        split_documents = text_splitter.split_documents(documents)
        
        print(f"Split documents: {split_documents}")
        
        # 3. Initialize the LLM
        
        llm = ChatOpenAI(
            model="openai/gpt-4o-mini",
            base_url="https://openrouter.ai/api/v1",
            api_key="",
            temperature=0.7,
            max_tokens=2000)
        
        # 4. Fetch the prompts
        
        map_prompt,combine_prompt = fetchPrompts()
        
        # 5. Create the summarization chain
        chain = load_summarize_chain(
            llm,
            map_prompt=map_prompt,
            combine_prompt=combine_prompt,
            chain_type="map_reduce"
        )
        
        return chain.run(split_documents)
        
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return "I am not able to summarize this web page at the moment. Please try again later."


def fetchPrompts():
        chunk_summary_prompt = PromptTemplate.from_template(
            """
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
                    
                    #Contents to summarize:
                        {text}
            """
        )
        
        overall_summary_prompt = PromptTemplate.from_template(
            """
                    #Role:
                        You are an expert summarizer with 10 years of experience integrating multi-part content.
                        
                    #Objective:
                        Your goal is to produce a concise, insightful overall summary of the entire content after all chunk summaries have been provided.
                    
                    #Context:
                        Do not hallucinate. Preserve meaning, nuance, and important insights.
                    
                    #Instructions:
                        1. Produce a final overall summary (200 or above words unless the user specifies a different length; if unspecified, default to 100–200 words).
                        2. Ensure summaries are meaningful, accurate, and do not omit key points.
                        3. Capture key arguments, evidence, contrasts, and conclusions from across all chunks.
                        4. Do not repeat the individual chunk summaries; synthesize them into a cohesive whole.
                        5. For final summary produce a clear, well-structured summary with a heading and bullet points.
                        
                    #Chunk summaries to combine:
                        {text}
            """
        )
        
        
        return chunk_summary_prompt,overall_summary_prompt

def main():
    st.set_page_config(page_title="Summarize Chatbot using LangChain and OpenAI", page_icon="🤖")
    st.title("Summarize Chatbot using LangChain and OpenAI")

    for key, default in {
        "show_result": False,
        "web_url":     "",
        "summary":     ""
    }.items():
        st.session_state.setdefault(key, default)

    if not st.session_state.show_result:
        web_url = st.text_input("Enter the web url to summarize", placeholder="https://example.com")
        if st.button("Summarize the webpage", disabled=not web_url):
            st.session_state.web_url = web_url
            st.session_state.show_result = True
            st.rerun()

    else:
        st.write(f"**Web URL:** {st.session_state.web_url}")

        if not st.session_state.summary:
            with st.spinner("Summarizing…"):
                st.session_state.summary = summarize_webpage(st.session_state.web_url)
            st.rerun()

        st.write(st.session_state.summary)

        if st.button("🔙 New summarization"):
            st.session_state.show_result = False
            st.session_state.web_url = ""
            st.session_state.summary = ""          
            st.rerun()


if __name__=='__main__':
    main()