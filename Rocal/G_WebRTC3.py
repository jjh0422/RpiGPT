import os
import time
import webrtcvad
import collections
import contextlib
import wave
import soundfile as sf
import speech_recognition as sr


def read_wave(path):
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def write_wave(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


class Frame(object):
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    n = int(sample_rate * frame_duration_ms / 1000 * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_collector(sample_rate, frame_duration_ms, padding_duration_ms, vad, frames):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False

    voiced_frames = []
    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)

        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
                voiced_frames.extend([f for f, s in ring_buffer])
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                triggered = False
                yield b''.join([f.bytes for f in voiced_frames])
                ring_buffer.clear()
                voiced_frames = []

    yield b''.join([f.bytes for f in voiced_frames])


def remove_silence_vad(audio_path, output_folder):
    # VAD 처리 시작 시간 기록
    vad_start_time = time.time()

    # 임시 폴더가 없으면 생성
    os.makedirs(output_folder, exist_ok=True)

    audio, sample_rate = read_wave(audio_path)
    vad = webrtcvad.Vad(0)
    frames = list(frame_generator(30, audio, sample_rate))
    segments = vad_collector(sample_rate, 30, 1000, vad, frames)

    output_audio = b''.join(segments)
    output_path = os.path.join(output_folder, os.path.basename(audio_path))
    write_wave(output_path, output_audio, sample_rate)

    # VAD 처리 종료 시간 기록
    vad_end_time = time.time()
    vad_duration = vad_end_time - vad_start_time  # VAD 처리 시간 계산

 #   print(f"파일: {os.path.basename(audio_path)}, VAD 처리 시간: {vad_duration:.6f}s")  # VAD 시간 출력

    return output_path, vad_duration  # VAD 처리 시간도 반환


def recognize_speech_from_wav(wav_file_path):
    r = sr.Recognizer()
    processed_wav_path, vad_time = remove_silence_vad(wav_file_path, "temp_processed")  # VAD 처리 후 파일 반환

    with sr.AudioFile(processed_wav_path) as source:
        audio = r.record(source)

    try:
        text = r.recognize_google(audio, language='ko-KR')
    except sr.UnknownValueError:
        text = "음성을 이해할 수 없습니다."
    except sr.RequestError as e:
        text = f"Google 음성 인식 서비스에 접근할 수 없습니다: {e}"

    os.remove(processed_wav_path)
    return text, vad_time  # VAD 처리 시간을 반환하도록 변경


def process_audio_files_in_folder(folder_path, output_text_file):
    rtf_sum = 0
    num_files = 0
    total_vad_time = 0  # 전체 VAD 처리 시간
    start_time_total = time.time()  # 전체 시작 시간 기록

    with open(output_text_file, 'w', encoding='utf-8') as f:
        for filename in os.listdir(folder_path):
            if filename.endswith(".wav"):
                num_files += 1
                file_name_without_extension = os.path.splitext(filename)[0]
                wav_file_path = os.path.join(folder_path, filename)

                speech, samplerate = sf.read(wav_file_path)
                total_utterance_duration = len(speech) / samplerate

                start_time = time.time()
                recognized_text, vad_time = recognize_speech_from_wav(wav_file_path)  # VAD 시간 반환
                end_time = time.time()
                total_duration = end_time - start_time

                total_vad_time += vad_time  # 전체 VAD 시간 누적

                rtf = total_duration / total_utterance_duration if total_utterance_duration > 0 else 0
                rtf_sum += rtf

                f.write(f"{file_name_without_extension} {recognized_text}\n")

               # print(f"파일: {filename}, VAD: {vad_time:.6f}s, 총 처리 시간: {total_duration:.6f}s")

    end_time_total = time.time()  # 전체 종료 시간 기록
    total_processing_time = end_time_total - start_time_total  # 전체 처리 시간 계산

    if num_files > 0:
        average_rtf = rtf_sum / num_files
        print(f"평균 RTF 값: {average_rtf:.4f}")

    print(f"총 VAD 처리 시간: {total_vad_time:.6f}초")
    print(f"총 처리 시간: {total_processing_time:.6f}초")


def main():
    folder_path = "300wav"
    output_text_file = "webrtc1.txt"
    process_audio_files_in_folder(folder_path, output_text_file)


if __name__ == "__main__":
    main()
