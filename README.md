# JARVIS 1.0

Welcome to **JARVIS 1.0**! This is a personal AI assistant web application powered by Google's Gemini AI. It allows you to interact with an intelligent assistant via voice or text, right from your browser.

## 🌟 Features

-   **Voice Interaction:** Speak to JARVIS and hear him reply.
-   **Smart Chat:** Text-based chat interface with history.
-   **Task Mode:** Special mode for executing specific commands.
-   **Modern UI:** A beautiful, dark-themed interface inspired by sci-fi aesthetics.
-   **Powered by Gemini:** Uses Google's advanced Gemini models for intelligence.

---

## 🛠️ Prerequisites

Before you begin, make sure you have the following installed on your computer:

1.  **Python:** You need Python installed (version 3.8 or higher is recommended).
    *   [Download Python Here](https://www.python.org/downloads/)
    *   *Note during installation:* Make sure to check the box that says **"Add Python to PATH"**.

---

## 🚀 Installation Guide

Follow these steps to get JARVIS running on your machine.

### 1. Download the Project
If you haven't already, download this project folder to your computer.

### 2. Open a Terminal
Open your command prompt (cmd), PowerShell, or terminal and navigate to the project folder.
*   **Tip:** You can open the folder in File Explorer, type `cmd` in the address bar at the top, and press Enter.

### 3. Create a Virtual Environment (Optional but Recommended)
It's good practice to create a virtual environment to keep your project dependencies isolated.
```bash
python -m venv .venv
```
*   **Activate the virtual environment:**
    *   **Windows:**
        ```bash
        .venv\Scripts\activate
        ```
    *   **Mac/Linux:**
        ```bash
        source .venv/bin/activate
        ```

### 4. Install Dependencies
Install the required Python libraries using the `requirements.txt` file.
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration (Important!)

JARVIS needs your Google Gemini API key to work.

1.  **Get your API Key:**
    *   Go to [Google AI Studio](https://aistudio.google.com/).
    *   Create a new API key.

2.  **Set up the Environment File:**
    *   In the project folder, you will find a file named `.env.example`.
    *   **Rename** this file to just `.env` (remove the `.example` part).
        *   *Note:* If you don't see file extensions, you might just see `.env` type file. You can also create a new text file, name it `.env`, and open it with Notepad.
    *   Open the `.env` file in a text editor (like Notepad or VS Code).
    *   You will see a line like this:
        ```
        GEMINI_API_KEY=YOUR_API_KEY_HERE
        ```
    *   Replace `YOUR_API_KEY_HERE` with the actual API key you copied from Google.
    *   It should look something like this:
        ```
        GEMINI_API_KEY=AIzaSyD...
        ```
    *   **Save** the file.

---

## ▶️ How to Run

1.  Make sure your virtual environment is activated (if you used one).
2.  Run the main application script:
    ```bash
    python Jarvis.py
    ```
3.  You should see output indicating the server is running, usually on `http://127.0.0.1:5000`.
4.  Open your web browser (Chrome is recommended) and go to:
    `http://127.0.0.1:5000`

Enjoy talking to JARVIS!

---

## 📜 License

This project is licensed under the **MIT License**.

```text
MIT License

Copyright (c) 2024 Mayuk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 👨‍💻 Credits

**Developed by Mayuk**
