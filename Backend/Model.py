import cohere  # Import the Cohere library for AI services.
from rich import print  # Import the Rich library to enhance terminal outputs.
from dotenv import dotenv_values  # Import dotenv to load environment variables.

import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Load environment variables from the .env file.
env_vars = dotenv_values(resource_path(".env"))

# Retrieve API key.
CohereAPIKey = env_vars.get("CohereAPIKey")
CohereModel = env_vars.get("CohereModel")

# Create a Cohere client using the provided API key.
co = cohere.Client(api_key=CohereAPIKey)

# Define a list of recognized function keywords for task categorization.
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder", "send message", "whatsapp call" , "video call"
]


# Initialize an empty list to store user messages.
messages = []

preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
*** If you don't know what to put anything in any catogary like good bye or user wanna go somewhere or leave put that under general catagory  or user wanna end a conversation then put it in general(query)***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if query is 'goodbye' respond with 'general goodbye', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'exit ( query )' if user wanna says goodbye or bye or says to going somewhere or wanna exit or leave from conversation or any greatings then respond with 'exit (query)' like 'bye jarvis', 'goodbye jarvis', 'see you jarvis', 'see you later jarvis' so respond with 'exit bye jarvis', 'exit goodbye jarvis', 'exit see you jarvis', 'exit see you later jarvis'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'send message (query)' if a query is asking to send a message like 'send message to mom i will be late today.', 'send message to dad' , 'send message to ritik' ,  etc. but if the query is asking to send multiple messages, respond with 'send message 1st contact name 1st message, send message 2nd contact name 2nd message' and so on.
-> Respond with 'whatsapp call (name of the person to call)' if a query is asking to call or phone call or make whatsapp call or audio call or'whatsapp call mom'  , 'phone call to mom' then reply with 'whatsapp call mom'and so on.
-> Respond with 'video call (name of the person to call)' if a query is asking to call or phone call or make whatsapp VIDEO call or video call or'video call ritik' and so on.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
-> Respond with 'send message (contact name message)' if a query is asking to send a message to a specific contact like 'send message to mom i will be late today.', 'send message to dad i will be there in 5 minutes.', etc. but if the query is asking to send multiple messages, respond with 'send message 1st contact name 1st message, send message 2nd contact name 2nd message' and so on.
-> Respond with 'whatsapp to (contact name message)' if a query is asking to send a whatsapp message to a specific contact like 'whatsapp to mom i will be late today.', 'whatsapp to dad i will be there in 5 minutes.', etc. but if the query is asking to send multiple whatsapp messages, respond with 'whatsapp to 1st contact name 1st message, whatsapp to 2nd contact name 2nd message' and so on.
-> Respond with 'telegram to (contact name message)' if a query is asking to send a telegram message to a specific contact like 'telegram to brother i will be late today.', 'telegram to dad i will be there in 5 minutes.', etc. but if the query is asking to send multiple telegram messages, respond with 'telegram to 1st contact name 1st message, telegram to 2nd contact name 2nd message' and so on.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'opening facebook, opening telegram, closing whatsapp' Sir***
*** If the user is saying goodbye or wants to end the conversation like 'bye Javis' respond with 'Bye Sir, Exiting '.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""
# Define a chat history with predefined user-chatbot interactions for context.
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "goodbye jarvis"},
    {"role": "Chatbot", "message": "exit goodbye jarvis"},
    {"role": "User", "message": "bye jarvis"},
    {"role": "Chatbot", "message": "exit bye jarvis"},
    {"role": "User", "message": "ok i gotta go bye"},
    {"role": "Chatbot", "message": "exit ok i gotta go bye"},
    {"role": "User", "message": "goodbye jarvis good to see you"},
    {"role": "Chatbot", "message": "exit goodbye jarvis good to see you"},
    {"role": "User", "message": "send whatsapp message to my dad hello"},
    {"role": "Chatbot", "message": "send message dad hello"},
    {"role": "User", "message": "message mother like what are you doing good morning"},
    {"role": "Chatbot", "message": "send message mother what are you doing good morning"},
    {"role": "User", "message": "message teacher what are you doing"},
    {"role": "Chatbot", "message": "send message teacher what are you doing."},
    {"role": "User", "message": "call my riki"},
    {"role": "Chatbot", "message": "whatsapp call riki"},
    {"role": "User", "message": "make a phone call to riki"},
    {"role": "Chatbot", "message": "whatsapp call riki"},
    {"role": "User", "message": "do video call to my shubham"},
    {"role": "Chatbot", "message": "video call shubham"},
    {"role": "User", "message": "make a phone call to ritik"},
    {"role": "Chatbot", "message": "whatsapp call ritik"},
    {"role": "User", "message": "make a whatsapp video call to ritik"},
    {"role": "Chatbot", "message": "video call ritik"},
    {"role": "User", "message": "make a video call to rohit"},
    {"role": "Chatbot", "message": "video call rohit"},

    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that i have a dancing performance on 5th aug at 11pm"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."},
    {"role": "User", "message": "hey send a message to mom that i will be late today."},
    {"role": "Chatbot", "message": "send message mom i will be late today."},
    {"role": "User", "message": "whatsapp to dad that i will be there in 5 minutes."},
    {"role": "Chatbot", "message": "whatsapp to dad i will be there in 5 minutes."},
    {"role": "User", "message": "telegram to brother that i will be late today."},
    {"role": "Chatbot", "message": "telegram to brother i will be late today."}
]

# Define the main function for decision-making on quries
def FirstLayerDMM(prompt: str = "test"):
    # Add the user's query to the messages list.
    messages.append({"role": "user", "content": f"{prompt}"})

    # Create a streaming chat session with the Cohere model.
    stream = co.chat_stream(
        model=CohereModel,  # Specify the Cohere model to use.
        message=prompt,          # Pass the user's query.
        temperature=0.7,         # Set the creativity level of the model.
        chat_history=ChatHistory, # Provide the predefined chat history for context.
        prompt_truncation='OFF', # Ensure the prompt is not truncated.
        connectors=[],           # No additional connectors are used.
        preamble=preamble        # Pass the detailed instruction preamble.
    )

    # Initialize an empty string to store the generated response.
    response = ""

    # Iterate over events in the stream and capture text generation events.
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text  # Append generated text to the response.

    response = response.replace("\n", "")
    response = response.split(",")

    response = [i.strip() for i in response]
    # Initialize empty list
    temp =[]

    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)
    # Update the response with the filtered list of tasks.
    response = temp
    
    if response == []:
        response = [f"general {prompt}"]

    # If '(query)' is in the response, recursively call the function for further clarification.
    if "(query)" in response:
        newresponse = FirstLayerDMM(prompt=prompt)
        
        return newresponse  # Return the clarified response.
    else:
        return response  # Return the filtered response.

    # Entry point for the script.
if __name__ == "__main__":
    # Continuously prompt the user for input and process it.
    while True:
        print(FirstLayerDMM(input(">>> ")))  # Print the categorized response.
