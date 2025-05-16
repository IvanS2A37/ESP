from machine import Pin, ADC, I2C
from time import sleep, ticks_ms
from ssd1306 import SSD1306_I2C

# 設定 OLED (I2C)
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

# 設定搖桿輸入
vrx = ADC(Pin(34))
vry = ADC(Pin(35))
button = Pin(27, Pin.IN, Pin.PULL_UP)  # 跳躍按鈕

# 設定 ADC 參數
vrx.atten(ADC.ATTN_11DB)
vry.atten(ADC.ATTN_11DB)
vrx.width(ADC.WIDTH_12BIT)
vry.width(ADC.WIDTH_12BIT)

# 遊戲常量
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64
GROUND_HEIGHT = 50
MARIO_WIDTH = 8
MARIO_HEIGHT = 8
GRAVITY = 0.5
JUMP_FORCE = -6
MOVE_SPEED = 2
PLATFORM_HEIGHT = 4
COIN_SIZE = 4
TOTAL_LEVELS = 5

# 搖桿靈敏度設置
JOYSTICK_DEAD_ZONE = 300  # 中立區域大小
JOYSTICK_CENTER = 2048    # 中心值
JOYSTICK_THRESHOLD_HIGH = JOYSTICK_CENTER + 1000  # 高閾值
JOYSTICK_THRESHOLD_LOW = JOYSTICK_CENTER - 1000   # 低閾值

class GameObject:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def collides_with(self, other):
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)

class Mario(GameObject):
    def __init__(self):
        super().__init__(20, GROUND_HEIGHT - MARIO_HEIGHT, MARIO_WIDTH, MARIO_HEIGHT)
        self.vy = 0
        self.is_jumping = False
        self.facing_right = True
        self.score = 0
        self.current_level = 1
        self.last_jump_time = 0  # 添加跳躍冷卻時間記錄
    
    def reset_position(self):
        self.x = 20
        self.y = GROUND_HEIGHT - MARIO_HEIGHT
        self.vy = 0
        self.is_jumping = False
    
    def update(self, platforms):
        # 重力
        self.vy += GRAVITY
        new_y = self.y + self.vy
        
        # 地面碰撞檢測
        if new_y > GROUND_HEIGHT - self.height:
            new_y = GROUND_HEIGHT - self.height
            self.vy = 0
            self.is_jumping = False
        
        # 平台碰撞檢測
        for platform in platforms:
            if (self.x + self.width > platform.x and 
                self.x < platform.x + platform.width):
                # 從上方碰撞
                if (self.y + self.height <= platform.y and 
                    new_y + self.height > platform.y):
                    new_y = platform.y - self.height
                    self.vy = 0
                    self.is_jumping = False
                # 從下方碰撞
                elif (self.y >= platform.y + platform.height and 
                      new_y < platform.y + platform.height):
                    new_y = platform.y + platform.height
                    self.vy = 0
        
        self.y = new_y
    
    def jump(self):
        current_time = ticks_ms()
        # 添加跳躍冷卻時間（250毫秒）
        if not self.is_jumping and current_time - self.last_jump_time > 250:
            self.vy = JUMP_FORCE
            self.is_jumping = True
            self.last_jump_time = current_time
    
    def move(self, direction):
        new_x = self.x + direction * MOVE_SPEED
        if 0 <= new_x <= SCREEN_WIDTH - self.width:
            self.x = new_x
        self.facing_right = direction > 0 if direction != 0 else self.facing_right

class Platform(GameObject):
    def __init__(self, x, y, width):
        super().__init__(x, y, width, PLATFORM_HEIGHT)

class Coin(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, COIN_SIZE, COIN_SIZE)
        self.collected = False

