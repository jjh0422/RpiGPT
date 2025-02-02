#전처리2

import os
import time
import librosa
import numpy as np
import soundfile as sf
import speech_recognition as sr


def remove_silence(audio_path, top_db=30):
    """
    음성 신호에서 무음 및 발성되지 않은 부분을 제거하는 함수 (패딩 추가)
    """
    y, sr = librosa.load(audio_path, sr=None)
    non_silent_intervals = librosa.effects.split(y, top_db=top_db, frame_length=2048, hop_length=512)

    buffer = int(0.01 * sr)  # 10ms padding 추가
    non_silent_audio = np.concatenate([
        y[max(0, start - buffer): min(len(y), end + buffer)] for start, end in non_silent_intervals
    ])

    temp_output_path = "temp_processed.wav"
    sf.write(temp_output_path, non_silent_audio, sr)
    return temp_output_path, len(non_silent_audio) / sr  # 음성 신호 길이 반환


def recognize_speech_from_wav(wav_file_path):
    """
    구글 음성 인식 API를 사용하여 음성을 텍스트로 변환하며, RTF 계산 추가
    """
    r = sr.Recognizer()
    processed_wav_path, utterance_duration = remove_silence(wav_file_path)  # 무음 제거 후 파일 사용

    with sr.AudioFile(processed_wav_path) as source:
        start_time = time.time()
        audio = r.record(source)
        read_time = time.time() - start_time

    try:
        start_inference = time.time()
        text = r.recognize_google(audio, language='ko-KR')
        inference_time = time.time() - start_inference
    except sr.UnknownValueError:
        text = "음성을 이해할 수 없습니다."
        inference_time = 0
    except sr.RequestError as e:
        text = f"Google 음성 인식 서비스에 접근할 수 없습니다: {e}"
        inference_time = 0

    os.remove(processed_wav_path)  # 임시 파일 삭제

    total_processing_time = read_time + inference_time
    rtf = total_processing_time / utterance_duration if utterance_duration > 0 else 0

    return text, rtf, total_processing_time


def process_audio_files_in_folder(folder_path, output_text_file):
    total_rtf = 0
    file_count = 0

    with open(output_text_file, 'w', encoding='utf-8') as f:
        for filename in os.listdir(folder_path):
            if filename.endswith(".wav"):
                file_name_without_extension = os.path.splitext(filename)[0]
                wav_file_path = os.path.join(folder_path, filename)
                recognized_text, rtf, processing_time = recognize_speech_from_wav(wav_file_path)

                total_rtf += rtf
                file_count += 1

                f.write(f"{file_name_without_extension} {recognized_text}\n")
                print(f"{filename}: RTF = {rtf:.4f}, Processing Time = {processing_time:.2f}s")

    if file_count > 0:
        avg_rtf = total_rtf / file_count
        print(f"\n평균 RTF: {avg_rtf:.4f}")


def main():
    folder_path = "300wav"
    output_text_file = "recognized_texts7.txt"
    process_audio_files_in_folder(folder_path, output_text_file)


if __name__ == "__main__":
    main()
