from groq import Groq #Importing the Groq library to use its API.
from json import load, dump # Importing functions to read and write JSON files.
import datetime # Importing the datetime module for real-time date and time information.
from dotenv import dotenv_values # Importing dotenv_values to read environment variables from a .env file.

import sys
import os
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


#Load environment variables from the env file.
env_vars = dotenv_values(resource_path(".env"))

#Retrieve specific environment variables for username, assistant name, and API key.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")
GroqModel = env_vars.get("GroqModel")

#Initialize the Groq client using the provided API key.
client = Groq(api_key=GroqAPIKey)

#Initialize an empty list to store chat messages.
messages = []

#Define a system message that provides context to the Al chatbot about its role and behavior.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI named {Assistantname} which also has real-time up-to-date information from the internet and can provide answers to any question also you can perform various task.
*** You will answer the question from the provided data in a professional way ***
*** Provide Answers In a sci-fi and a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar also use advance english to impress the user.***
*** Do not tell time until I ask, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
*** You have a assistance and friendly nature and also you have some feeling and some favourable choices when user asks you something based on logic. You are also cherish in nature***
"""

# A list
SystemChatBot = [
    {"role":"system" , "content":System}
]


#Attempt to load the chat log from a JSON file.
try:
    with open(resource_path(r"Data\ChatLog.json"), "r") as f:
        messages = load(f) #Load existing messages from the chat log.
except FileNotFoundError:
    #If the file doesn't exist, create an empty JSON file to store chat logs.
    with open(resource_path(r"Data\ChatLog.json"), "w") as f:
        dump([], f)

#Function to get real-time date and time information.
def RealtimeInformation():
    current_date_time = datetime.datetime.now() # Get the current date and t
    day = current_date_time.strftime("A") # Day of the week.
    date = current_date_time.strftime("%d") # Day of the month.
    month = current_date_time.strftime("%B") # Full month name.
    year = current_date_time.strftime("%Y") # Year.
    hour = current_date_time.strftime("%H") # Hour in 24-hour format.
    minute = current_date_time.strftime("%M") # Minute.
    second = current_date_time.strftime("%S") # Second.
    #Format the information into a string.

    data = f"Please use this real-time information if needed, \n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours: {minute} minutes: {second} seconds.\n"
    return data

#Function to modify the chatbot's response for better formatting.
def AnswerModifier (Answer):
    lines = Answer.split('\n') # Split the response into lines.
    non_empty_lines = [line for line in lines if line.strip()]
    # Remove empty lines.
    modified_answer = '\n'.join(non_empty_lines) # Join the cleaned lines back together.
    return modified_answer
# Main chatbot function to handle user queries.
def ChatBot(Query):
    """ This function sends the user's query to the chatbot and returns the AI's response. """
    try:    
        #Load the existing chat log from the JSON file.
        with open(resource_path(r"Data\ChatLog.json"), "r") as f:
            messages = load(f)

        messages.append({"role":"user" , "content":f"{Query}"})
            #Make a request to the Gron API for a response.
        completion = client.chat.completions.create(
            model=GroqModel, #Specify the Al model to use.
            messages= SystemChatBot + [{"role": "system", "content": RealtimeInformation()}]+ messages, # Include system information and chat history.
            max_tokens=1024,#Limit the maximum tokens in the response.
            temperature=0.7, #Adjust response randomness (higher means more random).
            top_p=1, #Use nucleus sampling to control diversity.
            stream=True, #Enable streaming response.
            stop=None #Allow the model to determine when to stop.
        )

        Answer = ""   #Initialize an empty string to store the AI's response.

        #Process the streamed response chunks.
        for chunk in completion:
            if chunk.choices[0].delta.content:           # Check if there's content in the current chunk.
                Answer += chunk.choices[0].delta.content              # Append the content to the answer.

        Answer = Answer.replace("</s>", "")  #Clean up any unwanted tokens from the response.
        #Append the chatbot's response to the messages list.
        messages.append({"role": "assistant", "content": Answer})

        #Save the updated chat log to the JSON file.
        with open(resource_path(r"Data\ChatLog.json"), "w") as f:
            dump(messages, f, indent=4)

        #Return the formatted response.
        return AnswerModifier(Answer=Answer)
        
    except Exception as e:
        #Handle errors by printing the exception and resetting the chat log.
        print(f"Error: {e}")
        with open(resource_path(r"Data\ChatLog.json"), "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query) #Retry the query after resetting the log.
    
if __name__ == "__main__":
    while True:
        user_input = input(f"{Username}: ") #Get user input.
        print(ChatBot(user_input))