import os
import librosa
import numpy as np
import soundfile as sf
import speech_recognition as sr
import time

def remove_silence(audio_path, top_db=30):
    """
    음성 신호에서 무음 및 발성되지 않은 부분을 제거하는 함수
    """
    # VAD 처리 시작 시간 기록
    vad_start_time = time.time()

    y, sr = librosa.load(audio_path, sr=None)
    non_silent_intervals = librosa.effects.split(y, top_db=top_db)

    if len(non_silent_intervals) == 0:
        return None, 0, 0, 0  # 무음 파일이면 None 반환

    non_silent_audio = np.concatenate([y[start:end] for start, end in non_silent_intervals])

    # 임시 파일 저장
    temp_output_path = "temp_processed.wav"
    sf.write(temp_output_path, non_silent_audio, sr)

    # VAD 처리 종료 시간 기록
    vad_end_time = time.time()
    vad_duration = vad_end_time - vad_start_time  # VAD 처리 시간 계산

    return temp_output_path, len(y) / sr, len(non_silent_audio) / sr, vad_duration  # 원본 음성 길이와 무음 제거 후 길이 반환

def recognize_speech_from_wav(wav_file_path):
    """
    구글 음성 인식 API를 사용하여 음성을 텍스트로 변환하고 RTF 계산
    """
    r = sr.Recognizer()

    # 무음 제거 및 처리된 파일 가져오기
    processed_wav_path, original_duration, vad_duration, vad_time = remove_silence(wav_file_path)

    if processed_wav_path is None:  # 음성이 전부 무음일 경우
        return "음성을 이해할 수 없습니다.", 0.0, vad_duration, vad_time

    start_time = time.time()

    with sr.AudioFile(processed_wav_path) as source:
        audio = r.record(source)

        try:
            text = r.recognize_google(audio, language='ko-KR')
        except sr.UnknownValueError:
            text = "음성을 이해할 수 없습니다."
        except sr.RequestError as e:
            text = f"Google 음성 인식 서비스에 접근할 수 없습니다: {e}"

    end_time = time.time()
    recognition_duration = end_time - start_time

    # 총 처리 시간 계산 (VAD 처리 시간 + 음성 인식 시간)
    total_duration = vad_duration + recognition_duration

    # RTF 계산 (original_duration이 0일 경우 대비)
    rtf = total_duration / original_duration if original_duration > 0 else 0.0

    os.remove(processed_wav_path)  # 임시 파일 삭제
    return text, rtf, vad_duration, recognition_duration

def process_audio_files_in_folder(folder_path, output_text_file):
    total_rtf = 0
    total_vad_time = 0
    total_recognition_time = 0
    file_count = 0
    start_time_total = time.time()  # 전체 처리 시작 시간 기록

    with open(output_text_file, 'w', encoding='utf-8') as f:
        for filename in os.listdir(folder_path):
            if filename.endswith(".wav"):
                file_name_without_extension = os.path.splitext(filename)[0]
                wav_file_path = os.path.join(folder_path, filename)

                # 음성 신호 길이 계산 (초 단위) - 실제 샘플레이트 사용
                speech, samplerate = sf.read(wav_file_path)
                original_duration = len(speech) / samplerate

                recognized_text, rtf, vad_duration, recognition_duration = recognize_speech_from_wav(wav_file_path)

                f.write(f"{file_name_without_extension} {recognized_text}\n")  # RTF 값 제거

                if rtf > 0:  # 유효한 RTF 값만 합산
                    total_rtf += rtf
                    total_vad_time += vad_duration
                    total_recognition_time += recognition_duration
                    file_count += 1

                # 파일당 VAD 처리 시간과 총 처리 시간 출력
                print(f"파일: {filename}, VAD: {vad_duration:.6f}s, 음성 인식: {recognition_duration:.6f}s, 총 처리 시간: {vad_duration + recognition_duration:.6f}s")

    end_time_total = time.time()  # 전체 처리 종료 시간 기록
    total_processing_time = end_time_total - start_time_total  # 총 처리 시간 계산

    if file_count > 0:
        avg_rtf = total_rtf / file_count
        print(f"평균 RTF: {avg_rtf:.4f}")

    print(f"총 VAD 처리 시간: {total_vad_time:.6f}초")
    print(f"총 음성 인식 시간: {total_recognition_time:.6f}초")
    print(f"총 처리 시간: {total_processing_time:.6f}초")  # 전체 처리 시간 출력

if __name__ == "__main__":
    folder_path = "300wav"
    output_text_file = "g4.txt"

    process_audio_files_in_folder(folder_path, output_text_file)
