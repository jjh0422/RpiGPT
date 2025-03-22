import os
import numpy as np
import soundfile as sf
import speech_recognition as sr
import time
import torch

def remove_silence(audio_path, model, get_speech_timestamps, read_audio, threshold=0.01):
    """
    Silero VAD를 사용하여 음성 신호에서 무음 및 발성되지 않은 부분을 제거하는 함수
    """
    # 오디오 파일 읽기
    wav, sample_rate = sf.read(audio_path)
    wav = read_audio(audio_path, sampling_rate=sample_rate)

    # 음성 구간 탐지
    vad_start_time = time.time()
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=sample_rate, threshold=threshold)
    vad_end_time = time.time()
    vad_duration = vad_end_time - vad_start_time  # VAD 처리 시간 계산

    if len(speech_timestamps) == 0:
        return None, 0, vad_duration  # 무음 파일이면 None 반환

    # 음성 구간만 추출
    non_silent_audio = np.concatenate([wav[ts['start']:ts['end']] for ts in speech_timestamps])

    # 임시 파일 저장
    temp_output_path = "temp_processed.wav"
    sf.write(temp_output_path, non_silent_audio, sample_rate)

    return temp_output_path, len(wav) / sample_rate, vad_duration

def recognize_speech_from_wav(wav_file_path, model, get_speech_timestamps, read_audio):
    """
    구글 음성 인식 API를 사용하여 음성을 텍스트로 변환하고 RTF 계산
    """
    r = sr.Recognizer()

    # 무음 제거 및 처리된 파일 가져오기
    processed_wav_path, original_duration, vad_duration = remove_silence(wav_file_path, model, get_speech_timestamps, read_audio)

    if processed_wav_path is None:
        return "음성을 이해할 수 없습니다.", 0.0, vad_duration

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

    os.remove(processed_wav_path)
    return text, rtf, vad_duration, recognition_duration

def process_audio_files_in_folder(folder_path, output_text_file, model, get_speech_timestamps, read_audio):
    total_rtf = 0
    total_vad_time = 0
    total_recognition_time = 0
    file_count = 0
    start_time_total = time.time()

    with open(output_text_file, 'w', encoding='utf-8') as f:
        for filename in os.listdir(folder_path):
            if filename.endswith(".wav"):
                file_name_without_extension = os.path.splitext(filename)[0]
                wav_file_path = os.path.join(folder_path, filename)

                speech, samplerate = sf.read(wav_file_path)
                original_duration = len(speech) / samplerate

                start_time = time.time()
                recognized_text, rtf, vad_duration, recognition_duration = recognize_speech_from_wav(
                    wav_file_path, model, get_speech_timestamps, read_audio
                )
                end_time = time.time()
                total_duration = end_time - start_time

                f.write(f"{file_name_without_extension} {recognized_text}\n")

                if rtf > 0:
                    total_rtf += rtf
                    total_vad_time += vad_duration
                    total_recognition_time += recognition_duration
                    file_count += 1

                # 파일당 VAD 처리 시간과 총 처리 시간 출력
                print(f"파일: {filename}, VAD: {vad_duration:.6f}s, 음성 인식: {recognition_duration:.6f}s, 총 처리 시간: {total_duration:.6f}s")

    end_time_total = time.time()
    total_processing_time = end_time_total - start_time_total

    if file_count > 0:
        avg_rtf = total_rtf / file_count
        print(f"평균 RTF 값: {avg_rtf:.4f}")

    print(f"총 VAD 처리 시간: {total_vad_time:.6f}초")
    print(f"총 음성 인식 시간: {total_recognition_time:.6f}초")
    print(f"총 처리 시간: {total_processing_time:.6f}초")

def main():
    # Silero VAD 모델 및 함수 불러오기 (한 번만)
    model, utils = torch.hub.load('snakers4/silero-vad', 'silero_vad', trust_repo=True)

    get_speech_timestamps, _, read_audio, _, _ = utils

    folder_path = "300wav"
    output_text_file = "silero.txt"

    process_audio_files_in_folder(folder_path, output_text_file,
                                   model, get_speech_timestamps, read_audio)

if __name__ == "__main__":
    main()
