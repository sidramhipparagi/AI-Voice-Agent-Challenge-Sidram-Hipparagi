# Riverwood AI Voice Agent

Hey! This is a voice assistant I built for construction site management. It speaks both Hindi and English, remembers your conversations, and can give you updates about what's happening on site.

## What It Does

Talk to it about construction updates - either by typing or speaking. It'll remember everything you talked about, even after you close and reopen it.

**Cool stuff:**
- Speaks and understands Hindi & English
- Voice input OR text input (your choice)
- Remembers past conversations
- Gives construction site updates
- Natural conversation flow

## Quick Setup

**1. Install the requirements:**
```bash
pip install -r requirements.txt
```

**2. Get a free API key:**
- Go to https://openrouter.ai/
- Sign up and grab an API key

**3. Create a `.env` file:**
```
OPENROUTER_API_KEY=your_key_here
```

**4. Run it:**
```bash
python voice_agent.py
```

That's it!

## How to Use It

When it starts, just talk to it:
- Type your message and hit Enter
- Or just press Enter to speak with your microphone
- Ask things like "What's the site progress?" or "Site ka update do"

**Special commands:**
- `history` - see all your past conversations
- `clear history` - wipe everything clean
- `quit` - exit (it auto-saves)

## Example Conversation

```
Agent: Hello! I'm your Riverwood AI assistant. How can I help you today?

You: What's happening on site today?
Agent: We're at 72% completion with 53 workers on site working on 
       Foundation and Structure Work. Weather is clear and sunny!

You: Site ka update do
Agent: Aaj hamari site pe 3rd floor ka kaam chal raha hai...
```

## Tech Stack

- Speech Recognition (Google)
- LLM via OpenRouter (Llama 3.3 8B - free)
- Text-to-Speech (Google TTS)
- Audio Playback (Pygame - reliable on Windows)
- Python 3.8+

## Notes

- Conversations save automatically to `conversation_history.json`
- It remembers the last 10 messages for context
- Works best with a decent microphone in a quiet room
- Uses free APIs so responses might take 1-3 seconds

## Troubleshooting

**Microphone not working?**
- Check your Windows privacy settings
- Make sure the microphone is plugged in

**API errors?**
- Double-check your API key in the `.env` file
- Make sure you have internet connection

**PyAudio installation issues on Windows?**
```bash
pip install pipwin
pipwin install pyaudio
```

---

Built for Riverwood Construction Management. Have fun chatting!
