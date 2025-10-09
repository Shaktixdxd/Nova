# Backend/ImageGeneration.py

from random import randint
from PIL import Image
import requests
from dotenv import dotenv_values
import os
from time import sleep
from typing import Literal
from pathlib import Path
import sys
from groq import Groq

# === Constants ===
WRITABLE_DATA_DIR = Path.home() / "JarvisData"
WRITABLE_DATA_DIR.mkdir(parents=True, exist_ok=True)

ImageSize = Literal['auto', '1024x1024', '1536x1024', '1024x1536', '256x256', '512x512', '1792x1024', '1024x1792']

# Global variable to control image generation
stop_image_generation = False

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# === Env and A4F Setup ===
env_vars = dotenv_values(resource_path(".env"))
a4f_api_key = env_vars.get("A4FAPIKey", "")  # Get actual API key from .env
a4f_base_url = "https://api.a4f.co/v1"

# Get Groq API key for stop command analysis
GROQ_API_KEY = env_vars.get("GroqAPIKey", "")
GroqModel = env_vars.get("GroqModel", "")

# Initialize Groq client
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    print("\033[93mWarning: GROQ_API_KEY not found in .env file. Stop detection will be basic.\033[0m")
    groq_client = None

try:
    from openai import OpenAI
    A4F_AVAILABLE = True
    a4f_client = OpenAI(api_key=a4f_api_key, base_url=a4f_base_url) if a4f_api_key else None
except ImportError:
    A4F_AVAILABLE = False
    a4f_client = None
    print("Install A4F using: pip install a4f-local openai")