def create_level(level):
    platforms = []
    coins = []
    
    if level == 1:
        # 第一關：簡單的平台配置
        platforms = [
            Platform(30, 40, 30),
            Platform(80, 30, 30),
            Platform(20, 20, 20),
        ]
        coins = [
            Coin(40, 30),
            Coin(90, 20),
            Coin(35, 10),
        ]
    
    elif level == 2:
        # 第二關：階梯式平台
        platforms = [
            Platform(20, 40, 20),
            Platform(50, 30, 20),
            Platform(80, 20, 20),
            Platform(110, 10, 15),
        ]
        coins = [
            Coin(25, 30),
            Coin(55, 20),
            Coin(85, 10),
            Coin(115, 0),
        ]
    
    elif level == 3:
        # 第三關：交錯平台
        platforms = [
            Platform(10, 40, 20),
            Platform(40, 30, 20),
            Platform(70, 40, 20),
            Platform(100, 30, 20),
        ]
        coins = [
            Coin(15, 30),
            Coin(45, 20),
            Coin(75, 30),
            Coin(105, 20),
        ]
    
    elif level == 4:
        # 第四關：高低起伏
        platforms = [
            Platform(20, 35, 25),
            Platform(55, 20, 25),
            Platform(90, 35, 25),
        ]
        coins = [
            Coin(30, 25),
            Coin(65, 10),
            Coin(100, 25),
            Coin(45, 45),
            Coin(80, 45),
        ]
    
    elif level == 5:
        # 第五關：最終關卡
        platforms = [
            Platform(20, 40, 15),
            Platform(45, 30, 15),
            Platform(70, 20, 15),
            Platform(95, 30, 15),
            Platform(120, 40, 8),
        ]
        coins = [
            Coin(25, 30),
            Coin(50, 20),
            Coin(75, 10),
            Coin(100, 20),
            Coin(122, 30),
        ]
    
    return platforms, coins

def check_level_complete(coins):
    return all(coin.collected for coin in coins)

def show_level_start(level):
    oled.fill(0)
    oled.text("Level " + str(level), 40, 20)
    oled.text("Ready!", 45, 35)
    oled.show()
    sleep(2)

def show_game_complete():
    oled.fill(0)
    oled.text("Congratulations!", 15, 20)
    oled.text("Game Complete!", 20, 35)
    oled.show()
    sleep(3)

def draw_game(mario, platforms, coins):
    oled.fill(0)
    
    # 繪製地面
    oled.hline(0, GROUND_HEIGHT, SCREEN_WIDTH, 1)
    
    # 繪製平台
    for platform in platforms:
        oled.rect(int(platform.x), int(platform.y), 
                 platform.width, platform.height, 1)
    
    # 繪製金幣
    for coin in coins:
        if not coin.collected:
            oled.rect(int(coin.x), int(coin.y), 
                     coin.width, coin.height, 1)
    
    # 繪製馬里奧
    if mario.facing_right:
        oled.rect(int(mario.x), int(mario.y), 
                 mario.width, mario.height, 1)
    else:
        oled.fill_rect(int(mario.x), int(mario.y), 
                      mario.width, mario.height, 1)
    
    # 顯示分數和關卡
    oled.text(f"L{mario.current_level} S:{mario.score}", 0, 0)
    
    oled.show()

def get_input():
    x = vrx.read()
    y = vry.read()
    
    # 水平移動判斷（加入死區）
    if abs(x - JOYSTICK_CENTER) < JOYSTICK_DEAD_ZONE:
        dx = 0
    else:
        dx = -1 if x < JOYSTICK_THRESHOLD_LOW else 1 if x > JOYSTICK_THRESHOLD_HIGH else 0
    
    # 跳躍判斷（加入死區和更高的閾值）
    should_jump = y < JOYSTICK_THRESHOLD_LOW - 200  # 需要推得更用力才會跳躍
    
    return dx, should_jump

# 初始化遊戲
mario = Mario()
platforms, coins = create_level(mario.current_level)

print("馬里奧遊戲開始！")
print("使用搖桿左右移動，向上推跳躍")  # 更新提示文字
show_level_start(mario.current_level)

# 遊戲主循環
while True:
    try:
        # 處理輸入
        direction, should_jump = get_input()
        if should_jump:  # 改用搖桿Y軸控制跳躍
            mario.jump()
        
        # 更新遊戲狀態
        mario.move(direction)
        mario.update(platforms)
        
        # 檢測金幣收集
        for coin in coins:
            if not coin.collected and mario.collides_with(coin):
                coin.collected = True
                mario.score += 100
        
        # 檢查關卡完成
        if check_level_complete(coins):
            if mario.current_level < TOTAL_LEVELS:
                mario.current_level += 1
                mario.reset_position()
                platforms, coins = create_level(mario.current_level)
                show_level_start(mario.current_level)
            else:
                show_game_complete()
                mario.current_level = 1
                mario.score = 0
                mario.reset_position()
                platforms, coins = create_level(mario.current_level)
                show_level_start(mario.current_level)
        
        # 更新顯示
        draw_game(mario, platforms, coins)
        
        sleep(0.02)
        
    except Exception as e:
        print("錯誤：", e)
        oled.fill(0)
        oled.text("Error:", 0, 0)
        oled.text(str(e), 0, 20)
        oled.show()
        sleep(1) 