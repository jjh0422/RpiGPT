import os
import time
import threading
import psutil
import speech_recognition as sr

def recognize_speech_from_wav(wav_file_path):
    r = sr.Recognizer()
    with sr.AudioFile(wav_file_path) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio, language='ko-KR')
    except sr.UnknownValueError:
        text = "음성을 이해할 수 없습니다."
    except sr.RequestError as e:
        text = f"Google 음성 인식 서비스에 접근할 수 없습니다: {e}"
    return text

def monitor_cpu_usage(cpu_log):
    while monitoring:
        cpu_usages = psutil.cpu_percent(interval=1, percpu=True)
        total_usage = sum(cpu_usages) / len(cpu_usages)  # 평균 CPU 사용량 계산
        cpu_log.append((cpu_usages, total_usage))
        time.sleep(9)  # 총 10초 주기로 측정

def process_audio_files_in_folder(folder_path, output_text_file, cpu_usage_file):
    global monitoring
    cpu_log = []
    monitoring = True
    
    # CPU 모니터링 스레드 시작
    cpu_thread = threading.Thread(target=monitor_cpu_usage, args=(cpu_log,))
    cpu_thread.start()
    
    with open(output_text_file, 'w', encoding='utf-8') as f:
        for filename in os.listdir(folder_path):
            if filename.endswith(".wav"):
                wav_file_path = os.path.join(folder_path, filename)
                recognized_text = recognize_speech_from_wav(wav_file_path)
                f.write(f"File: {filename}\n")
                f.write(f"Text: {recognized_text}\n\n")
    
    # CPU 모니터링 중지
    monitoring = False
    cpu_thread.join()
    
    # CPU 사용량 저장
    with open(cpu_usage_file, 'w', encoding='utf-8') as f:
        for i, (usages, total) in enumerate(cpu_log):
            usage_str = ", ".join([f"Core {idx}: {usage}%" for idx, usage in enumerate(usages)])
            f.write(f"{i * 10}초: {usage_str}, Total: {total:.2f}%\n")

if __name__ == "__main__":
    folder_path = "300wav"
    output_text_file = "recognized_texts.txt"
    cpu_usage_file = "cpu_usage.txt"
    process_audio_files_in_folder(folder_path, output_text_file, cpu_usage_file)
