from machine import Pin, ADC
from time import sleep

# 設定 LED 腳位
led_up = Pin(5, Pin.OUT)    # D1
led_down = Pin(4, Pin.OUT)  # D2
led_left = Pin(0, Pin.OUT)  # D3
led_right = Pin(2, Pin.OUT) # D4

# 設定搖桿的 X 軸輸入（A0）
joystick_x = ADC(Pin(34))  

# 閾值設定
CENTER = 2048     # 中心值 (12位ADC，範圍0-4095)
THRESHOLD = 1000   # 靈敏度範圍（可調）

def clear_leds():
    led_up.off()
    led_down.off()
    led_left.off()
    led_right.off()

while True:
    x_val = joystick_x.read()  # 讀取 0~1023 的值

    clear_leds()  # 每次 loop 先熄滅全部 LED

    if x_val < CENTER - THRESHOLD:
        led_left.on()
    elif x_val > CENTER + THRESHOLD:
        led_right.on()
    else:
        # 你可以擴展成用 Y 軸做上下
        pass

    # 延遲一點避免太快
    sleep(0.1)