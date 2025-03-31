import os
import numpy as np
import soundfile as sf
import torch
import time

def remove_silence_and_save(audio_path, model, get_speech_timestamps, read_audio, output_folder, threshold=0.01):
    """
    Silero VAD로 무음 제거 + 단계별 처리 시간 측정
    """
    t0 = time.time()

    # 1단계: 오디오 읽기
    t1 = time.time()
    wav = read_audio(audio_path)
    sample_rate = 16000  # Silero 모델의 기본 샘플링률
    t2 = time.time()

    # 2단계: 음성 구간 추출
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=sample_rate, threshold=threshold)
    t3 = time.time()

    # 3단계: 음성 구간 연결
    if len(speech_timestamps) == 0:
        return None, {
            "load": t2 - t1,
            "split": t3 - t2,
            "concat": 0.0,
            "save": 0.0,
            "total": time.time() - t0
        }
    non_silent_audio = np.concatenate([wav[ts['start']:ts['end']] for ts in speech_timestamps])
    t4 = time.time()

    # 4단계: 저장
    file_name = os.path.basename(audio_path)
    output_path = os.path.join(output_folder, f"vad_{file_name}")
    sf.write(output_path, non_silent_audio, sample_rate)
    t5 = time.time()

    step_times = {
        "load": t2 - t1,
        "split": t3 - t2,
        "concat": t4 - t3,
        "save": t5 - t4,
        "total": t5 - t0
    }

    return output_path, step_times

def process_audio_files_in_folder(folder_path, output_folder, model, get_speech_timestamps, read_audio):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

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
            wav_file_path = os.path.join(folder_path, filename)
            _, step_times = remove_silence_and_save(wav_file_path, model, get_speech_timestamps, read_audio, output_folder)

            if step_times:  # 무음 파일이 아닐 경우
                for key in total_times:
                    total_times[key] += step_times[key]
                total_files += 1

    print(f"\n📦 총 처리한 파일 수: {total_files}개")
    if total_files > 0:
        print("📊 단계별 평균 처리 시간:")
        print(f"  ⏱ 1단계 - 오디오 읽기:     {total_times['load'] / total_files:.8f}초")
        print(f"  ⏱ 2단계 - 음성 구간 추출: {total_times['split'] / total_files:.8f}초")
        print(f"  ⏱ 3단계 - 파형 재구성:     {total_times['concat'] / total_files:.8f}초")
        print(f"  ⏱ 4단계 - 파일 저장:       {total_times['save'] / total_files:.8f}초")
        print(f"  ✅ 총 평균 처리 시간:       {total_times['total'] / total_files:.8f}초")

def main():
    # 모델 및 함수 로드
    model, utils = torch.hub.load('snakers4/silero-vad', 'silero_vad', trust_repo=True)
    get_speech_timestamps, _, read_audio, _, _ = utils

    folder_path = "300wav"       # 입력 폴더
    output_folder = "vad_silero" # 출력 폴더

    start_all = time.time()
    process_audio_files_in_folder(folder_path, output_folder, model, get_speech_timestamps, read_audio)
    end_all = time.time()

    print(f"\n🧮 프로그램 전체 실행 시간: {end_all - start_all:.2f}초")

if __name__ == "__main__":
    main()
