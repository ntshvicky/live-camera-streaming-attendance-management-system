# Rough
brew install portaudio # require for pyaudio
pip install pyaudio
pip install SpeechRecognition

# Step to work on it
## You can use your own logic base on your need
1. run create_database.py - to create sqlite database - one time use
2. run record_face.py - to record user face data, it will save face image in dataset folder, for better result; be near, go little far, move face up-down-right-left
3. run trainer.py - after recording run trainer to tell your model to recognize face data
4. run app.py - this is main application, run and work on web ui using flask.. 

Dont forget to install requirements.txt in virtualenv