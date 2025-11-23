import datetime
import speech_recognition as sr
import wikipedia
import webbrowser
import os
from . import functions as f
from . import Gemini as g

class JarvisEngine:
    def __init__(self):
        self.is_active = True
        self._system_check()

    def _system_check(self):
        """Verify that essential components are available."""
        try:
            # Check if Gemini is configured
            g.load_api_key()
            print("System Check: Gemini API Key found.")
        except Exception as e:
            print(f"System Check Warning: Gemini API Key issue - {e}")

    def process_command(self, query, mode='ai', model_name='gemini-2.0-flash-lite'):
        """Process a text command and return the response text."""
        query = query.lower()
        response = ""

        # Global Commands (Work in any mode)
        if 'shutdown' in query or 'shut down' in query:
            response = "Shutting Down..."
            self.is_active = False
            return response

        # AI Mode: Route strictly to Gemini
        if mode == 'ai':
            try:
                response = g.gemini_chat(query, model_name=model_name)
            except Exception as e:
                response = f"Error connecting to Gemini: {e}"
            return response
            
        # Task Mode: Strict Task Execution ONLY
        # If we are here, mode is NOT 'ai' (it's 'task')
        print(f"Processing Task Mode Command: {query}")
        
        if 'wikipedia' in query:
             # ... existing logic ...
            f.pspk('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            try:
                results = wikipedia.summary(query, sentences=2)
                response = "According to Wikipedia: " + results
                f.pspk(response)
            except Exception as e:
                response = f"Could not find results on Wikipedia. Error: {e}"
                f.pspk(response)

        elif 'open youtube' in query:
            webbrowser.open("www.youtube.com")
            response = "Opening YouTube"
            f.pspk(response)

        elif 'open google' in query:
            webbrowser.open("www.google.com")
            response = "Opening Google"
            f.pspk(response)

        elif 'open stackoverflow' in query:
            webbrowser.open("www.stackoverflow.com")
            response = "Opening Stack Overflow"
            f.pspk(response)

        elif 'open amazon' in query:
            webbrowser.open("www.amazon.in")
            response = "Opening Amazon"
            f.pspk(response)

        elif 'open facebook' in query:
            webbrowser.open("www.facebook.com")
            response = "Opening Facebook"
            f.pspk(response)

        elif 'open instagram' in query:
            webbrowser.open("www.instagram.com")
            response = "Opening Instagram"
            f.pspk(response)

        elif 'open snapchat' in query:
            webbrowser.open("www.snapchat.com")
            response = "Opening Snapchat"
            f.pspk(response)
        
        elif 'open netflix' in query:
            webbrowser.open("www.netflix.com")
            response = "Opening Netflix"
            f.pspk(response)
        
        elif 'open reddit' in query:
            webbrowser.open("www.reddit.com")
            response = "Opening Reddit"
            f.pspk(response)

        elif 'open chatgpt' in query or 'open chat gpt' in query:
            webbrowser.open("www.openai.com/chatgpt")
            response = "Opening ChatGPT"
            f.pspk(response)

        elif 'open sonyl' in query or 'open sonyliv' in query:
            webbrowser.open("www.sonyliv.com")
            response = "Opening SonyLIV"
            f.pspk(response)

        elif 'open gmail' in query:
            webbrowser.open("www.gmail.com")
            response = "Opening Gmail"
            f.pspk(response)

        elif 'open protonmail' in query or 'open proton mail' in query:
            webbrowser.open("www.protonmail.com")
            response = "Opening ProtonMail"
            f.pspk(response)
        
        elif 'open e care' in query or 'open ecare' in query:
            webbrowser.open("https://app.franciscanecare.com/Portal/Dashboard")
            response = "Opening e-Care"
            f.pspk(response)
        
        elif 'play soft songs' in query: # plays music
            music_dir = "C:\\Users\\user\\Music\\Playlists\\SOFT SONGS.m3u8"
            if os.path.exists(music_dir):
                os.startfile(music_dir)
                response = "Playing soft songs"
            else:
                response = "Playlist not found."
            f.pspk(response)

        elif 'the time' in query: # says the present time
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            response = f"Sir, it's {strTime} right now"
            f.pspk(response)

        elif 'date' in query: # says today's date
            current_date = datetime.date.today()
            date = current_date.strftime("%Y-%m-%d")
            response = f"Sir, it's {date} today!"
            f.pspk(response)

        elif 'open' in query and 'v'in query and 's' in query and 'code' in query:
            fdir='C:\\Users\\user\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe'
            if os.path.exists(fdir):
                os.startfile(fdir)
                response = "Opening VS Code"
            else:
                response = "VS Code not found."
            f.pspk(response)

        elif 'open whatsapp' in query or 'open whats up' in query or 'open whats app' in query:
            fdir='C:\\Program Files\\WindowsApps\\5319275A.WhatsAppDesktop_2.2422.7.0_x64__cv1g1gvanyjgm\\WhatsApp.exe'
            # Note: WindowsApps folder is restricted, startfile might fail if permissions aren't right, but keeping logic same as main.py
            try:
                os.startfile("whatsapp:") # Try protocol handler first if possible, else fallback
            except:
                pass 
            # Reverting to original logic for path
            if os.path.exists(fdir):
                os.startfile(fdir)
                response = "Opening WhatsApp"
            else:
                response = "Opening WhatsApp via protocol"
                os.system("start whatsapp:")
            f.pspk(response)

        elif 'open telegram' in query:
            fdir='C:\\Program Files\\WindowsApps\\TelegramMessengerLLP.TelegramDesktop_5.0.1.0_x64__t4vj0pshhgkwm\\Telegram.exe'
            if os.path.exists(fdir):
                os.startfile(fdir)
                response = "Opening Telegram"
            else:
                response = "Telegram executable not found."
            f.pspk(response)
        
        elif 'open spotify' in query:
            fdir='C:\\Program Files\\WindowsApps\\SpotifyAB.SpotifyMusic_1.239.578.0_x64__zpdnekdrzrea0\\Spotify.exe'
            if os.path.exists(fdir):
                os.startfile(fdir)
                response = "Opening Spotify"
            else:
                response = "Spotify executable not found."
            f.pspk(response)

        elif 'open' in query and 'premere pro' in query:
            fdir='C:\\Program Files\\Adobe\\Adobe Premiere Pro 2023\\Adobe Premiere Pro.exe'
            if os.path.exists(fdir):
                os.startfile(fdir)
                response = "Opening Premiere Pro"
            else:
                response = "Premiere Pro not found."
            f.pspk(response)

        elif 'open brave' in query:
            fdir='C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'
            if os.path.exists(fdir):
                os.startfile(fdir)
                response = "Opening Brave Browser"
            else:
                response = "Brave Browser not found."
            f.pspk(response)

        elif 'open' in query and 'after effects' in query:
            fdir='C:\\Program Files\\Adobe\\Adobe After Effects 2023\\Support Files\\AfterFX.exe'
            if os.path.exists(fdir):
                os.startfile(fdir)
                response = "Opening After Effects"
            else:
                response = "After Effects not found."
            f.pspk(response)
        
        elif 'open bitdefender' in query:
            fdir='C:\\Program Files\\Bitdefender\\Bitdefender Security App\\seccenter.exe'
            if os.path.exists(fdir):
                os.startfile(fdir)
                response = "Opening Bitdefender"
            else:
                response = "Bitdefender not found."
            f.pspk(response)
        
        elif 'open'in query and 'word' in query:
            fdir='C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE'
            if os.path.exists(fdir):
                os.startfile(fdir)
                response = "Opening Word"
            else:
                response = "Word not found."
            f.pspk(response)

        elif 'open' in query and 'powerpoint' in query:
            fdir='C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE'
            if os.path.exists(fdir):
                os.startfile(fdir)
                response = "Opening PowerPoint"
            else:
                response = "PowerPoint not found."
            f.pspk(response)

        elif 'open' in query and 'proton' in query and 'vpn' in query or 'open protonvpn' in query:
            fdir='C:\\Program Files\\Proton\\VPN\\ProtonVPN.Launcher.exe'
            if os.path.exists(fdir):
                os.startfile(fdir)
                response = "Opening ProtonVPN"
            else:
                response = "ProtonVPN not found."
            f.pspk(response)

        elif 'open blue' in query and 'j' in query or 'open bluej' in query:
            fdir='C:\\Program Files\\BlueJ\\BlueJ.exe'
            if os.path.exists(fdir):
                os.startfile(fdir)
                response = "Opening BlueJ"
            else:
                response = "BlueJ not found."
            f.pspk(response)

        elif 'open idm' in query or 'open internet download manager'in query:
            fdir='C:\\Program Files (x86)\\Internet Download Manager\\IDMan.exe'
            if os.path.exists(fdir):
                os.startfile(fdir)
                response = "Opening IDM"
            else:
                response = "IDM not found."
            f.pspk(response)

        elif 'open minecraft' in query or 'open tlauncher' in query:
            fdir='C:\\Users\\user\\Desktop\\TLauncher.exe'
            if os.path.exists(fdir):
                os.startfile(fdir)
                response = "Opening Minecraft Launcher"
            else:
                response = "TLauncher not found."
            f.pspk(response)

        elif 'open discord' in query:
            fdir='C:\\Users\\user\\AppData\\Local\\Discord\\Update.exe'
            if os.path.exists(fdir):
                os.startfile(fdir)
                response = "Opening Discord"
            else:
                response = "Discord not found."
            f.pspk(response)

        elif 'open' in query and 'droidcam' in query or 'open droid cam' in query:
            fdir='C:\\Program Files (x86)\\DroidCam\\DroidCamApp.exe'
            if os.path.exists(fdir):
                os.startfile(fdir)
                response = "Opening DroidCam"
            else:
                response = "DroidCam not found."
            f.pspk(response)

        elif 'use' in query and 'gemini' in query:
            response = "Gemini mode is integrated directly. Just ask your question."
            f.pspk(response)
            # In the GUI version, we can just route everything to Gemini if it's not a command
            
        else:
            # If we are here, it means we are in Task Mode (AI mode returns early)
            # and no command matched.
            response = "Command not recognized in Task Mode."
            f.pspk(response)
                
        return response
