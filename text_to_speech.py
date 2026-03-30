import pyttsx3

def speak(text):
    engine = pyttsx3.init()
    # Optional: slow down the reading rate slightly for clarity
    rate = engine.getProperty('rate')
    engine.setProperty('rate', 150)
    
    print(f"Commander: {text}")
    engine.say(text)
    engine.runAndWait()
