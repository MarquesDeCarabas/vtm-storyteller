# 🎙️ Voice Narration Feature

## Overview

VTM Storyteller v3.1 now includes **AI-powered voice narration** using ElevenLabs Text-to-Speech technology. The Storyteller can narrate responses in a sensual, atmospheric voice perfect for the World of Darkness.

---

## Features

### 🔊 Voice Toggle Button
- Located next to the chat input field
- Click to enable/disable voice narration
- Visual feedback: 🔊 (ON) / 🔇 (OFF)
- Active state highlighted in red

### 🎭 Dual Language Support
- **English**: Serafina - Deep, sensual female voice
- **Spanish**: Rachel - Warm, expressive female voice
- Automatic language detection (future feature)

### 🎵 Automatic Playback
- Storyteller responses are automatically narrated when voice is ON
- Only one audio plays at a time (new responses stop previous audio)
- Clean audio cleanup after playback

---

## Configuration

### Environment Variable Required

Add the following environment variable to Railway:

```
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

### Getting an ElevenLabs API Key

1. Sign up at [ElevenLabs](https://elevenlabs.io/)
2. Navigate to your profile settings
3. Generate an API key
4. Copy the key to Railway environment variables

---

## Technical Details

### Selected Voices

**English Voice**:
- **Name**: Serafina - Flirty Sensual Temptress
- **Voice ID**: `EXAVITQu4vr4xnSDxMaL`
- **Characteristics**: Deep, smooth, velvety, captivating
- **Perfect for**: Seductress, siren, femme fatale characters

**Spanish Voice**:
- **Name**: Rachel
- **Voice ID**: `21m00Tcm4TlvDq8ikWAM`
- **Characteristics**: Warm, expressive, natural
- **Perfect for**: Storytelling and narration

### API Endpoints

#### `/tts` - Text to Speech
**Method**: POST  
**Body**:
```json
{
  "text": "Text to convert to speech",
  "language": "en"  // or "es"
}
```
**Returns**: Audio file (MP3)

#### `/tts/voices` - Get Available Voices
**Method**: GET  
**Returns**:
```json
{
  "en": {
    "voice_id": "EXAVITQu4vr4xnSDxMaL",
    "name": "Serafina",
    "description": "Deep, sensual female voice perfect for VTM storytelling"
  },
  "es": {
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "name": "Rachel",
    "description": "Warm, expressive female voice for Spanish narration"
  }
}
```

---

## Voice Settings

The TTS uses optimized settings for storytelling:

```javascript
{
  "stability": 0.5,           // Balance between consistency and expressiveness
  "similarity_boost": 0.75,   // How similar to the original voice
  "style": 0.5,               // Style exaggeration
  "use_speaker_boost": true   // Enhanced clarity
}
```

---

## Usage

1. **Enable Voice**: Click the 🔊 button next to the chat input
2. **Send Message**: Type your message and send it to the Storyteller
3. **Listen**: The Storyteller's response will be narrated automatically
4. **Disable**: Click the 🔇 button to turn off narration

---

## Troubleshooting

### Voice Not Working

1. **Check API Key**: Ensure `ELEVENLABS_API_KEY` is set in Railway
2. **Check Browser Console**: Look for TTS errors in the developer console
3. **Check Audio Permissions**: Ensure your browser allows audio playback
4. **Check Network**: Verify the `/tts` endpoint is accessible

### Audio Quality Issues

- The voice uses ElevenLabs' Multilingual v2 model
- Quality depends on text length and complexity
- Shorter responses generally have better quality

---

## Future Enhancements

- [ ] Automatic language detection based on response
- [ ] Voice speed control
- [ ] Voice selection (choose different voices)
- [ ] Volume control
- [ ] Download narration as MP3
- [ ] Voice for dice roll results
- [ ] Character-specific voices

---

## Credits

**Voice Technology**: ElevenLabs  
**Selected Voices**: Serafina, Rachel  
**Integration**: VTM Storyteller v3.1

---

**Enjoy immersive voice narration in your VTM chronicles!** 🧛🎙️

