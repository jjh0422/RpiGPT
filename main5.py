import os
import openai
import speech_recognition as sr
from gtts import gTTS
import serial  # 아두이노와의 시리얼 통신을 위한 라이브러리
import time
from googletrans import Translator  # 번역기 라이브러리
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# NLTK 다운로드 (최초 실행 시 필요)
nltk.download('vader_lexicon')

# OpenAI API 키 설정
openai.api_key = '키 생성'

# 시스템 초기 메시지 설정
messages = [{"role": "system", "content": "You are an intelligent assistant."}]

# 시리얼 포트 설정 (아두이노 연결)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # 포트 이름을 실제 포트에 맞게 변경
time.sleep(2)  # 아두이노가 초기화되는 시간을 대기

# 번역기 초기화
translator = Translator()
# 감정 분석기 초기화
sia = SentimentIntensityAnalyzer()

def get_data_from_arduino(keyword):
    """아두이노로부터 특정 키워드에 해당하는 데이터를 읽어오는 함수"""
    if ser.in_waiting > 0:  # 시리얼 포트에 데이터가 있으면
        data = ser.readline().decode('utf-8').rstrip()  # 한 줄의 데이터 읽기
        if keyword in data:  # 해당 키워드가 포함된 데이터만 처리
            value = data.split(":")[1].strip()  # ':' 이후 값만 추출
            return value
    return None

def audio():
    """음성 녹음 및 텍스트로 변환"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("무엇을 말씀하십니까?")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        try:
            data = r.recognize_google(audio, language='ko-KR')
            print("녹음된 텍스트: " + data)
        except sr.UnknownValueError:
            print("음성을 이해할 수 없습니다.")
            data = ""
        except sr.RequestError as e:
            print(f"Google 음성 인식 서비스에 접근할 수 없습니다: {e}")
            data = ""

    return data

def translate_text(text):
    """한국어 텍스트를 영어로 번역"""
    translated = translator.translate(text, src='ko', dest='en')
    return translated.text

def sentiment_analysis(text):
    """NLTK를 사용한 감정 분석"""
    sentiment_scores = sia.polarity_scores(text)
    if sentiment_scores['compound'] >= 0.05:
        return "긍정"
    elif sentiment_scores['compound'] <= -0.05:
        return "부정"
    else:
        return "중립"

def speak(audiostring):
    """텍스트를 음성으로 변환하여 출력"""
    tts = gTTS(text=audiostring, lang='ko')
    tts.save("audio.mp3")
    os.system("mpg321 audio.mp3")

def info():
    while True:  # 무한 루프로 지속적인 대화 가능
        message = audio().replace(" ", "")

        if message.lower() in ['끝', '종료', 'stop', 'exit']:
            print("대화를 종료합니다.")
            break

        # 키워드에 따라 아두이노 데이터 가져오기
        if "온도" in message:
            temperature = get_data_from_arduino("온도")
            if temperature:
                response = f"온도는 {temperature}입니다."
            else:
                response = "아두이노에서 온도 데이터를 가져오지 못했습니다."
            print(response)
            speak(response)
            continue

        elif "습도" in message:
            humidity = get_data_from_arduino("습도")
            if humidity:
                response = f"습도는 {humidity}입니다."
            else:
                response = "아두이노에서 습도 데이터를 가져오지 못했습니다."
            print(response)
            speak(response)
            continue

        elif "토양습도" in message:
            soil_humidity = get_data_from_arduino("토양습도")
            if soil_humidity:
                response = f"토양습도는 {soil_humidity}입니다."
            else:
                response = "아두이노에서 토양습도 데이터를 가져오지 못했습니다."
            print(response)
            speak(response)
            continue

        elif "조도" in message:
            brightness = get_data_from_arduino("조도")
            if brightness:
                response = f"조도는 {brightness}입니다."
            else:
                response = "아두이노에서 조도 데이터를 가져오지 못했습니다."
            print(response)
            speak(response)
            continue

        # 일반적인 대화는 OpenAI ChatGPT API로 처리
        messages.append({"role": "user", "content": message})

        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )

        reply = chat.choices[0].message

        # 한국어 메시지를 영어로 번역
        translated_message = translate_text(message)
        # 번역된 메시지로 감정 분석 수행
        sentiment = sentiment_analysis(translated_message)

        print("Assistant: ", reply.content)
        print("분석된 감정: ", sentiment)  # 감정 분석 결과 출력
        speak(reply.content)

        messages.append(reply)

if __name__ == "__main__":
    info()
