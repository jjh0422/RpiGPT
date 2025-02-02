# cer 측정

import jiwer
import re


# 공백과 구두점을 제외한 텍스트를 처리하는 함수
def preprocess_text(text):
    # 공백과 구두점 제외하고 음절만 남김
    text = re.sub(r"[^\w가-힣]", "", text)  # 한글과 숫자, 알파벳을 제외한 문자 제거
    return text


# CER 계산 함수
def calculate_cer(reference_file, hypothesis_file):
    # 파일에서 텍스트 읽기
    with open(reference_file, "r", encoding="utf-8") as ref_file:
        reference_lines = ref_file.readlines()  # 각 문장 읽기

    with open(hypothesis_file, "r", encoding="utf-8") as hyp_file:
        hypothesis_lines = hyp_file.readlines()  # 각 문장 읽기

    cer_results = []  # 각 문장에 대한 CER 결과 저장

    # 각 문장에 대해 CER 계산
    for ref_line, hyp_line in zip(reference_lines, hypothesis_lines):
        # 전처리
        ref_line = preprocess_text(ref_line.strip())
        hyp_line = preprocess_text(hyp_line.strip())

        # CER 측정
        cer = jiwer.cer(ref_line, hyp_line)
        cer_results.append(cer)

    # 평균 CER 계산
    avg_cer = sum(cer_results) / len(cer_results) if cer_results else 0.0
    return avg_cer


# 텍스트 파일 경로
reference_file = "sorted_korean-.txt"  # 레퍼런스 텍스트 파일 경로
hypothesis_file = "sorted_recognized_texts7_pi-.txt"  # 음성 인식 결과 텍스트 파일 경로

# CER 계산
avg_cer = calculate_cer(reference_file, hypothesis_file)

# 평균 CER 출력
print(f"평균 CER: {avg_cer:.4f}")
