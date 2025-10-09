import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values
import threading
import sys
import time
from queue import Queue
from groq import Groq
import json


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Load environment variables from a .env file
env_vars = dotenv_values(resource_path(".env"))

# Your Assistant Voice (default to a valid string if not found in .env)
AssistantVoice = env_vars.get("AssistantVoice", "en-CA-liamNeural")
VOICE = AssistantVoice

# Get Groq API key from environment variables
GROQ_API_KEY = env_vars.get("GroqAPIKey", "")
GroqModel = env_vars.get("GroqModel", "")

# Ensure AssistantVoice is a string
if not isinstance(AssistantVoice, str) or not AssistantVoice:
    raise ValueError("AssistantVoice must be a valid string.")

# Initialize Groq client
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    print("\033[93mWarning: GROQ_API_KEY not found in .env file. Stop detection will be basic.\033[0m")
    groq_client = None

# Global variables for TTS queue system
tts_queue = Queue()
stop_all_tts = False
current_tts_thread = None
queue_worker_running = False
file_monitor_thread = None
stop_monitoring = False

def analyze_stop_command(text):
    """Use Groq API to analyze if the stop command is meant for the assistant"""
    global groq_client
    
    if not groq_client:
        # Fallback to basic detection if no API key
        return 'stop' in text.lower() and ('jarvis' in text.lower() or 'assistant' in text.lower())
    
    try:
        prompt = f"""
        You are an AI assistant analyzer. Your job is to determine if a user's sentence contains a command to stop an AI assistant (like Jarvis) from speaking or performing a task.

        Analyze this sentence: "{text}"

        Consider these scenarios:
        - "stop" or "jarvis stop" or "stop talking" = TRUE (command to stop assistant)
        - "stop the music" or "stop playing" = TRUE (command to stop assistant actions)
        - "I need to stop at the store" = FALSE (not a command to assistant)
        - "The stop sign was red" = FALSE (not a command to assistant)
        - "Stop what you're doing" = TRUE (command to stop assistant)
        - "Can you stop please" = TRUE (command to stop assistant)

        Respond with only "TRUE" if this is a command to stop the assistant, or "FALSE" if it's just normal conversation containing the word "stop" but not meant as a command.
        """
        
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=GroqModel,
            temperature=0.1,
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip().upper()
        
        if result == "TRUE":
            print(f"\033[92mGroq Analysis: '{text}' is a STOP command for assistant\033[0m")
            return True
        else:
            print(f"\033[94mGroq Analysis: '{text}' is NOT a stop command (normal conversation)\033[0m")
            return False
            
    except Exception as e:
        print(f"\033[91mError with Groq API: {e}\033[0m")
        print("\033[93mFalling back to basic stop detection...\033[0m")
        # Fallback to basic detection
        return 'stop' in text.lower() and ('jarvis' in text.lower() or 'assistant' in text.lower())

def monitor_input_file():
    """Monitor the input.txt file for stop commands"""
    global stop_all_tts, stop_monitoring
    
    input_file_path = resource_path("Data/input.txt")
    last_content = ""
    
    while not stop_monitoring:
        try:
            if os.path.exists(input_file_path):
                with open(input_file_path, 'r', encoding='utf-8') as file:
                    content = file.read().strip()
                    
                    if content and content != last_content:
                        print(f"\033[96mMonitoring detected: '{content}'\033[0m")
                        
                        # Check for explicit stop command marker
                        if content == "STOP_COMMAND_FOR_ASSISTANT":
                            print("\033[91mExplicit stop command detected! Terminating all TTS...\033[0m")
                            stop_all_tts = True
                            # Clear the queue
                            while not tts_queue.empty():
                                try:
                                    tts_queue.get_nowait()
                                except:
                                    break
                            # Stop current playback
                            if pygame.mixer.get_init():
                                pygame.mixer.music.stop()
                        
                        # Also check if it's a natural stop command
                        elif 'stop' in content.lower():
                            is_stop_command = analyze_stop_command(content)
                            if is_stop_command:
                                print("\033[91mIntelligent Stop command detected! Terminating all TTS...\033[0m")
                                stop_all_tts = True
                                # Clear the queue
                                while not tts_queue.empty():
                                    try:
                                        tts_queue.get_nowait()
                                    except:
                                        break
                                # Stop current playback
                                if pygame.mixer.get_init():
                                    pygame.mixer.music.stop()
                        
                        last_content = content
            
            time.sleep(0.1)  # Check every 100ms
            
        except Exception as e:
            time.sleep(0.1)
            continue

