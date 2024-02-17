import speech_recognition as sr

# Initialize recognizer
r = sr.Recognizer()

# Use the default microphone as the audio source
with sr.Microphone() as source:
    print("Please say something:")
    # Listen for the first phrase and extract it into audio data
    audio_data = r.listen(source)
    print("Recognizing...")
    try:
        # Recognize speech using Google Web Speech API
        text = r.recognize_google(audio_data)
        #text = r.recognize_google(audio_data, language="ko-KR")
        #text = r.recognize_google(audio_data, language="vi-VN")
        #text = r.recognize_google(audio_data, language="te-IN")

        print("You said: " + text)
    except sr.UnknownValueError:
        print("Google Web Speech API could not understand the audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Web Speech API; {e}")
