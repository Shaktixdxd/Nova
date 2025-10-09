from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
from Backend.TextToSpeech import TextToSpeech as speak
import sys
from pipes import quote
import pyttsx3
import eel
import time
import pyautogui

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


env_vars = dotenv_values(resource_path(".env"))
GroqAPIKey = env_vars.get("GroqAPIKey")

classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "ZOLcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "05uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLa0e",
"LWkFKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"

client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need-don't hesitate to ask.",
]
messages = []

SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems, etc."}]

def GoogleSearch(Topic):
    search(Topic)
    return True

# Function to generate content using AI and save it to a file.
def Content(Topic):

    #Nested function to open a file in Notepad.
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File]) # Open the file in Notepad.

    # Nested function to generate content using the Al chatbot.
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})  # Add the user's prompt to messages
        from groq  import Groq#Import Groq for Al chat functionalities.
        #Initialize the Grog client with the API key.
        client = Groq(api_key=GroqAPIKey)

        completion = client.chat.completions.create(
            model="gemma2-9b-it",  # Specify the AI model
            messages=SystemChatBot + messages,  # Include system instructions and chat history
            max_tokens=2048,  # Limit the maximum tokens in the response
            temperature=0.7,  # Adjust response randomness
            top_p=1,  # Use nucleus sampling for response diversity
            stream=True,  # Enable streaming response
            stop=None  # Allow the model to determine stopping conditions
        )

        Answer = ""  # Initialize an empty string for the response

        # Process streamed response chunks
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content  # Append content to the response

        Answer = Answer.replace("</s>", "")  # Remove unwanted tokens from the response
        messages.append({"role": "assistant", "content": Answer})  # Add the AI's response to messages
        return Answer

        
    Topic = Topic.replace("Content ", "") # Remove "Content from the topic. 
    ContentByAI = ContentWriterAI(Topic) # Generate content using AI.

    # Save the generated content to a text file.
    with open(resource_path(rf"Data\{Topic.lower().replace(' ','_')}.txt"), "w", encoding="utf-8") as file: 
        file.write(ContentByAI) # Write the content to the file.
        file.close()
    
    OpenNotepad(resource_path(rf"Data\{Topic.lower().replace(' ','_')}.txt")) # Open the file in Notepad. 
    return True # Indicate success.

def YoutubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

def PlayYoutube(query):
    playonyt(query)
    return True

import requests
from bs4 import BeautifulSoup
from AppOpener import open as appopen
from webbrowser import open as webopen
import sqlite3





def findContact(query):    
    con = sqlite3.connect("jarvis.db")
    cursor = con.cursor()
    try:
        query = query.strip().split(' ')
        query = query[0]
        query = query.replace('.', '')
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str
        con.close()
        return mobile_number_str, query
    except Exception as e:
        print(e)
        con.close()
        return 0, 0


useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

def whatsApp(mobile_no, message, flag, name):
    jarvis_message = ""

    if flag == 'message':
        jarvis_message = f"Message sent successfully to {name}"
    elif flag == 'call':
        message = ''
        jarvis_message = f"Calling {name}"
    else:
        message = ''
        jarvis_message = f"Starting video call with {name}"

    encoded_message = message
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"
    full_command = f'start "" "{whatsapp_url}"'

    subprocess.run(full_command, shell=True)
    time.sleep(5)  # Give WhatsApp time to open
    subprocess.run(full_command, shell=True)

    if flag == 'message':
        pyautogui.press('enter')

    elif flag == 'call':
        location = pyautogui.locateOnScreen("Frontend/Graphics/voice_call.png", confidence=0.6)
        if location:
            pyautogui.moveTo(pyautogui.center(location), duration=0.5)
            pyautogui.click()
            time.sleep(1)
            pyautogui.click()
        else:
            print("Could not locate the voice call button.")

    elif flag == 'video call':
        location = pyautogui.locateOnScreen("Frontend/Graphics/video_call.png", confidence=0.6)
        if location:
            pyautogui.moveTo(pyautogui.center(location), duration=0.5)
            pyautogui.click()
            time.sleep(1)
            pyautogui.click()
        else:
            print("Could not locate the video call button.")

    return jarvis_message


