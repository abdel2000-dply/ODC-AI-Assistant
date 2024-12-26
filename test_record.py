from src.utils.utils import recognize_speech_from_mic

def main():
    while True:
        print("\nStarting speech recognition test...")
        recognized_text = recognize_speech_from_mic()
        if recognized_text:
            print(f"Recognized Text: {recognized_text}")
        else:
            print("No speech recognized.")
        
        choice = input("\nPress Enter to continue or 'q' to quit: ")
        if choice.lower() == 'q':
            break

if __name__ == "__main__":
    main()
