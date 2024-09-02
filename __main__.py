import subprocess
import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import openai
import datetime
import random
import requests

from groq import Groq
from config import groq_api_key
from click import prompt

import requests

def get_weather(city):
    api_key = "e06cded6ccc37da50a23cbac20d44c76"
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    response = requests.get(base_url)

    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        weather_description = data['weather'][0]['description']
        say(f"The current temperature in {city} is {temp} degrees Celsius with {weather_description}.")
    elif response.status_code == 401:
        say("Sorry, your API key is invalid.")
    elif response.status_code == 404:
        say(f"Sorry, I couldn't find weather information for {city}.")
    else:
        say("Sorry, I couldn't retrieve the weather information.")


def extract_city_from_query(query):
    query = query.lower()
    if "weather in" in query:
        city = query.split("weather in")[-1].strip()
        return city
    return None

def tell_joke(query):
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!"
    ]
    say(random.choice(jokes))

chatStr = ""

def chat(query):
    global chatStr
    client = Groq(api_key=groq_api_key)

    chatStr += f"Shreya: {query}\nEureka: "

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": chatStr}],
            temperature=1,
            max_tokens=150,
            top_p=1,
            stream=True,
            stop=None,
        )

        text = ""
        for chunk in completion:
            content = getattr(chunk.choices[0].delta, 'content', None)
            if content is not None:
                text += content

        if "Sorry, I did not understand that." in text or "It seems like" in text:
            text = "I'm sorry, can you please clarify your question?"

        chatStr += f"{text}\n"
        say(text)

        if len(chatStr) > 1000:
            chatStr = chatStr[-1000:]

    except Exception as e:
        print(f"Error: {e}")
        chatStr += "Eureka: [Error in generating response]\n"

    return text


def ai(prompt):
    client = Groq(api_key=groq_api_key)
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    text = ""
    for chunk in completion:
        content = getattr(chunk.choices[0].delta, 'content', None)
        if content is not None:
            text += content

    if not os.path.exists("Openai"):
        os.mkdir("Openai")

    with open(f"Openai/{''.join(prompt.split('intelligence')[1:]).strip() }.txt", "w") as f:
        f.write(text)

def say(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)

    engine.say(text)
    engine.runAndWait()

def take_Command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            print("Recognising..")
            query = recognizer.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query
        except sr.UnknownValueError:
            return "Sorry, I did not understand that."
        except sr.RequestError:
            return "Sorry, there was an issue with the speech recognition service."


if __name__ == "__main__":
    print('Greetings from Eureka A.I!')
    say("Hello, I am Eureka A.I. How may I help you?")

    while True:
        print("\nListening...")
        query = take_Command()
        command_executed = False

        sites = [["youtube", "https://www.youtube.com"],
                ["wikipedia", "https://www.wikipedia.com"],
                ["google", "https://www.google.com"]]

        for site in sites:
            if f"open {site[0]}".lower() in query.lower():
                say(f"Opening {site[0]}...")
                webbrowser.open(site[1])
                command_executed = True
                break

        if "open music" in query.lower():
            musicPath = r"C:\Users\srika\Downloads\Dekha-Tenu.mp3"
            say("Opening music...")
            opener = "start" if os.name == "nt" else "xdg-open"
            subprocess.call([opener, musicPath], shell=True)
            command_executed = True

        elif "time" in query.lower():
            strfTime = datetime.datetime.now().strftime("%H:%M:%S")
            say(f"Mam the time is {strfTime}")
            command_executed = True

        elif "open my coding app" in query.lower():
            codePath = r"C:\Users\srika\OneDrive\Desktop\LeetCode.lnk"
            say("Opening code...")
            subprocess.run(['start', codePath], shell=True)
            command_executed = True

        elif "openai".lower() in query.lower():
            ai(prompt=query)
            command_executed = True

        elif "using artificial intelligence".lower() in query.lower():
            ai(prompt=query)
            say("Your response is being generated")
            command_executed = True

        elif "Eureka quit".lower() in query.lower():
            say("Goodbye!")
            exit()

        elif "reset chat".lower() in query.lower():
            chatStr = ""
            say("Chat has been reset.")
            command_executed = True

        elif "Joke".lower() in query.lower():
            tell_joke(query)
            command_executed = True

        elif "weather in" in query.lower():
            city = extract_city_from_query(query)
            get_weather(city)
            command_executed = True

        if not command_executed:
            print("Chatting...")
            chat(query)