def check_stop_command():
    """Quick check for stop commands without continuous monitoring"""
    global stop_image_generation
    
    try:
        input_file_path = resource_path("Data/input.txt")
        if os.path.exists(input_file_path):
            with open(input_file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                
                if content:
                    # Check for explicit stop command marker
                    if content == "STOP_COMMAND_FOR_ASSISTANT":
                        print("\033[91mStop command detected! Stopping image generation...\033[0m")
                        stop_image_generation = True
                        return True
                    
                    # Check for natural stop commands
                    elif 'stop' in content.lower():
                        if analyze_stop_command(content):
                            print(f"\033[91mStop command detected: '{content}'\033[0m")
                            stop_image_generation = True
                            return True
        
        return stop_image_generation
        
    except Exception:
        return stop_image_generation

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
        return result == "TRUE"
            
    except Exception as e:
        print(f"\033[91mError with Groq API: {e}\033[0m")
        # Fallback to basic detection
        return 'stop' in text.lower() and ('jarvis' in text.lower() or 'assistant' in text.lower())

def open_images(prompt):
    """Open generated images with stop check"""
    if check_stop_command():
        print("\033[93mSkipping image opening due to stop command\033[0m")
        return
        
    prompt = prompt.replace(" ", "_")
    for i in range(1, 5):
        if check_stop_command():
            print("\033[93mImage opening stopped by user command\033[0m")
            break
            
        image_path = WRITABLE_DATA_DIR / f'generated_{prompt}{i}.jpg'
        if image_path.exists():
            try:
                Image.open(image_path).show()
                sleep(1)
            except Exception as e:
                print(f"Error opening image {i}: {e}")

def generate_image_with_a4f_single(prompt, image_number, size: ImageSize):
    """Generate single image with A4F - with stop checks"""
    if not a4f_client or check_stop_command(): 
        return False
        
    models = [
        "provider-5/gpt-image-1", "provider-5/dall-e-3",
        "provider-1/FLUX.1-schnell", "provider-2/FLUX.1-schnell",
        "provider-3/FLUX.1-schnell", "provider-5/FLUX.1 [schnell]",
        "provider-1/FLUX.1.1-pro"
    ]
    
    for model in models:
        if check_stop_command():
            print(f"\033[91mImage generation {image_number} stopped by user command\033[0m")
            return False
            
        try:
            response = a4f_client.images.generate(
                model=model,
                prompt=prompt,
                n=1,
                size=size,
                response_format="url"
            )
            
            if check_stop_command():
                print(f"\033[91mImage generation {image_number} stopped during API call\033[0m")
                return False
                
            image_url = response.data[0].url if response and response.data else None
            if image_url:
                res = requests.get(image_url, timeout=15)
                
                if check_stop_command():
                    print(f"\033[91mImage generation {image_number} stopped during download\033[0m")
                    return False
                    
                if res.status_code == 200:
                    filename = f"generated_{prompt.replace(' ', '_')}{image_number}.jpg"
                    with open(WRITABLE_DATA_DIR / filename, "wb") as f:
                        f.write(res.content)
                    return True
        except Exception: 
            if check_stop_command():
                return False
            continue
    return False

def generate_fallback_images(prompt, start_index=1, size: ImageSize = "1024x1024"):
    """Generate fallback images with stop checks"""
    if check_stop_command():
        print("\033[93mSkipping fallback image generation due to stop command\033[0m")
        return
        
    width, height = map(int, size.split('x')) if size != "auto" else (1024, 1024)
    
    for i in range(start_index, 5):
        if check_stop_command():
            print(f"\033[91mFallback image generation stopped at image {i}\033[0m")
            break
            
        try:
            url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width={width}&height={height}&seed={randint(0, 100000)}"
            res = requests.get(url, timeout=30)
            
            if check_stop_command():
                print(f"\033[91mFallback image {i} stopped during download\033[0m")
                break
                
            if res.status_code == 200:
                filename = f"generated_{prompt.replace(' ', '_')}{i}.jpg"
                with open(WRITABLE_DATA_DIR / filename, "wb") as f:
                    f.write(res.content)
                print(f"Fallback image {i} generated")
            sleep(1)
        except Exception as e:
            if check_stop_command():
                print(f"\033[91mFallback image {i} stopped due to error: {e}\033[0m")
                break
            print(f"Error in fallback gen {i}: {e}")

def GenerateImages(prompt: str, size: ImageSize = "1024x1024"):
    """Main function to generate images - simplified with stop checks"""
    global stop_image_generation
    
    print(f"\033[94mStarting image generation for: '{prompt}'\033[0m")
    
    # Check if stopped before starting
    if check_stop_command():
        print("\033[93mImage generation cancelled before starting\033[0m")
        return
    
    success = 0
    
    # Try A4F first if available
    if a4f_client and a4f_api_key:
        print("Using A4F...")
        if generate_image_with_a4f_single(prompt, 1, size):
            success = 1
            # Generate variations
            for i in range(2, 5):
                if check_stop_command():
                    print(f"\033[91mImage generation stopped at variation {i}\033[0m")
                    break
                if generate_image_with_a4f_single(f"{prompt}, variation {i}", i, size):
                    success += 1
    
    # Use fallback if needed and not stopped
    if success < 4 and not check_stop_command():
        print(f"Falling back for {4 - success} images")
        generate_fallback_images(prompt, start_index=success+1, size=size)
    
    # Open images if any were generated and not stopped
    if not check_stop_command():
        open_images(prompt)
        print(f"\033[92mImage generation completed!\033[0m")
    else:
        print("\033[93mImage generation interrupted by user command\033[0m")

def ProcessImageRequestFromDataFile():
    """Process image generation request from data file"""
    try:
        file_path = resource_path("Frontend/Files/ImageGeneration.data")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Check if file exists, if not create it
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("False,False")
            return
            
        with open(file_path, "r") as f:
            data = f.read().strip()
            
        if not data or "," not in data:
            print("Invalid ImageGeneration.data format.")
            return
            
        parts = data.split(",")
        prompt = parts[0].strip()
        status = parts[1].strip()
        size = parts[2].strip() if len(parts) > 2 else "1024x1024"
        
        if status != "True":
            return
            
        print(f"\033[94mProcessing image request: {prompt}, size: {size}\033[0m")
        
        # Generate images
        GenerateImages(prompt, size)
        
        # Reset to prevent regeneration
        with open(file_path, "w") as f:
            f.write("False,False")
        
    except Exception as e:
        print(f"[ImageGen Error] {e}")

def reset_image_generation():
    """Reset the image generation system"""
    global stop_image_generation
    stop_image_generation = False
    print("\033[96mImage generation system reset\033[0m")

def stop_image_generation_immediately():
    """Immediately stop image generation"""
    global stop_image_generation
    stop_image_generation = True
    print("\033[91mImage generation stopped immediately!\033[0m")

# Keep the automatic execution like the old code
if __name__ == "__main__":
    ProcessImageRequestFromDataFile()