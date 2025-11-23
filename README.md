# JARVIS 1.0

Welcome to **JARVIS 1.0**! This is a personal AI assistant web application powered by Google's Gemini AI. It allows you to interact with an intelligent assistant via voice or text, right from your browser.

## 🌟 Features

-   **Voice Interaction:** Speak to JARVIS and hear him reply.
-   **Smart Chat:** Text-based chat interface with history.
-   **Task Mode:** Special mode for executing specific commands.
-   **Modern UI:** A beautiful, dark-themed interface inspired by sci-fi aesthetics.
-   **Powered by Gemini:** Uses Google's advanced Gemini models for intelligence.

---

## � 1. Get your Gemini API Key (Required for both methods)

JARVIS needs your Google Gemini API key to work. You must do this first.

1.  **Get your API Key:**
    *   Go to [Google AI Studio](https://aistudio.google.com/). You need to use a 18+ Google account.
    *   Create a new API key.
    *   Copy the key, you will need it in the next steps.

---

## ⚡ 2. Replit Installation (Easy Mode)

This is the easiest way to run JARVIS without installing anything on your computer.

1.  **Import to Replit:**
    *   Go to [replit.com/import/github](https://replit.com/import/github).
    *   Paste the repository link: `https://github.com/MayukXT/JARVIS`
    *   Click **Import from GitHub**.

2.  **Follow Instructions:**
    *   Follow the instructions provided by the Replit Agent to set up the environment.

3.  **Configure API Key:**
    *   The Replit Agent should automatically ask you for the API key.
    *   **If the Replit Agent doesn't prompt you:**
        *   In Replit, look for "Secrets" (usually in the Tools section on the left).
        *   Add a new secret with the key `GEMINI_API_KEY` and paste your API key as the value.

4.  **Note:**
    *   You **do not** need to publish the app to use it. You can run it directly in the Replit editor.

---

## 💻 3. Local Installation (Best Mode)

Run JARVIS directly on your own machine for the best performance and control.

### �🛠️ Prerequisites

Before you begin, make sure you have the following installed on your computer:

1.  **Python:** You need Python installed (version 3.8 or higher is recommended).
    *   [Download Python Here](https://www.python.org/downloads/)
    *   *Note during installation:* Make sure to check the box that says **"Add Python to PATH"**.

### 🚀 Installation Steps

1.  **Download the Project:**
    *   If you haven't already, download this project folder to your computer.

2.  **Open a Terminal:**
    *   Open your command prompt (cmd), PowerShell, or terminal and navigate to the project folder.

3.  **Create a Virtual Environment (Optional but Recommended):**
    ```bash
    python -m venv .venv
    ```
    *   **Activate the virtual environment:**
        *   **Windows:** `.venv\Scripts\activate`
        *   **Mac/Linux:** `source .venv/bin/activate`

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up the Environment File:**
    *   In the project folder, you will find a file named `.env.example`.
    *   **Rename** this file to just `.env` (remove the `.example` part).
    *   Open the `.env` file in a text editor.
    *   Replace `YOUR_API_KEY_HERE` with your actual API key:
        ```
        GEMINI_API_KEY=AIzaSyD...
        ```
    *   **Save** the file.

### ▶️ How to Run

1.  Make sure your virtual environment is activated.
2.  Run the main application script:
    ```bash
    python Jarvis.py
    ```
3.  Open your web browser and go to: `http://127.0.0.1:5000`

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