def whatsapp_message(query):
    query = query.removeprefix("send message ")
    contact_no, name = findContact(query)
    print(contact_no, name)
    if(name == 0):
        print("No contacts found, Sir!")
        return
    query = query.replace(name , ' ' , 1)
    print(query)
    if(contact_no != 0):
        message = 'message'
        value = whatsApp(contact_no, query, message, name)
        print(value)
    else :
        print("There aren't any contacts yet, Sir!")

def whatsapp_call(query):
    query = query.removeprefix("whatsapp call ")
    contact_no, name = findContact(query) 
    print(contact_no, name)
    if(contact_no != 0):                   
        message = 'call'                    
        value = whatsApp(contact_no, query, message, name)
        print(value)
    else :
        print("There aren't any contacts yet, Sir!")

def whatsapp_video(query):
    query = query.removeprefix("video call ")
    contact_no, name = findContact(query) 
    if(contact_no != 0):                       
        message = 'video call'                 
        value = whatsApp(contact_no, query, message, name)
        print(value)
    else :
        print("There aren't any contacts yet, Sir!")

# whatsapp_video("video call scammer")

def OpenApp(app, sess=requests.session()):
    # Define known web fallbacks
    web_apps = {
    "youtube": "www.youtube.com", "facebook": "www.facebook.com", "github": "www.github.com", "youtube studio": "studio.youtube.com", "twitter": "www.twitter.com", "instagram": "www.instagram.com", "linkedin": "www.linkedin.com", "wikipedia": "www.wikipedia.org", "reddit": "www.reddit.com", "pinterest": "www.pinterest.com", "quora": "www.quora.com", "tumblr": "www.tumblr.com", "flickr": "www.flickr.com", "snapchat": "www.snapchat.com", "tiktok": "www.tiktok.com", "vimeo": "www.vimeo.com", "dropbox": "www.dropbox.com", "onedrive": "www.onedrive.com", "google drive": "drive.google.com", "icloud": "www.icloud.com", "amazon": "www.amazon.com", "ebay": "www.ebay.com", "alibaba": "www.alibaba.com", "netflix": "www.netflix.com", "hulu": "www.hulu.com", "disney plus": "www.disneyplus.com", "hbo max": "www.hbomax.com", "spotify": "www.spotify.com", "soundcloud": "www.soundcloud.com", "apple music": "www.apple.com/apple-music", "pandora": "www.pandora.com", "deezer": "www.deezer.com", "bandcamp": "www.bandcamp.com", "bbc": "www.bbc.com", "cnn": "www.cnn.com", "nytimes": "www.nytimes.com", "the guardian": "www.theguardian.com", "forbes": "www.forbes.com", "bloomberg": "www.bloomberg.com", "reuters": "www.reuters.com", "espn": "www.espn.com", "fox news": "www.foxnews.com", "nbc news": "www.nbcnews.com", "cbs news": "www.cbsnews.com", "abc news": "www.abcnews.go.com", "msnbc": "www.msnbc.com", "npr": "www.npr.org", "wsj": "www.wsj.com", "yahoo news": "news.yahoo.com", "buzzfeed": "www.buzzfeed.com", "huffpost": "www.huffpost.com", "canva": "www.canva.com", "chatgpt": "chat.openai.com", "slack": "www.slack.com", "trello": "www.trello.com", "asana": "www.asana.com", "zoom": "www.zoom.us", "skype": "www.skype.com", "microsoft teams": "www.microsoft.com/microsoft-teams", "google meet": "meet.google.com", "webex": "www.webex.com", "jira": "www.atlassian.com/software/jira", "notion": "www.notion.so", "airtable": "www.airtable.com", "monday": "www.monday.com", "clickup": "www.clickup.com", "dropbox paper": "www.dropbox.com/paper", "confluence": "www.atlassian.com/software/confluence", "figma": "www.figma.com", "adobe xd": "www.adobe.com/products/xd.html", "invision": "www.invisionapp.com", "microsoft word": "www.microsoft.com/microsoft-365/word", "google docs": "docs.google.com", "medium": "www.medium.com", "wordpress": "www.wordpress.com", "wix": "www.wix.com", "squarespace": "www.squarespace.com", "shopify": "www.shopify.com", "bigcommerce": "www.bigcommerce.com", "weebly": "www.weebly.com", "godaddy": "www.godaddy.com", "namecheap": "www.namecheap.com", "bluehost": "www.bluehost.com", "siteground": "www.siteground.com", "hostgator": "www.hostgator.com", "dreamhost": "www.dreamhost.com", "a2 hosting": "www.a2hosting.com", "inmotion hosting": "www.inmotionhosting.com", "digitalocean": "www.digitalocean.com", "linode": "www.linode.com", "aws": "aws.amazon.com", "azure": "azure.microsoft.com", "google cloud": "cloud.google.com", "heroku": "www.heroku.com", "gitlab": "www.gitlab.com", "bitbucket": "bitbucket.org", "codepen": "codepen.io", "jsfiddle": "jsfiddle.net", "repl.it": "repl.it", "stack overflow": "stackoverflow.com", "stackoverflow careers": "stackoverflow.com/jobs", "glassdoor": "www.glassdoor.com", "indeed": "www.indeed.com", "linkedin jobs": "www.linkedin.com/jobs", "monster": "www.monster.com", "simplyhired": "www.simplyhired.com", "angel.co": "angel.co", "github jobs": "jobs.github.com", "ziprecruiter": "www.ziprecruiter.com", "careerbuilder": "www.careerbuilder.com", "snagajob": "www.snagajob.com", "dice": "www.dice.com", "jobs": "www.jobs.com", "bamboohr": "www.bamboohr.com", "workday": "www.workday.com", "adp": "www.adp.com", "sap successfactors": "www.sap.com/products/hcm.html", "oracle hcm": "www.oracle.com/applications/human-capital-management", "zenefits": "www.zenefits.com", "paycor": "www.paycor.com", "paycom": "www.paycom.com", "gusto": "www.gusto.com", "square": "squareup.com", "stripe": "www.stripe.com", "paypal": "www.paypal.com", "venmo": "www.venmo.com", "cash app": "cash.app"
    }

    try:
        # Try opening as a native app
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True

    except Exception as e:
        print(f"[INFO] Native app not found or failed: {e}")

        app_lower = app.lower().strip()

        # Check for known web-based apps
        for key in web_apps:
            if key in app_lower:
                print(f"[INFO] Opening web version of '{key}'")
                webopen(web_apps[key])
                return True

        # Fallback to Google search
        print(f"[INFO] No known app matched '{app}'. Searching on Google...")

        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all("a", {"jsname": "UWckNb"})
            return [link.get("href") for link in links if link.get("href")]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            try:
                response = sess.get(url, headers=headers)
                if response.status_code == 200:
                    return response.text
            except Exception as e:
                print(f"[ERROR] Google search failed: {e}")
            return None

        html = search_google(app)
        links = extract_links(html)

        if links:
            print(f"[INFO] Opening Google result: {links[0]}")
            webopen("https://www.google.com" + links[0])
        else:
            print("[WARNING] No links found in search.")
            GoogleSearch(app)

        return True


def CloseApp(app):
    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        
        except:
            return False
        

def System(command):
    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume mute")

    def volume_up():
        keyboard.press_and_release("volume up")

    def volume_down():
        keyboard.press_and_release("volume down")

    if "mute" in command:
        mute()
    elif "unmute" in command:
        unmute()
    elif "volume up" in command:
        volume_up()
    elif "volume down" in command:
        volume_down()
    
    return True


async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        if command.startswith("open"):
            if "open it" in command:
                pass
            if "open file" == command:
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)
        
        elif command.startswith("general "):
            pass

        elif command.startswith("realtime "):
            pass


        elif command.startswith("send_message ") or command.startswith("send message "):
            whatsapp_message(command)
        elif command.startswith("whatsapp_call ") or command.startswith("whatsapp call "):
            whatsapp_call(command)
        elif command.startswith("video_call ") or command.startswith("video call "):
            whatsapp_video(command)


        elif command.startswith("close "):  
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)

        else:
            print(f"No Function found for {command}")

    results = await asyncio.gather(*funcs)

    for result in results: 
        if isinstance(result, str):
            yield result
        else:
            yield result

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
        
    return True

