#G3에 전처리 추가

import os
import librosa
import numpy as np
import soundfile as sf
import speech_recognition as sr


def remove_silence(audio_path, top_db=20):
    """
    음성 신호에서 무음 및 발성되지 않은 부분을 제거하는 함수
    """
    y, sr = librosa.load(audio_path, sr=None)
    non_silent_intervals = librosa.effects.split(y, top_db=top_db)
    non_silent_audio = np.concatenate([y[start:end] for start, end in non_silent_intervals])

    # 임시 파일로 저장
    temp_output_path = "temp_processed.wav"
    sf.write(temp_output_path, non_silent_audio, sr)
    return temp_output_path


def recognize_speech_from_wav(wav_file_path):
    """
    구글 음성 인식 API를 사용하여 음성을 텍스트로 변환
    """
    r = sr.Recognizer()
    processed_wav_path = remove_silence(wav_file_path)  # 무음 제거 후 파일 사용

    with sr.AudioFile(processed_wav_path) as source:
        audio = r.record(source)

    try:
        text = r.recognize_google(audio, language='ko-KR')
    except sr.UnknownValueError:
        text = "음성을 이해할 수 없습니다."
    except sr.RequestError as e:
        text = f"Google 음성 인식 서비스에 접근할 수 없습니다: {e}"

    os.remove(processed_wav_path)  # 임시 파일 삭제
    return text


def process_audio_files_in_folder(folder_path, output_text_file):
    with open(output_text_file, 'w', encoding='utf-8') as f:
        for filename in os.listdir(folder_path):
            if filename.endswith(".wav"):
                file_name_without_extension = os.path.splitext(filename)[0]
                wav_file_path = os.path.join(folder_path, filename)
                recognized_text = recognize_speech_from_wav(wav_file_path)
                f.write(f"{file_name_without_extension} {recognized_text}\n")


if __name__ == "__main__":
    folder_path = "300wav"
    output_text_file = "recognized_texts5.txt"
    process_audio_files_in_folder(folder_path, output_text_file)
