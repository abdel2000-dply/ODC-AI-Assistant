from src.utils.utils import recognize_speech_from_mic

def main():
    print("Starting speech recognition test...")
    recognized_text = recognize_speech_from_mic()
    if recognized_text:
        print(f"Recognized Text: {recognized_text}")
    else:
        print("No speech recognized.")

if __name__ == "__main__":
    main()
