from machine import Pin, ADC, PWM, I2C, SoftI2C
import time
from ssd1306 import SSD1306_I2C

# 初始化OLED
try:
    # 使用软件I2C，使用不同的引脚
    i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=100000)  # 改用GPIO 22和21
    oled = SSD1306_I2C(128, 64, i2c)
    print("OLED初始化成功")
except Exception as e:
    print(f"OLED初始化失败: {e}")
    oled = None

# 初始化第一组摇杆引脚（控制第一个马达）
joystick_x = ADC(Pin(34))  # X轴
joystick_y = ADC(Pin(35))  # Y轴

# 初始化第二组摇杆引脚（控制第二个马达）
joystick2_x = ADC(Pin(33))  # X轴
joystick2_y = ADC(Pin(15))  # Y轴

# 初始化第一个马达L298N控制引脚
ENA = PWM(Pin(25))  # 使能A
IN1 = Pin(26, Pin.OUT)  # 输入1
IN2 = Pin(4, Pin.OUT)  # 输入2

# 初始化第二个马达L298N控制引脚
ENB = PWM(Pin(27))  # 使能B
IN3 = Pin(14, Pin.OUT)  # 输入3
IN4 = Pin(12, Pin.OUT)  # 输入4

# 设置PWM频率
ENA.freq(1000)  # 1kHz
ENB.freq(1000)  # 1kHz
ENA.duty(0)  # 初始占空比为0
ENB.duty(0)  # 初始占空比为0

# 设置ADC范围
for adc in [joystick_x, joystick_y, joystick2_x, joystick2_y]:
    adc.atten(ADC.ATTN_11DB)
    adc.width(ADC.WIDTH_12BIT)

# 定义阈值
THRESHOLD = 500  # 摇杆阈值

def update_display(motor1_speed, motor1_direction, motor2_speed, motor2_direction):
    """更新OLED显示"""
    if oled is None:
        return
    try:
        oled.fill(0)  # 清除显示
        oled.text("Motor Control", 0, 0)
        oled.text(f"M1:{motor1_speed}", 0, 20)
        oled.text(f"{motor1_direction}", 0, 30)
        oled.text(f"M2:{motor2_speed}", 0, 40)
        oled.text(f"{motor2_direction}", 0, 50)
        oled.show()
        print("OLED显示已更新")
    except Exception as e:
        print(f"OLED显示更新失败: {e}")

def read_joystick():
    """读取第一个摇杆值"""
    y = joystick_y.read()
    print(f"马达1摇杆值: Y={y}")
    return y

def read_joystick2():
    """读取第二个摇杆值"""
    y = joystick2_y.read()
    print(f"马达2摇杆值: Y={y}")
    return y

def stop_motor1():
    """停止第一个马达"""
    print("停止马达1")
    ENA.duty(0)  # 关闭PWM输出
    IN1.value(0)
    IN2.value(0)

def stop_motor2():
    """停止第二个马达"""
    print("停止马达2")
    ENB.duty(0)  # 关闭PWM输出
    IN3.value(0)
    IN4.value(0)

def control_motor1(y):
    """控制第一个马达"""
    if y < 2000 - THRESHOLD:  # 上
        # 计算速度
        y = max(0, min(y, 2000))
        speed = int(((2000 - y) / 2000) ** 0.5 * 1023)
        speed = max(0, min(speed, 1023))
        print(f"马达1速度: {speed}")
        
        # 设置马达方向 - 正转
        IN1.value(1)
        IN2.value(0)
        
        # 设置PWM占空比
        ENA.duty(speed)
        return speed, "FORWARD"
    elif y > 2000 + THRESHOLD:  # 下
        # 计算速度
        y = max(2000, min(y, 4000))
        speed = int(((y - 2000) / 2000) ** 0.5 * 1023)
        speed = max(0, min(speed, 1023))
        print(f"马达1速度: {speed}")
        
        # 设置马达方向 - 反转
        IN1.value(0)
        IN2.value(1)
        
        # 设置PWM占空比
        ENA.duty(speed)
        return speed, "REVERSE"
    else:
        stop_motor1()
        return 0, "STOP"

def control_motor2(y):
    """控制第二个马达"""
    if y < 2000 - THRESHOLD:  # 上
        # 计算速度
        y = max(0, min(y, 2000))
        speed = int(((2000 - y) / 2000) ** 0.5 * 1023)
        speed = max(0, min(speed, 1023))
        print(f"马达2速度: {speed}")
        
        # 设置马达方向 - 正转
        IN3.value(1)
        IN4.value(0)
        
        # 设置PWM占空比
        ENB.duty(speed)
        return speed, "FORWARD"
    elif y > 2000 + THRESHOLD:  # 下
        # 计算速度
        y = max(2000, min(y, 4000))
        speed = int(((y - 2000) / 2000) ** 0.5 * 1023)
        speed = max(0, min(speed, 1023))
        print(f"马达2速度: {speed}")
        
        # 设置马达方向 - 反转
        IN3.value(0)
        IN4.value(1)
        
        # 设置PWM占空比
        ENB.duty(speed)
        return speed, "REVERSE"
    else:
        stop_motor2()
        return 0, "STOP"

def main():
    print("开始运行摇杆控制程序...")
    print("使用L298N马达驱动模块")
    print("马达1控制：使用第一个摇杆Y轴")
    print("马达2控制：使用第二个摇杆Y轴")
    print(f"摇杆阈值: {THRESHOLD}")
    print("向上移动摇杆：正转")
    print("向下移动摇杆：反转")
    
    # 显示初始信息
    if oled is not None:
        try:
            oled.fill(0)
            oled.text("Dual Motor", 0, 0)
            oled.text("Control Ready", 0, 20)
            oled.show()
        except Exception as e:
            print(f"OLED显示初始化失败: {e}")
    time.sleep(2)
    
    # 确保初始状态为停止
    stop_motor1()
    stop_motor2()
    
    while True:
        try:
            # 读取两个摇杆的Y值
            motor1_y = read_joystick()
            motor2_y = read_joystick2()
            
            # 控制两个马达
            motor1_speed, motor1_dir = control_motor1(motor1_y)
            motor2_speed, motor2_dir = control_motor2(motor2_y)
            
            # 更新显示
            update_display(motor1_speed, motor1_dir, motor2_speed, motor2_dir)
            
            # 短暂延时
            time.sleep(0.1)
        except Exception as e:
            print(f"运行错误: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
