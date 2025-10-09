#jarvis my file
from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDictonaryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus)
from Backend.ImageGeneration import ProcessImageRequestFromDataFile, stop_image_generation_immediately, reset_image_generation
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import StartContinuousListening, StopContinuousListening, CleanupWebDriver, analyze_stop_command
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech, reset_tts_system, stop_all_tts_immediately
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import sys
import threading
import json
import os

import sys
import os

# Start with greeting
threading.Thread(target=TextToSpeech, args=("Hello Sir! All systems active and alive! What can I assist you with today?",)).start()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller sets this
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

env_vars = dotenv_values(resource_path(".env"))

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}! How are you?
{Assistantname} : Hello {Username} I'm doing well, how can I help you today?
'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search" , "send message" , "whatsapp call" , "video call"]

# Global variables for continuous listening
continuous_listening_thread = None
listening_active = False

def ShowDefaultChatIfNoChats():
    File = open(resource_path(r"Data\ChatLog.json"), "r", encoding="utf-8")
    if len(File.read()) < 5:
        with open(TempDictonaryPath("Database.data"), "w", encoding="utf-8") as file:
            file.write("")

        with open(TempDictonaryPath("Responses.data"), "w", encoding="utf-8") as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    with open(resource_path(r"Data\ChatLog.json"), "r", encoding="utf-8") as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""

    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"

    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDictonaryPath("Database.data"), "w", encoding="utf-8") as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    File = open(TempDictonaryPath("Database.data"), "r", encoding="utf-8")
    Data = File.read()

    if len(str(Data)) > 0:
        lines = Data.split("\n")
        result = '\n'.join(lines)
        File.close()
        File = open(TempDictonaryPath("Responses.data"), "w", encoding="utf-8")
        File.write(result)
        File.close()

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

def ReadInputFile():
    """Read the current content from Data/input.txt"""
    try:
        input_file_path = resource_path("Data/input.txt")
        if os.path.exists(input_file_path):
            with open(input_file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        return ""
    except Exception as e:
        print(f"Error reading input file: {e}")
        return ""

def ClearInputFile():
    """Clear the Data/input.txt file"""
    try:
        input_file_path = resource_path("Data/input.txt")
        with open(input_file_path, 'w', encoding='utf-8') as file:
            file.write("")
    except Exception as e:
        print(f"Error clearing input file: {e}")

def StartContinuousListeningThread():
    """Start the continuous listening in a separate thread"""
    global continuous_listening_thread, listening_active
    
    if not listening_active:
        listening_active = True
        continuous_listening_thread = threading.Thread(target=StartContinuousListening, daemon=True)
        continuous_listening_thread.start()
        print("\033[92mContinuous listening thread started\033[0m")

def StopContinuousListeningThread():
    """Stop the continuous listening thread"""
    global listening_active
    
    if listening_active:
        listening_active = False
        StopContinuousListening()
        print("\033[93mContinuous listening thread stopped\033[0m")

def MainExecution():
    """Main execution function that processes queries"""
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    # Read query from input file
    Query = ReadInputFile()
    
    if not Query:
        return False
    
    # Check if it's a stop command - if so, don't process further
    if Query == "STOP_COMMAND_FOR_ASSISTANT":
        print("\033[91mStop command detected - stopping all operations and clearing input\033[0m")
        stop_all_tts_immediately()
        stop_image_generation_immediately()
        ClearInputFile()
        return False
    
    # Check if it's a natural stop command - if so, don't process further
    if 'stop' in Query.lower() and analyze_stop_command(Query):
        print(f"\033[91mIntelligent stop command detected: '{Query}' - stopping all operations and clearing input\033[0m")
        stop_all_tts_immediately()
        stop_image_generation_immediately()
        ClearInputFile()
        return False
    
    # Clear the input file since we're processing this query
    ClearInputFile()
    
    # Reset TTS and image generation systems for new interaction
    reset_tts_system()
    reset_image_generation()
    
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)

    print("")
    print(f"Decision: {Decision}")
    print("")

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])

    Merged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True
        
    for queries in Decision:
        if TaskExecution == False:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True

    if ImageExecution:
        with open(resource_path(r"Frontend/Files/ImageGeneration.data"), "w") as file:
            file.write(f"{ImageGenerationQuery},True")

        try:
            TextToSpeech("Generating Images sir! might take a moment...")
            ProcessImageRequestFromDataFile()
        except Exception as e:
            TextToSpeech("Facing error while Generating Images , Sir!")
            print(f"Error Generating Image: {e}")

    if G and R or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True
    
    else:
        for Queries in Decision:
            if "general " in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general ", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "realtime" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

            elif "exit" in Queries:
                QueryFinal = "Okay, Bye! Have a nice day!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                SetAssistantStatus("Answering...")
                os._exit(1)

def FirstThread(): 
    """Main thread that handles microphone status and query processing"""
    global listening_active
    last_input_content = ""
    
    while True:
        CurrentStatus = GetMicrophoneStatus()

        if CurrentStatus == "True":
            # Start continuous listening if not already active
            if not listening_active:
                StartContinuousListeningThread()
            
            # Check if there's new input to process
            current_input = ReadInputFile()
            if current_input and current_input != last_input_content:
                last_input_content = current_input
                MainExecution()
                
        else:
            # Stop continuous listening if microphone is off
            if listening_active:
                StopContinuousListeningThread()
                
            AIStatus = GetAssistantStatus()

            if "Available..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available...")

def SecondThread():
    """GUI thread"""
    GraphicalUserInterface()

# Initialize the system
InitialExecution()

if __name__ == "__main__":
    try:
        thread2 = threading.Thread(target=FirstThread, daemon=True)
        thread2.start()
        SecondThread()
    except KeyboardInterrupt:
        print("\nShutting down...")
        StopContinuousListeningThread()
        CleanupWebDriver()
    finally:
        # Cleanup on exit
        StopContinuousListeningThread()
        CleanupWebDriver()