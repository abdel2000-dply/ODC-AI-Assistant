# ODC-AI-Assistant

## Overview

ODC-AI-Assistant is an AI-powered assistant designed to help users interact with the Orange Digital Center. It provides functionalities such as speech recognition, text-to-speech, event scraping, and conversational AI using LangChain.

## Features

- **Speech Recognition**: Recognize speech from the microphone using Google's speech recognition API.
- **Text-to-Speech**: Convert text to speech using edge-tts and play it using mpv.
- **Event Scraping**: Scrape event details from the Orange Digital Center website using Selenium.
- **Conversational AI**: Handle conversations using LangChain and Cohere's language model.

## Setup Instructions

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/yourusername/ODC-AI-Assistant.git
    cd ODC-AI-Assistant
    ```

2. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Environment Variables**:
    - Create a `.env` file in the root directory.
    - Add your API keys and other environment variables:
        ```
        GROQ_API_KEY=your_groq_api_key
        COHERE_API_KEY=your_cohere_api_key
        ```

4. **Setup**:
    - Run the setup script for initial setup:
        ```sh
        python setup.py
        ```

## Usage

1. **Run the Scheduler**:
    - In one terminal, run:
        ```sh
        python run_scheduler.py
        ```

2. **Run the Main Application**:
    - In another terminal, run:
        ```sh
        python src/main.py
        ```

## Project Structure

```
ODC-AI-Assistant/
├── data/
│   └── odc_gen_infos.txt
├── src/
│   ├── assistant.py
│   ├── handlers/
│   │   └── langchain_handler.py
│   ├── utils/
│   │   ├── utils.py
│   │   └── event_scraper.py
│   └── main.py
├── requirements.txt
├── setup.py
├── run_scheduler.py
└── README.md
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.