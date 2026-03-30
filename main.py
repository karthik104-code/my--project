import sys
import os
from dotenv import load_dotenv

# Import modules
from speech_to_text import listen_and_transcribe
from text_to_speech import speak
from brain import process_command

def main():
    load_dotenv()
    
    print("============== COMMANDER AI ==============")
    print("Press Ctrl+C to exit.")
    
    if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "your_api_key_here":
        print("CRITICAL: GEMINI_API_KEY not found in .env.")
        print("Please edit the .env file and add your key.")
    
    speak("System starting. I am online.")
    
    while True:
        try:
            # 1. Listen
            user_text = listen_and_transcribe(timeout=None, phrase_time_limit=10)
            
            # 2. Process
            if user_text:
                if user_text.lower() in ["exit command", "stop listening", "quit system", "goodbye commander"]:
                    speak("Shutting down. Goodbye.")
                    sys.exit(0)
                    
                response_text = process_command(user_text)
                
                # 3. Respond
                if response_text:
                    speak(response_text)
            
        except KeyboardInterrupt:
            print("\nExiting Commander...")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

if __name__ == "__main__":
    main()
