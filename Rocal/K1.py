from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import soundfile as sf

# 모델과 프로세서 로드
processor = Wav2Vec2Processor.from_pretrained("local_model_directory")
model = Wav2Vec2ForCTC.from_pretrained("local_model_directory").to('cpu')

# 음성 파일 로드
speech, _ = sf.read("output.wav")

# 음성 데이터 전처리
inputs = processor(speech, sampling_rate=16000, return_tensors="pt", padding="longest")
input_values = inputs.input_values.to("cpu")

# 예측 수행
with torch.no_grad():
    logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)

print("Transcription:", transcription)
