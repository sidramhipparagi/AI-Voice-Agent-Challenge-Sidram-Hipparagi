import os
import speech_recognition as sr
from gtts import gTTS
import pygame
import requests
import json
from datetime import datetime
import tempfile
import random
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class RiverwoodVoiceAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.conversation_history = []
        self.recognizer = sr.Recognizer()
        self.language = "en"  # Default language
        self.user_name = None
        self.history_file = "conversation_history.json"
        
        # Construction site data for simulation
        self.construction_data = {
            "site_name": "Riverwood Residential Complex",
            "progress": random.randint(65, 75),
            "current_phase": "Foundation and Structure Work",
            "workers_today": random.randint(45, 60),
            "materials_delivered": ["Steel bars", "Cement bags", "Concrete mix"],
            "next_milestone": "Completion of 3rd floor slab",
            "weather": random.choice(["Clear and sunny", "Partly cloudy", "Good working conditions"])
        }
        
        # Load previous conversation history
        self.load_conversation_history()
    
    def load_conversation_history(self):
        """Load conversation history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversation_history = data.get('conversations', [])
                    print(f"\n[Loaded {len(self.conversation_history)} previous messages from history]")
        except Exception as e:
            print(f"Note: Could not load conversation history: {e}")
            self.conversation_history = []
    
    def save_conversation_history(self):
        """Save conversation history to file"""
        try:
            data = {
                'last_updated': datetime.now().isoformat(),
                'conversations': self.conversation_history
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n[Conversation history saved: {len(self.conversation_history)} messages]")
        except Exception as e:
            print(f"Warning: Could not save conversation history: {e}")
    
    def display_conversation_summary(self):
        """Display a summary of recent conversation history"""
        if not self.conversation_history:
            return
        
        print("\n" + "=" * 60)
        print("RECENT CONVERSATION HISTORY")
        print("=" * 60)
        
        # Show last 6 messages (3 exchanges)
        recent = self.conversation_history[-6:] if len(self.conversation_history) > 6 else self.conversation_history
        
        for msg in recent:
            role = "You" if msg['role'] == 'user' else "Agent"
            content = msg['content']
            # Truncate long messages
            if len(content) > 80:
                content = content[:77] + "..."
            print(f"{role}: {content}")
        
        if len(self.conversation_history) > 6:
            print(f"\n[...and {len(self.conversation_history) - 6} more messages]")
        
        print("=" * 60)
    
    def greet_user(self):
        """Greet the user in Hindi or English"""
        greetings = [
            "Hello! I'm your Riverwood AI assistant. How can I help you today?",
            "Namaste! Main aapki Riverwood AI assistant hoon. Aaj main aapki kaise madad kar sakti hoon?",
            "Hi there! Welcome to Riverwood. What can I do for you?",
            "Namaskar! Riverwood mein aapka swagat hai. Main aapki kya seva kar sakti hoon?"
        ]
        greeting = random.choice(greetings)
        print(f"\nAgent: {greeting}")
        self.speak(greeting)
        return greeting
    
    def listen(self):
        """Listen to user input via microphone"""
        print("\nListening... (Speak now)")
        with sr.Microphone() as source:
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("Processing speech...")
                
                # Try English first
                try:
                    text = self.recognizer.recognize_google(audio, language="en-IN")
                    self.language = "en"
                    return text
                except:
                    # Try Hindi
                    try:
                        text = self.recognizer.recognize_google(audio, language="hi-IN")
                        self.language = "hi"
                        return text
                    except:
                        return None
            except sr.WaitTimeoutError:
                print("No speech detected. Please try again.")
                return None
            except Exception as e:
                print(f"Error listening: {e}")
                return None
    
    def get_text_input(self):
        """Get text input from user"""
        text = input("\nYou (type your message or press Enter to speak): ").strip()
        return text if text else None
    
    def speak(self, text):
        """Convert text to speech and play it"""
        temp_file = None
        try:
            # Detect language for TTS
            tts_lang = "hi" if self.language == "hi" or any(ord(char) > 127 for char in text) else "en"
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
            
            # Generate speech
            tts = gTTS(text=text, lang=tts_lang, slow=False)
            tts.save(temp_file)
            
            # Initialize pygame mixer if not already initialized
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            # Play audio using pygame
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Wait for audio to finish playing
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Small delay to ensure file is released
            time.sleep(0.2)
            
        except Exception as e:
            print(f"TTS Error: {e}")
        
        finally:
            # Clean up temp file
            if temp_file and os.path.exists(temp_file):
                try:
                    pygame.mixer.music.unload()
                    time.sleep(0.1)
                    os.remove(temp_file)
                except Exception:
                    pass  # Ignore cleanup errors
    
    def get_llm_response(self, user_input):
        """Get response from LLM via OpenRouter"""
        try:
            # Check if asking for construction update
            construction_keywords = ["update", "progress", "site", "construction", "status", "work"]
            if any(keyword in user_input.lower() for keyword in construction_keywords):
                # Add construction context to the prompt
                user_input = f"{user_input}\n\nConstruction Site Data:\n" + json.dumps(self.construction_data, indent=2)
            
            # Prepare messages with conversation history
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful AI assistant for Riverwood Residential Complex construction site. 
                    You can speak both Hindi and English fluently. 
                    You help with construction updates, answer questions, and have casual conversations.
                    Keep responses conversational, brief (2-3 sentences), and friendly.
                    If user asks about construction updates, provide specific details from the data provided.
                    Remember previous conversation context."""
                }
            ]
            
            # Add conversation history (last 5 exchanges for context)
            for msg in self.conversation_history[-10:]:
                messages.append(msg)
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Call OpenRouter API
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "meta-llama/llama-3.3-8b-instruct:free", 
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 150
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result['choices'][0]['message']['content']
                
                # Store in conversation history
                self.conversation_history.append({"role": "user", "content": user_input})
                self.conversation_history.append({"role": "assistant", "content": assistant_message})
                
                return assistant_message
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                print(f"Error: {error_msg}")
                return "I'm having trouble connecting right now. Please try again."
                
        except Exception as e:
            print(f"LLM Error: {e}")
            return "I encountered an error. Could you please repeat that?"
    
    def run(self):
        """Main loop for the voice agent"""
        print("=" * 60)
        print("RIVERWOOD AI VOICE AGENT")
        print("=" * 60)
        print("\nInstructions:")
        print("- Press Enter to speak via microphone")
        print("- Type your message to chat via text")
        print("- Type 'history' to view conversation history")
        print("- Type 'clear history' to clear all history")
        print("- Type 'quit' or 'exit' to end the conversation")
        print("=" * 60)
        
        # Display recent conversation summary if exists
        if self.conversation_history:
            self.display_conversation_summary()
        
        # Greet the user
        self.greet_user()
        
        # Main conversation loop
        while True:
            # Get user input (text or voice)
            user_input = self.get_text_input()
            
            if user_input is None:
                # User pressed Enter - use voice input
                user_input = self.listen()
                if user_input is None:
                    continue
            
            # Check for special commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                # Save conversation history before exiting
                self.save_conversation_history()
                farewell = "Goodbye! Have a great day!" if self.language == "en" else "Namaste! Aapka din shubh ho!"
                print(f"\nAgent: {farewell}")
                self.speak(farewell)
                break
            
            # Command to view full history
            elif user_input.lower() == 'history':
                self.display_full_history()
                continue
            
            # Command to clear history
            elif user_input.lower() == 'clear history':
                confirm = input("Are you sure you want to clear all history? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    self.conversation_history = []
                    if os.path.exists(self.history_file):
                        os.remove(self.history_file)
                    print("\nConversation history cleared!")
                else:
                    print("\nHistory not cleared.")
                continue
            
            print(f"You: {user_input}")
            
            # Get LLM response
            print("Thinking...")
            response = self.get_llm_response(user_input)
            
            # Display and speak response
            print(f"\nAgent: {response}")
            self.speak(response)
            
            # Auto-save history every 5 messages
            if len(self.conversation_history) % 10 == 0:
                self.save_conversation_history()
        
        print("\n" + "=" * 60)
        print("Thank you for using Riverwood AI Voice Agent!")
        print("=" * 60)
    
    def display_full_history(self):
        """Display complete conversation history"""
        if not self.conversation_history:
            print("\nNo conversation history available.")
            return
        
        print("\n" + "=" * 60)
        print("COMPLETE CONVERSATION HISTORY")
        print(f"Total Messages: {len(self.conversation_history)}")
        print("=" * 60)
        
        for i, msg in enumerate(self.conversation_history, 1):
            role = "You" if msg['role'] == 'user' else "Agent"
            content = msg['content']
            print(f"\n[{i}] {role}:")
            print(f"    {content}")
        
        print("\n" + "=" * 60)
        input("\nPress Enter to continue...")
        print()


def main():
    # Load API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    # Initialize and run the agent
    agent = RiverwoodVoiceAgent(api_key)
    agent.run()


if __name__ == "__main__":
    main()

