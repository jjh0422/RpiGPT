import os
import time
import webrtcvad
import collections
import contextlib
import wave

# 1단계: 오디오 로딩
def read_wave(path):
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
        assert wf.getframerate() in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, wf.getframerate()

# 4단계: 오디오 저장
def write_wave(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)

# 프레임 단위 클래스
class Frame:
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration

# 2단계: 프레임 생성
def frame_generator(frame_duration_ms, audio, sample_rate):
    n = int(sample_rate * frame_duration_ms / 1000 * 2)
    offset, timestamp = 0, 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n

# 2단계: VAD 판단
def vad_collector(sample_rate, frame_duration_ms, padding_duration_ms, vad, frames):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    voiced_frames = []

    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)
        if not triggered:
            ring_buffer.append((frame, is_speech))
            if len([f for f, speech in ring_buffer if speech]) > 0.9 * ring_buffer.maxlen:
                triggered = True
                voiced_frames.extend([f for f, s in ring_buffer])
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            if len([f for f, speech in ring_buffer if not speech]) > 0.9 * ring_buffer.maxlen:
                triggered = False
                yield b''.join([f.bytes for f in voiced_frames])
                ring_buffer.clear()
                voiced_frames = []

    yield b''.join([f.bytes for f in voiced_frames])

# 파일 하나 처리 (단계별 시간 측정 포함)
def remove_silence_and_measure(audio_path, output_folder):
    t0 = time.time()

    # 1단계: 오디오 로딩
    t1 = time.time()
    audio, sample_rate = read_wave(audio_path)
    t2 = time.time()

    # 2단계: 프레임 생성 + VAD
    vad = webrtcvad.Vad(0)
    frames = list(frame_generator(30, audio, sample_rate))
    segments = vad_collector(sample_rate, 30, 100, vad, frames)
    t3 = time.time()

    # 3단계: 파형 재구성
    output_audio = b''.join(segments)
    t4 = time.time()

    # 4단계: 저장
    output_path = os.path.join(output_folder, f"vad_{os.path.basename(audio_path)}")
    write_wave(output_path, output_audio, sample_rate)
    t5 = time.time()

    step_times = {
        "load": t2 - t1,
        "split": t3 - t2,    # librosa에서 split에 해당
        "concat": t4 - t3,
        "save": t5 - t4,
        "total": t5 - t0
    }

    return step_times

# 폴더 전체 처리 및 평균 계산
def process_audio_files_in_folder(folder_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    total_times = {
        "load": 0.0,
        "split": 0.0,
        "concat": 0.0,
        "save": 0.0,
        "total": 0.0
    }

    total_files = 0

    for filename in os.listdir(folder_path):
        if filename.endswith(".wav"):
            wav_path = os.path.join(folder_path, filename)
            step_times = remove_silence_and_measure(wav_path, output_folder)

            for key in total_times:
                total_times[key] += step_times[key]

            total_files += 1

    # 평균 출력
    print(f"\n📦 총 파일 수: {total_files}개")
    if total_files > 0:
        print(f"📊 단계별 평균 처리 시간:")
        print(f"  ⏱ 1단계 - 오디오 로딩:   {total_times['load'] / total_files:.8f}초")
        print(f"  ⏱ 2단계 - 무음 판단:     {total_times['split'] / total_files:.8f}초")
        print(f"  ⏱ 3단계 - 파형 재구성:   {total_times['concat'] / total_files:.8f}초")
        print(f"  ⏱ 4단계 - 파일 저장:     {total_times['save'] / total_files:.8f}초")
        print(f"  ✅ 총 평균 처리 시간:     {total_times['total'] / total_files:.8f}초")
    else:
        print("⚠️ .wav 파일이 없습니다.")

# 메인 실행
def main():
    folder_path = "300wav"
    output_folder = "vad_output"

    start_all = time.time()
    process_audio_files_in_folder(folder_path, output_folder)
    end_all = time.time()

    print(f"\n🧮 프로그램 전체 실행 시간: {end_all - start_all:.2f}초")

if __name__ == "__main__":
    main()
