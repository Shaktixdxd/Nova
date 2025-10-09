from googlesearch import search
from groq import Groq # Importing the Groq library to use its API.
from json import load, dump # Importing functions to read and write JSON files.
import datetime # Importing the datetime module for real-time date and time information.
from dotenv import dotenv_values #Importing dotenv values to read environment variables from a .env file.
import os

from duckduckgo_search import DDGS
import sys
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

#Load environment variables from the env file.
env_vars = dotenv_values(resource_path(".env"))

#Retrieve environment variables for the chatbot configuration.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")
GroqModel = env_vars.get("GroqModel")

# Initialize the Groq client with the provided API key.
client = Groq(api_key=GroqAPIKey)

# Define the system instructions for the chatbot.
System = f"""{Assistantname} is an AI with real-time Google data. Respond clearly, professionally, and under 100 words. Always state info is real-time. No disclaimers, no suggestions — just direct, accurate answers."""

# Try to load the chat log from a JSON file, or create an empty one if it
try:
    with open(resource_path(r"Data\ChatLog.json"), "r") as f:
        pass
except:
    with open(resource_path(r"Data\ChatLog.json"), "w") as f:
        dump([], f)


def GoogleSearch(query):
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=5))
        Answer = ""
        for i in results:
            Answer += f"Title: {i['title']}\n"
            Answer += f"Description: {i['body']}\n\n"
        if len(Answer) >= 3000:
            Answer = Answer[:3000]
        print(Answer)
        return Answer
    except Exception as e:
        return f"Search failed: {str(e)}"

# Function to clean up the answer by removing empty lines.
def AnswerModifier (Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# Predefined chatbot conversation system message and an initial user message.
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to get real-time information like the current date and time.
def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data += f"Use This Real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Load the chat log and fetch only the last 4 messages (2 user + 2 assistant)
    with open(resource_path(r"Data\ChatLog.json"), "r") as f:
        full_messages = load(f)
        # Keep only the last 4 messages: 2 user prompts + 2 assistant responses
        messages = full_messages[-4:] if len(full_messages) >= 4 else full_messages

    # 🔍 Get fresh search results
    search_data = GoogleSearch(prompt)

    # 🧠 Prepare messages for the AI
    messages.append({"role": "user", "content": f"{prompt}"})
    # Inject search results into a system message
    system_message = Information() + "\nUse the following search results to answer the user's query:\n" + search_data
    suspie = SystemChatBot + [{"role": "system", "content": system_message}] + messages

    completion = client.chat.completions.create(
        model=GroqModel,
        messages=suspie,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )

    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    # Save chat log
    with open(resource_path(r"Data\ChatLog.json"), "w") as f:
        dump(messages, f, indent=4)

    if SystemChatBot:
        SystemChatBot.pop()

    return AnswerModifier(Answer=Answer)

# Main entry point of the program for interactive querying.
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
        # print(GoogleSearch(prompt))
