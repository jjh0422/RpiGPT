import os
import openai
import speech_recognition as sr
from gtts import gTTS

# OpenAI API 키 설정
openai.api_key = 'sk-FfXqkZrgukOiwYVk8wnu5j4cTkxYrYGE0YOJ9z93yUT3BlbkFJpZMKL2rMFDizoe2T_mALHbdKkZlRRoQTMsskfMedwA'

# 시스템 초기 메시지 설정
messages = [{"role": "system", "content": "You are an intelligent assistant."}]

def audio():
    # 음성 녹음 및 텍스트로 변환
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
    # 텍스트를 음성으로 변환하여 출력
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
