AI Mode Logic:
- Input Method: Manual Microphone Toggle.
- Behavior:
  - User clicks the microphone button to start listening.
  - User clicks the microphone button again to stop listening.
  - While listening, transcribe speech to text.
  - When stopped, the transcribed text remains in the chat input box.
  - If the user edits the text in the chatbox, the next transcription (if any) or message sending should continue from the current text in the box.
  - The microphone should NOT listen in the background when not toggled on.

Task Mode Logic:
- Input Method: Always Listening (Background).
- Behavior:
  - System constantly listens for the wake word "Hey Jarvis".
  - Upon detecting "Hey Jarvis", the system activates to listen for a command.
  - The command spoken after "Hey Jarvis" should be captured.
  - The captured command must be displayed in the chat window as a sent message.
  - The assistant must process the command and display a reply in the chat window.
