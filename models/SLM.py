import ollama
import os
import re
import json
from pytube import YouTube
from transformers import pipeline
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.llms import ChatMessage

class Speech2Text:
    def __init__(self,model_name="openai/whisper-tiny",device='cuda'):
        try:
            self.pipe = pipeline("automatic-speech-recognition", model=model_name, device = 'cuda')
        except:
            print("No cuda found, falling back to cpu")
            self.pipe = pipeline("automatic-speech-recognition", model=model_name, device = 'cpu')
    
    def get_transcript(self,file_path):
        return self.pipe(file_path)['text']

class SLM:
    def __init__(self,model_name,):
        self.model_name=model_name
        self.audio_model = Speech2Text()
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
        Settings.llm = Ollama(model=self.model_name, request_timeout=360.0)
    
    def prompt(self,chat_history,stream):
        return ollama.chat(model=self.model_name,messages=chat_history,stream=stream)


    def get_youtube_video(self,url: str) -> str:
        """Download a YouTube video, transcribe the audio, and summarize the transcription."""
        # Download YouTube video
        yt = YouTube(url)
        video_title = yt.title  # Get the video title
        video_stream = yt.streams.filter(only_audio=True).first()
        output_file = video_stream.download(filename='video.mp4')
        base, ext = os.path.splitext(output_file)
        wav_file = base + '.wav'
        os.system(f'ffmpeg -i {output_file} {wav_file}')

        # Transcribe audio using Whisper
        transcription = self.audio_model.get_transcript(wav_file)
        os.remove('video.mp4')
        os.remove('video.wav')
        return video_title,transcription
        
    def check_for_videos(self,text):
        youtube_url_pattern = re.compile(r'(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w\-]+)')
        matches = youtube_url_pattern.findall(text)
        if matches:
            return ""
        
        context = ""
        template = """
        Summarize the following video, be as concise as possible unless the user ask, extract some bullet points, you should answer with summary exclusively
        Transcription: {transcription}
        """
        for idx,match in enumerate(matches):
            video_title,transcription = self.get_youtube_video(match)
            prompt = [
            {'role': 'user', 'content': template.format(transcription=transcription)}
        ]
            summary = self.prompt(chat_history=prompt,stream=False)['message']['content']
            context+=f"Transcription of the Video #{idx}\nTitle of the video:{video_title}\nUrl of the video: {match}\nSummary of the video:\n{summary}\n\n"
        return context

    def chat(self,chat_history, data_folder, is_stream=True):
        """
        System role message must always be the first
        """
        documents = SimpleDirectoryReader(data_folder).load_data()

        # Limit metadata to current folder
        cwd = os.getcwd()
        for doc in documents:
            fp = doc.metadata['file_path']
            doc.metadata['file_path'] = os.path.relpath(fp, cwd)
        # Load documents
        index = VectorStoreIndex.from_documents(
            documents,
        )

        # Load chat_history or create new history 
        if len(chat_history)==1:
            memory = ChatMemoryBuffer.from_defaults(token_limit=1500)
        else:
            # Save all messages into memory except the last messag that is the current prompt
            memory = ChatMemoryBuffer.from_defaults(token_limit=1500)
            for message in chat_history[:-1]:
                memory.put(ChatMessage(role=message['role'],content=message['content']))
        
        # Create chat engine with memory
        chat_engine = index.as_chat_engine(
            chat_mode = "context",
            memory = memory,
            system_prompt = (
                "You are my helpful assitant"
            )
        )

        # Current user input
        user_input = chat_history[-1]['content']

        # Use a template and tools for the user prompt
        context = self.check_for_videos(user_input)
        template = """
        Context:{context}\n
        User input: {user_input}
        """
        prompt = template.format(context=context,user_input=user_input)
        print(prompt)
        if is_stream:
            response = chat_engine.stream_chat(prompt)
        else:
            reponse = chat_engine.chat(prompt)

        return response
    
    def create_title(self,message) ->str:
        template="""
        Your only task is to create headline for the following text, the complete Output of the text should be less than 30 characters
        Text:{context}\n\n
        Headline: 
        """
        prompt =[{'role': 'user', 'content': template.format(context=message)}]
        title = self.prompt(chat_history=prompt,stream=False)
        return title['message']['content'][:45]
    
    @staticmethod
    def get_source_file_paths(response):
        source_nodes = response.source_nodes
        file_paths = set()
        for node in source_nodes:
            if 'file_path' in node.metadata:
                file_paths.add(node.metadata['file_path'])
        return list(file_paths)
    

        