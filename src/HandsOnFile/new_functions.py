from pydub import AudioSegment
sound1 = AudioSegment.from_file("/home/ricardo/Downloads/lula-convert-file.wav", format="wav")
sound2 = AudioSegment.from_file("/home/ricardo/Downloads/lula-convert-file (1).wav", format="wav")

# sound1 6 dB louder
#louder = sound1 + 6
# sound1, with sound2 appended (use louder instead of sound1 to append the louder version)
combined = sound1 + sound2

# simple export
file_handle = combined.export("/home/ricardo/Downloads/joined_lula.mp3", format="mp3")