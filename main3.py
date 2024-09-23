# 음성인식 + gpt 사용 + 아두이노 연동 온도


import os
import openai
import speech_recognition as sr
from gtts import gTTS
import serial  # 아두이노와의 시리얼 통신을 위한 라이브러리
import time

# OpenAI API 키 설정
openai.api_key = '키 생성'

# 시스템 초기 메시지 설정
messages = [{"role": "system", "content": "You are an intelligent assistant."}]

# 시리얼 포트 설정 (아두이노 연결)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # 포트 이름을 실제 포트에 맞게 변경
time.sleep(2)  # 아두이노가 초기화되는 시간을 대기

def get_temperature_from_arduino():
    """아두이노로부터 온도 데이터를 읽어오는 함수"""
    if ser.in_waiting > 0:  # 시리얼 포트에 데이터가 있으면
        data = ser.readline().decode('utf-8').rstrip()  # 한 줄의 데이터 읽기
        return data
    return "아두이노에서 데이터를 읽지 못했습니다."

def audio():
    """음성 녹음 및 텍스트로 변환"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("무엇을 말씀하십니까?")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        try:
            # Google 음성 인식 API를 사용하여 한글 텍스트로 변환
            data = r.recognize_google(audio, language='ko-KR')
            print("녹음된 텍스트: " + data)
        except sr.UnknownValueError:
            print("음성을 이해할 수 없습니다.")
            data = ""
        except sr.RequestError as e:
            print(f"Google 음성 인식 서비스에 접근할 수 없습니다: {e}")
            data = ""

    return data

def speak(audiostring):
    """텍스트를 음성으로 변환하여 출력"""
    tts = gTTS(text=audiostring, lang='ko')
    tts.save("audio.mp3")
    # MP3 파일을 재생 (리눅스에서 mpg321 사용)
    os.system("mpg321 audio.mp3")

def info():
    while True:  # 무한 루프로 지속적인 대화 가능
        message = audio().replace(" ", "")

        if message.lower() in ['끝', '종료', 'stop', 'exit']:
            print("대화를 종료합니다.")
            break

        # "온도"라는 단어가 음성에 포함되어 있으면
        if "온도" in message:
            temperature = get_temperature_from_arduino()  # 아두이노에서 온도 데이터 가져오기
            response = f"온도는 {temperature} 입니다."
            print(response)
            speak(response)
            continue  # 바로 다음 루프로 이동하여 OpenAI API를 호출하지 않음

        # 일반적인 대화는 OpenAI ChatGPT API로 처리
        messages.append(
            {"role": "user", "content": message},
        )

        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )

        reply = chat.choices[0].message

        print("Assistant: ", reply.content)
        speak(reply.content)

        messages.append(reply)

if __name__ == "__main__":
    info()
