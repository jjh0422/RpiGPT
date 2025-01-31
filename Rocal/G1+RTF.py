import speech_recognition as sr
import time


def recognize_speech_from_wav(wav_file_path):
    # 음성 인식기 초기화
    r = sr.Recognizer()

    # WAV 파일 로드
    with sr.AudioFile(wav_file_path) as source:
        audio = r.record(source)  # 전체 파일을 읽음

    try:
        # Google 음성 인식 API를 사용하여 한글 텍스트로 변환
        start_time = time.time()  # 처리 시작 시간
        text = r.recognize_google(audio, language='ko-KR')
        end_time = time.time()  # 처리 종료 시간
        print("인식된 텍스트: " + text)
    except sr.UnknownValueError:
        print("음성을 이해할 수 없습니다.")
        text = ""
        end_time = time.time()
    except sr.RequestError as e:
        print(f"Google 음성 인식 서비스에 접근할 수 없습니다: {e}")
        text = ""
        end_time = time.time()

    # RTF 계산
    total_duration = end_time - start_time  # 전체 처리 시간
    total_utterance_duration = len(audio.frame_data) / audio.sample_rate  # 음성 신호 길이 (초)
    rtf = total_duration / total_utterance_duration if total_utterance_duration > 0 else 0

    # 지연시간 출력
    print(f"처리 시간: {total_duration:.4f}초")
    print(f"음성 신호 길이: {total_utterance_duration:.4f}초")
    print(f"RTF 값: {rtf:.4f}")

    return text


if __name__ == "__main__":
    # WAV 파일 경로
    wav_file_path = "output.wav"

    # 음성 인식 실행
    recognized_text = recognize_speech_from_wav(wav_file_path)
