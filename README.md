# DOE Mod

An automatic [Science Bowl](https://science.osti.gov/wdts/nsb) moderator. Uses [ScibowlDB](https://scibowldb.com) to get questions, [Whisper](https://github.com/openai/whisper) for speech recognition, and ChatGPT for checking answers (when they can't be decided locally).

## Installation

This only works on Mac right now, but everything is cross-platform except the `say` command. The speech recognition runs locally and may take a bit on older Macs.

1. Create an [OpenAI API key](https://platform.openai.com/account/api-keys)
2. Run `open ~/.zshrc` in Terminal
3. Paste `export OPENAI_API_KEY='your-api-key-here'` at the bottom and save
4. Run `cd ~/Downloads && git clone https://github.com/ag8/doemod.git && cd doemod`
5. Run `brew install portaudio` (using [Homebrew](https://brew.sh/))
6. Run `pip install -r requirements.txt`

## Running

1. Run `python moderator_server.py`
2. Connect to the server on each device you want to buzz from

## Roadmap

Let us know what features you'd like to see prioritized!

- [ ] Proper equation reading
- [ ] Better speech synth with [StyleTTS2](https://github.com/yl4579/StyleTTS2)
- [ ] Option to call Whisper API
- [ ] Option to use local LLM to check answers
- [ ] Compete against LLMs for the buzzer
- [ ] Browser GUI
- [ ] Round settings (# of questions, categories)
- [ ] Quiz bowl
- [ ] Cross-platform support
- [ ] Potentially run in browser with [whisper.cpp WASM](https://whisper.ggerganov.com/)
