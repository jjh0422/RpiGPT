import serial

# 시리얼 포트와 통신 속도 설정
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

try:
    while True:
        # 아두이노로부터 데이터 읽기
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').rstrip()
            if data:
                print(f'Received: {data}')
finally:
    ser.close()
