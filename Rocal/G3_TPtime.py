#원시데이터 사용, rtf와 총처리시간 측정

import os
import speech_recognition as sr
import time
import soundfile as sf


def recognize_speech_from_wav(wav_file_path):
    # 음성 인식기 초기화
    r = sr.Recognizer()

    # WAV 파일 로드
    with sr.AudioFile(wav_file_path) as source:
        audio = r.record(source)  # 전체 파일을 읽음

    try:
        # Google 음성 인식 API를 사용하여 한글 텍스트로 변환
        text = r.recognize_google(audio, language='ko-KR')
    except sr.UnknownValueError:
        text = "음성을 이해할 수 없습니다."
    except sr.RequestError as e:
        text = f"Google 음성 인식 서비스에 접근할 수 없습니다: {e}"

    return text


def process_audio_files_in_folder(folder_path, output_text_file):
    rtf_sum = 0  # RTF 값을 합산하기 위한 변수
    num_files = 0  # 파일 개수 카운트
    start_time_total = time.time()  # 전체 처리 시작 시간 기록

    with open(output_text_file, 'w', encoding='utf-8') as f:
        # 폴더 내의 모든 WAV 파일 처리
        for filename in os.listdir(folder_path):
            if filename.endswith(".wav"):
                num_files += 1
                file_name_without_extension = os.path.splitext(filename)[0]
                wav_file_path = os.path.join(folder_path, filename)

                # 음성 신호 길이 계산 (초 단위) - 실제 샘플레이트 사용
                speech, samplerate = sf.read(wav_file_path)
                total_utterance_duration = len(speech) / samplerate

                # 처리 시간 측정
                start_time = time.time()  # 처리 시작 시간
                recognized_text = recognize_speech_from_wav(wav_file_path)
                end_time = time.time()  # 처리 종료 시간

                total_duration = end_time - start_time  # 개별 파일 처리 시간

                # RTF 계산
                rtf = total_duration / total_utterance_duration if total_utterance_duration > 0 else 0
                rtf_sum += rtf

                # 결과 파일에 기록
                f.write(f"{file_name_without_extension} {recognized_text}\n")

    end_time_total = time.time()  # 전체 처리 종료 시간 기록
    total_processing_time = end_time_total - start_time_total  # 총 처리 시간 계산

    if num_files > 0:
        average_rtf = rtf_sum / num_files
        print(f"평균 RTF 값: {average_rtf:.4f}")

    print(f"총 처리 시간: {total_processing_time:.2f}초")  # 전체 처리 시간 출력


if __name__ == "__main__":
    folder_path = "300wav"         # 오디오 파일이 있는 폴더 경로
    output_text_file = "noise@.txt"  # 인식된 텍스트를 저장할 파일
    process_audio_files_in_folder(folder_path, output_text_file)
