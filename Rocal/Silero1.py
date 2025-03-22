import os
import numpy as np
import soundfile as sf
import speech_recognition as sr
import time
import torch


def remove_silence(audio_path, model, get_speech_timestamps, read_audio, threshold=0.5):
    """
    Silero VAD를 사용하여 음성 신호에서 무음 및 발성되지 않은 부분을 제거하는 함수
    """
    # 오디오 파일 읽기
    wav = read_audio(audio_path, sampling_rate=16000)
    sample_rate = 16000

    # 음성 구간 탐지
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=sample_rate, threshold=threshold)

    if len(speech_timestamps) == 0:
        return None, 0  # 무음 파일이면 None 반환

    # 음성 구간만 추출
    non_silent_audio = np.concatenate([wav[ts['start']:ts['end']] for ts in speech_timestamps])

    # 임시 파일 저장
    temp_output_path = "temp_processed.wav"
    sf.write(temp_output_path, non_silent_audio, sample_rate)

    return temp_output_path, len(non_silent_audio) / sample_rate


def recognize_speech_from_wav(wav_file_path, model, get_speech_timestamps, read_audio, original_duration):
    """
    구글 음성 인식 API를 사용하여 음성을 텍스트로 변환하고 RTF 계산
    """
    r = sr.Recognizer()

    # 무음 제거 및 처리된 파일 가져오기
    processed_wav_path, _ = remove_silence(wav_file_path, model, get_speech_timestamps, read_audio)

    if processed_wav_path is None:
        return "음성을 이해할 수 없습니다.", 0.0

    start_time = time.time()

    with sr.AudioFile(processed_wav_path) as source:
        read_start = time.time()
        audio = r.record(source)
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

    # RTF 계산 (original_duration이 0일 경우 대비)
    rtf = (read_time + inference_time + decoding_time) / original_duration if original_duration > 0 else 0.0

    os.remove(processed_wav_path)
    return text, rtf


def process_audio_files_in_folder(folder_path, output_text_file, model, get_speech_timestamps, read_audio):
    total_rtf = 0
    file_count = 0
    start_time_total = time.time()

    with open(output_text_file, 'w', encoding='utf-8') as f:
        for filename in os.listdir(folder_path):
            if filename.endswith(".wav"):
                file_name_without_extension = os.path.splitext(filename)[0]
                wav_file_path = os.path.join(folder_path, filename)

                speech, samplerate = sf.read(wav_file_path)
                original_duration = len(speech) / samplerate

                recognized_text, rtf = recognize_speech_from_wav(
                    wav_file_path, model, get_speech_timestamps, read_audio, original_duration
                )
                f.write(f"{file_name_without_extension} {recognized_text}\n")

                if rtf > 0:
                    total_rtf += rtf
                    file_count += 1

    end_time_total = time.time()
    total_processing_time = end_time_total - start_time_total

    if file_count > 0:
        avg_rtf = total_rtf / file_count
        print(f"평균 RTF: {avg_rtf:.4f}")

    print(f"총 처리 시간: {total_processing_time:.2f}초")


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
