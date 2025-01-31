from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import soundfile as sf
import time

# 모델과 프로세서 로드
processor = Wav2Vec2Processor.from_pretrained("local_model_directory")
model = Wav2Vec2ForCTC.from_pretrained("local_model_directory").to('cpu')

# 음성 파일 로드
speech, _ = sf.read("output.wav")

# 음성 신호 길이 (초 단위)
total_utterance_duration = len(speech) / 16000  # 16000은 샘플링 레이트 (Hz)

# 음성 데이터 전처리
inputs = processor(speech, sampling_rate=16000, return_tensors="pt", padding="longest")
input_values = inputs.input_values.to("cpu")

# 예측 수행
start_time = time.time()  # 처리 시작 시간
with torch.no_grad():
    logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)
end_time = time.time()  # 처리 종료 시간

# 처리 시간
total_duration = end_time - start_time  # 전체 처리 시간

# RTF 계산
rtf = total_duration / total_utterance_duration if total_utterance_duration > 0 else 0

# 결과 출력
print("Transcription:", transcription)
print(f"처리 시간: {total_duration:.4f}초")
print(f"음성 신호 길이: {total_utterance_duration:.4f}초")
print(f"RTF 값: {rtf:.4f}")