def start_file_monitoring():
    """Start monitoring the input.txt file for stop commands"""
    global file_monitor_thread, stop_monitoring
    
    stop_monitoring = False
    file_monitor_thread = threading.Thread(target=monitor_input_file, daemon=True)
    file_monitor_thread.start()
    print("\033[93mIntelligent file monitoring started for Data/input.txt\033[0m")

def stop_file_monitoring():
    """Stop file monitoring"""
    global stop_monitoring
    stop_monitoring = True

async def TextToAudioFile(text):
    """Asynchronous function to convert text to an audio file"""
    file_path = resource_path(r"Data\speech.mp3")
    data_dir = os.path.dirname(file_path)
    os.makedirs(data_dir, exist_ok=True)
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    print("Generating audio...")
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)
    print(f"Audio file saved: {file_path}")
    return file_path

def remove_file(file_path):
    """Remove file safely"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed file: {file_path}")
    except Exception as e:
        print(f"Error removing file: {e}")

def play_tts_audio(text):
    """Play TTS audio with stop monitoring"""
    global stop_all_tts
    
    if stop_all_tts:
        print("\033[91mTTS cancelled due to stop command!\033[0m")
        return
    
    pygame.mixer.init()
    try:
        file_path = asyncio.run(TextToAudioFile(text))
        
        if stop_all_tts:
            remove_file(file_path)
            print("\033[91mTTS cancelled during generation!\033[0m")
            return
        
        if os.path.exists(file_path):
            print("Playing TTS audio...")
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # Monitor playback and check for stop command
            while pygame.mixer.music.get_busy() and not stop_all_tts:
                pygame.time.Clock().tick(10)
                
            if stop_all_tts:
                pygame.mixer.music.stop()
                print("\033[91mTTS playback stopped by intelligent user command!\033[0m")
        
        remove_file(file_path)
        
    except Exception as e:
        print(f"Error during TTS playback: {e}")
    finally:
        pygame.mixer.quit()

def tts_queue_worker():
    """Worker thread that processes TTS queue"""
    global stop_all_tts, queue_worker_running
    
    queue_worker_running = True
    print("\033[92mTTS Queue Worker started\033[0m")
    
    while queue_worker_running:
        try:
            if not tts_queue.empty() and not stop_all_tts:
                text = tts_queue.get(timeout=1)
                print(f"\033[94mProcessing TTS from queue: '{text[:50]}...'\033[0m")
                play_tts_audio(text)
                tts_queue.task_done()
            else:
                time.sleep(0.1)
        except:
            time.sleep(0.1)
            continue
    
    print("\033[93mTTS Queue Worker stopped\033[0m")

def start_tts_queue_system():
    """Start the TTS queue system"""
    global current_tts_thread
    
    # Start file monitoring
    start_file_monitoring()
    
    # Start queue worker
    current_tts_thread = threading.Thread(target=tts_queue_worker, daemon=True)
    current_tts_thread.start()

def TextToSpeech(text, func=lambda x=None: True):
    """Main TTS function that adds text to queue"""
    global stop_all_tts, tts_queue
    
    if not text or not text.strip():
        return
    
    # Reset stop flag when new TTS is requested (unless it's a continuation)
    if not stop_all_tts:
        stop_all_tts = False
    
    # Process long text
    data = str(text).split(".")
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information."
    ]
    
    # If the text is very long, truncate it
    if len(data) > 4 and len(text) > 250:
        final_text = " ".join(text.split(".")[0:2]) + ". " + random.choice(responses)
    else:
        final_text = text
    
    print(f"\033[92mAdding to TTS queue: '{final_text[:50]}...'\033[0m")
    tts_queue.put(final_text)

def reset_tts_system():
    """Reset the TTS system (clear stop flag)"""
    global stop_all_tts
    stop_all_tts = False
    print("\033[96mTTS system reset - ready for new audio\033[0m")

def stop_all_tts_immediately():
    """Immediately stop all TTS"""
    global stop_all_tts
    stop_all_tts = True
    
    # Clear the queue
    while not tts_queue.empty():
        try:
            tts_queue.get_nowait()
        except:
            break
    
    # Stop current playback
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
    
    print("\033[91mAll TTS stopped immediately!\033[0m")

# Initialize the TTS system when module is imported
start_tts_queue_system()

# Main execution for testing
if __name__ == "__main__":
    try:
        while True:
            user_input = input("Enter text for TTS (or 'quit' to exit): ")
            if user_input.lower() in ['quit', 'exit']:
                break
            elif user_input.lower() == 'reset':
                reset_tts_system()
            elif user_input.lower() == 'stop':
                stop_all_tts_immediately()
            else:
                TextToSpeech(user_input)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        stop_file_monitoring()
        queue_worker_running = False