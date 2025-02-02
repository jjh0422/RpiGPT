# 레퍼런스 데이터 출력 데이터와 맞게 변환

import re

def sort_sentences_by_numbers_and_alphabets(input_file, output_file):
    # 파일에서 텍스트 읽기
    with open(input_file, "r", encoding="utf-8") as infile:
        sentences = infile.readlines()  # 각 문장 읽기

    # 문장 정렬: 숫자-알파벳 순으로 정렬
    sorted_sentences = sorted(sentences, key=lambda x: re.sub(r'[^a-zA-Z0-9]', '', x))  # 숫자와 알파벳만 추출해서 정렬

    # 정렬된 문장을 출력 파일에 저장
    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.writelines(sorted_sentences)


# 사용 예시
input_file = "recognized_texts7_pi.txt"  # 입력 텍스트 파일 경로
output_file = "sorted_recognized_texts7_pi-.txt"  # 출력 파일 경로

sort_sentences_by_numbers_and_alphabets(input_file, output_file)
