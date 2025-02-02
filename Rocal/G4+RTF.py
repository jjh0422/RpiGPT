import os
import librosa
import numpy as np
import soundfile as sf
import speech_recognition as sr
import time


def remove_silence(audio_path, top_db=20):
    """
    음성 신호에서 무음 및 발성되지 않은 부분을 제거하는 함수
    """
    y, sr = librosa.load(audio_path, sr=None)
    non_silent_intervals = librosa.effects.split(y, top_db=top_db)

    if len(non_silent_intervals) == 0:
        return None, 0  # 무음 파일이면 None 반환

    non_silent_audio = np.concatenate([y[start:end] for start, end in non_silent_intervals])

    # 임시 파일 저장
    temp_output_path = "temp_processed.wav"
    sf.write(temp_output_path, non_silent_audio, sr)

    return temp_output_path, len(y) / sr  # 원본 음성 길이 반환


def recognize_speech_from_wav(wav_file_path):
    """
    구글 음성 인식 API를 사용하여 음성을 텍스트로 변환하고 RTF 계산
    """
    r = sr.Recognizer()

    # 무음 제거 및 처리된 파일 가져오기
    processed_wav_path, utterance_duration = remove_silence(wav_file_path)

    if processed_wav_path is None:  # 음성이 전부 무음일 경우
        return "음성을 이해할 수 없습니다.", 0.0

    start_time = time.time()

    with sr.AudioFile(processed_wav_path) as source:
        read_start = time.time()
        audio = r.record(source)  # 오디오 로딩
        read_time = time.time() - read_start

        inference_start = time.time()
        try:
            text = r.recognize_google(audio, language='ko-KR')
        except sr.UnknownValueError:
            text = "음성을 이해할 수 없습니다."
        except sr.RequestError as e:
            text = f"Google 음성 인식 서비스에 접근할 수 없습니다: {e}"
        inference_time = time.time() - inference_start

    total_time = time.time() - start_time
    decoding_time = total_time - (read_time + inference_time)

    # RTF 계산 (utterance_duration이 0일 경우 대비)
    rtf = (read_time + inference_time + decoding_time) / utterance_duration if utterance_duration > 0 else 0.0

    os.remove(processed_wav_path)  # 임시 파일 삭제
    return text, rtf


def process_audio_files_in_folder(folder_path, output_text_file):
    total_rtf = 0
    file_count = 0

    with open(output_text_file, 'w', encoding='utf-8') as f:
        for filename in os.listdir(folder_path):
            if filename.endswith(".wav"):
                file_name_without_extension = os.path.splitext(filename)[0]
                wav_file_path = os.path.join(folder_path, filename)

                recognized_text, rtf = recognize_speech_from_wav(wav_file_path)
                f.write(f"{file_name_without_extension} {recognized_text} (RTF: {rtf:.4f})\n")

                if rtf > 0:  # 유효한 RTF 값만 합산
                    total_rtf += rtf
                    file_count += 1

    if file_count > 0:
        avg_rtf = total_rtf / file_count
        print(f"평균 RTF: {avg_rtf:.4f}")


if __name__ == "__main__":
    folder_path = "300wav"
    output_text_file = "recognized_texts6.txt"

    process_audio_files_in_folder(folder_path, output_text_file)
