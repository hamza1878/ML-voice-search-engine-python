import pyttsx3

engine = pyttsx3.init()

voices = engine.getProperty('voices')

def speak(text, lang):
    for voice in voices:
        if lang in voice.languages or lang.lower() in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    engine.say(text)
    engine.runAndWait()

# ENGLISH
speak("Hello, how are you?", "english")

# FRENCH
speak("Bonjour, comment ça va ?", "french")

# ARABIC (may depend on installed voices)
speak("مرحبا كيف حالك", "arabic")