from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import threading
import time
from groq import Groq


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Load environment variables from the .env file.
env_vars = dotenv_values(resource_path(".env"))
# Get the input language setting from the environment variables, default to "en" if not set.
InputLanguage = env_vars.get("InputLanguage", "en")

# Get Groq API key for stop command analysis
GROQ_API_KEY = env_vars.get("GroqAPIKey", "")
GroqModel = env_vars.get("GroqModel", "")

# Initialize Groq client
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    print("\033[93mWarning: GROQ_API_KEY not found in .env file. Stop detection will be basic.\033[0m")
    groq_client = None

# Global variables for continuous listening control
listening_active = False
driver = None

# Debugging print to check if InputLanguage is loaded correctly.
print(f"Input Language: {InputLanguage}")

# Define the HTML code for the speech recognition interface.
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent = transcript;
            };

            recognition.onend = function() {
                if (recognition) {
                    recognition.start();
                }
            };
            recognition.start();
        }

        function stopRecognition() {
            if (recognition) {
                recognition.stop();
                recognition = null;
            }
            output.innerHTML = "";
        }
        
        function clearOutput() {
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace the language setting in the HTML code with the input language from the environment variables.
HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Write the modified HTML code to a file.
with open(resource_path(r"DataVoice.html"), "w") as f:
    f.write(HtmlCode)

# Get the current working directory.
current_dir = getattr(sys, '_MEIPASS', os.path.abspath("."))

# Generate the absolute file path for the HTML file.
Link = f"file:///{resource_path('DataVoice.html').replace(os.sep, '/')}"
print(f"Attempting to open file at: {Link}")

# Set Chrome options for the WebDriver.
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

# Initialize the Chrome WebDriver using the ChromeDriverManager.
service = Service(ChromeDriverManager().install())

# Define the path for temporary files.
TempDirPath = rf"{current_dir}/Frontend/Files"

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

def SetAssistantStatus(Status):
    """Function to set the assistant's status by writing it to a file."""
    try:
        os.makedirs(TempDirPath, exist_ok=True)
        with open(rf"{TempDirPath}/Status.data", "w", encoding="utf-8") as file:
            file.write(Status)
    except Exception as e:
        print(f"Error setting status: {e}")

def WriteToInputFile(text):
    """Writes the recognized speech text to Data/input.txt file."""
    try:
        data_dir = resource_path("Data")
        os.makedirs(data_dir, exist_ok=True)
        
        with open(resource_path("Data/input.txt"), "w", encoding="utf-8") as file:
            file.write(text)
        print(f"Text written to input.txt: {text}")
    except Exception as e:
        print(f"Error writing to input.txt: {e}")

def QueryModifier(Query):
    """Function to modify a query to ensure proper punctuation and formatting."""
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "wh"]

    # Check if the query is a question and add a question mark if necessary.
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '?'
        else:
            new_query += '?'
    else:
        # Add a period if the query is not a question.
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '.'
        else:
            new_query += '.'
    return new_query

def UniversalTranslator(Text):
    """Function to translate text into English using the mtranslate library."""
    try:
        english_translation = mt.translate(Text, "en", "auto")
        return english_translation.capitalize()
    except:
        return Text.capitalize()

def InitializeWebDriver():
    """Initialize the web driver and open the HTML file."""
    global driver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(Link)
    return driver

def StartContinuousListening():
    """Start continuous speech recognition that writes to input.txt."""
    global listening_active, driver
    
    if not driver:
        driver = InitializeWebDriver()
    
    listening_active = True
    print("\033[92mStarting continuous listening...\033[0m")
    
    # Start speech recognition
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "start"))).click()
        
        last_text = ""
        while listening_active:
            try:
                # Get the recognized text from the HTML output element
                current_text = driver.find_element(by=By.ID, value="output").text.strip()
                
                if current_text and current_text != last_text:
                    print(f"\033[96mHeard: {current_text}\033[0m")
                    
                    # Check if it's a stop command for the assistant
                    if analyze_stop_command(current_text):
                        print(f"\033[91mIntelligent Stop command detected: '{current_text}'\033[0m")
                        WriteToInputFile("STOP_COMMAND_FOR_ASSISTANT")
                        # Clear the output to continue listening for new commands
                        driver.execute_script("clearOutput();")
                        last_text = ""
                    else:
                        # Process the text normally
                        if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                            processed_text = QueryModifier(current_text)
                            WriteToInputFile(processed_text)
                        else:
                            SetAssistantStatus('Translating ...')
                            translated_text = QueryModifier(UniversalTranslator(current_text))
                            WriteToInputFile(translated_text)
                        
                        # Clear the output to continue listening for new commands
                        driver.execute_script("clearOutput();")
                        last_text = ""
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
            except Exception as e:
                time.sleep(0.1)
                continue
                
    except Exception as e:
        print(f"Error in continuous listening: {e}")

def StopContinuousListening():
    """Stop continuous speech recognition."""
    global listening_active, driver
    listening_active = False
    
    if driver:
        try:
            driver.find_element(by=By.ID, value="end").click()
            print("\033[93mContinuous listening stopped.\033[0m")
        except:
            pass

def SpeechRecognition():
    """Function to perform single speech recognition (for compatibility)."""
    global driver
    
    if not driver:
        driver = InitializeWebDriver()
    
    # Click start button
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "start"))).click()

    while True:
        try:
            # Get the recognized text from the HTML output element
            Text = driver.find_element(by=By.ID, value="output").text

            if Text:
                # Stop recognition by clicking the stop button
                driver.find_element(by=By.ID, value="end").click()
                return Text
        except:
            continue

def CleanupWebDriver():
    """Cleanup function to close the web driver."""
    global driver
    if driver:
        try:
            driver.quit()
            driver = None
        except:
            pass

# Main execution block for testing
if __name__ == "__main__":
    try:
        # Initialize and start continuous listening
        StartContinuousListening()
    except KeyboardInterrupt:
        print("\nStopping...")
        StopContinuousListening()
        CleanupWebDriver()