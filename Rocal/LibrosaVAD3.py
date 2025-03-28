import os
import librosa
import numpy as np
import soundfile as sf
import time


def remove_silence_and_save(audio_path, output_folder, top_db=30):
    """
    음성에서 무음을 제거하고 각 단계별 처리 시간을 반환
    """
    t0 = time.time()

    # 1단계: 오디오 로딩
    t1 = time.time()
    y, sr = librosa.load(audio_path, sr=None)
    t2 = time.time()

    # 2단계: 무음 판단
    non_silent_intervals = librosa.effects.split(
        y, top_db=top_db, frame_length=2048, hop_length=512
    )
    t3 = time.time()

    # 3단계: 파형 재구성
    non_silent_audio = np.concatenate([
        y[start:end] for start, end in non_silent_intervals
    ])
    t4 = time.time()

    # 4단계: 저장
    file_name = os.path.basename(audio_path)
    output_path = os.path.join(output_folder, f"vad_{file_name}")
    sf.write(output_path, non_silent_audio, sr)
    t5 = time.time()

    # 각 단계별 시간 계산
    step_times = {
        "load": t2 - t1,
        "split": t3 - t2,
        "concat": t4 - t3,
        "save": t5 - t4,
        "total": t5 - t0
    }

    return step_times


def process_audio_files_in_folder(folder_path, output_folder):
    """
    폴더 내 모든 .wav 파일에 대해 VAD 수행 및 평균 시간 계산
    """
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
            wav_path = os.path.join(folder_path, filename)
            step_times = remove_silence_and_save(wav_path, output_folder)

            for key in total_times:
                total_times[key] += step_times[key]

            total_files += 1

    # 평균 계산
    print(f"\n📦 총 파일 수: {total_files}개")
    if total_files > 0:
        print(f"📊 단계별 평균 처리 시간:")
        print(f"  ⏱ 1단계 - 오디오 로딩:   {total_times['load'] / total_files:.8f}초")
        print(f"  ⏱ 2단계 - 무음 판단:     {total_times['split'] / total_files:.8f}초")
        print(f"  ⏱ 3단계 - 파형 재구성:   {total_times['concat'] / total_files:.8f}초")
        print(f"  ⏱ 4단계 - 파일 저장:     {total_times['save'] / total_files:.8f}초")
        print(f"  ✅ 총 평균 처리 시간:     {total_times['total'] / total_files:.8f}초")


def main():
    folder_path = "300wav"        # 원본 오디오 폴더
    output_folder = "vad_output"  # 출력 폴더

    start_all = time.time()
    process_audio_files_in_folder(folder_path, output_folder)
    end_all = time.time()

    print(f"\n🧮 프로그램 전체 실행 시간: {end_all - start_all:.2f}초")


if __name__ == "__main__":
    main()
