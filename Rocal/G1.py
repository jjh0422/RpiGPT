#구글 클라우드 음성인식 ai, wav 파일 1개

import speech_recognition as sr


def recognize_speech_from_wav(wav_file_path):
    # 음성 인식기 초기화
    r = sr.Recognizer()

    # WAV 파일 로드
    with sr.AudioFile(wav_file_path) as source:
        audio = r.record(source)  # 전체 파일을 읽음

    try:
        # Google 음성 인식 API를 사용하여 한글 텍스트로 변환
        text = r.recognize_google(audio, language='ko-KR')
        print("인식된 텍스트: " + text)
    except sr.UnknownValueError:
        print("음성을 이해할 수 없습니다.")
        text = ""
    except sr.RequestError as e:
        print(f"Google 음성 인식 서비스에 접근할 수 없습니다: {e}")
        text = ""

    return text


if __name__ == "__main__":
    # WAV 파일 경로
    wav_file_path = "output.wav"

    # 음성 인식 실행
    recognized_text = recognize_speech_from_wav(wav_file_path)
