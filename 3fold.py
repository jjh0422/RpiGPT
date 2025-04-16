import os
import shutil
import wave

# Create directories for the categories
os.makedirs('0-3_seconds', exist_ok=True)
os.makedirs('3-6_seconds', exist_ok=True)
os.makedirs('6_seconds_above', exist_ok=True)


# Function to get the duration of a wav file
def get_wav_duration(file_path):
    with wave.open(file_path, 'r') as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        duration = frames / float(rate)
    return duration


# Path to the folder containing wav files
folder_path = '300wav'

# Iterate through each file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.wav'):
        file_path = os.path.join(folder_path, filename)
        duration = get_wav_duration(file_path)

        # Categorize and move the file based on its duration
        if duration <= 3:
            shutil.move(file_path, os.path.join('0-3_seconds', filename))
        elif 3 < duration <= 6:
            shutil.move(file_path, os.path.join('3-6_seconds', filename))
        else:
            shutil.move(file_path, os.path.join('6_seconds_above', filename))

print("Files have been categorized and moved successfully.")
