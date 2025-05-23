from machine import Pin, ADC, I2C, PWM
from time import sleep
from ssd1306 import SSD1306_I2C

# 設定 OLED (I2C)
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

# 設定蜂鳴器
buzzer = PWM(Pin(16))
buzzer.freq(1000)  # 設定初始頻率
buzzer.duty(0)     # 初始靜音

# 設定搖桿輸入
# 玩家1的搖桿
vrx1 = ADC(Pin(34))
vry1 = ADC(Pin(35))
button1 = Pin(27, Pin.IN, Pin.PULL_UP)

# 玩家2的搖桿
vrx2 = ADC(Pin(25))
vry2 = ADC(Pin(26))
button2 = Pin(4, Pin.IN, Pin.PULL_UP)

# 設定 ADC 參數
for adc in [vrx1, vry1, vrx2, vry2]:
    adc.atten(ADC.ATTN_11DB)
    adc.width(ADC.WIDTH_12BIT)

# 遊戲常量
BOARD_SIZE = 15  # 15x15的棋盤
CELL_SIZE = 4    # 每個格子4像素
BOARD_OFFSET_X = 4  # 棋盤左邊距
BOARD_OFFSET_Y = 4  # 棋盤上邊距

# 搖桿設置
JOYSTICK_DEAD_ZONE = 300
JOYSTICK_CENTER = 2048
JOYSTICK_THRESHOLD = 1000

def play_tone(frequency, duration):
    buzzer.freq(frequency)
    buzzer.duty(512)  # 50% 音量
    sleep(duration)
    buzzer.duty(0)    # 停止發聲

def play_move_sound():
    # 落子音效：上升的音階
    play_tone(440, 0.05)  # A4
    play_tone(523, 0.05)  # C5
    play_tone(659, 0.05)  # E5

def play_win_sound():
    # 獲勝音效：歡快的音階
    play_tone(523, 0.1)  # C5
    play_tone(659, 0.1)  # E5
    play_tone(784, 0.1)  # G5
    play_tone(1047, 0.2) # C6
    sleep(0.1)
    play_tone(1047, 0.2) # C6
    play_tone(1047, 0.2) # C6

class Gomoku:
    def __init__(self):
        self.board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.current_player = 1  # 1代表黑棋，2代表白棋
        self.cursor_x = BOARD_SIZE // 2
        self.cursor_y = BOARD_SIZE // 2
        self.game_over = False
        self.winner = 0

    def move_cursor(self, dx, dy):
        new_x = self.cursor_x + dx
        new_y = self.cursor_y + dy
        if 0 <= new_x < BOARD_SIZE and 0 <= new_y < BOARD_SIZE:
            self.cursor_x = new_x
            self.cursor_y = new_y

    def place_stone(self):
        if self.board[self.cursor_y][self.cursor_x] == 0 and not self.game_over:
            self.board[self.cursor_y][self.cursor_x] = self.current_player
            play_move_sound()  # 播放落子音效
            if self.check_win():
                self.game_over = True
                self.winner = self.current_player
                play_win_sound()  # 播放獲勝音效
            else:
                self.current_player = 3 - self.current_player  # 切換玩家

    def check_win(self):
        directions = [(1,0), (0,1), (1,1), (1,-1)]  # 水平、垂直、對角線
        for dx, dy in directions:
            count = 1
            # 正向檢查
            x, y = self.cursor_x + dx, self.cursor_y + dy
            while 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and self.board[y][x] == self.current_player:
                count += 1
                x += dx
                y += dy
            # 反向檢查
            x, y = self.cursor_x - dx, self.cursor_y - dy
            while 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and self.board[y][x] == self.current_player:
                count += 1
                x -= dx
                y -= dy
            if count >= 5:
                return True
        return False

    def draw_board(self):
        oled.fill(0)
        
        # 繪製棋盤
        for i in range(BOARD_SIZE):
            # 橫線
            oled.hline(BOARD_OFFSET_X, BOARD_OFFSET_Y + i * CELL_SIZE,
                      BOARD_SIZE * CELL_SIZE, 1)
            # 豎線
            oled.vline(BOARD_OFFSET_X + i * CELL_SIZE, BOARD_OFFSET_Y,
                      BOARD_SIZE * CELL_SIZE, 1)

        # 繪製棋子
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                center_x = BOARD_OFFSET_X + x * CELL_SIZE
                center_y = BOARD_OFFSET_Y + y * CELL_SIZE
                if self.board[y][x] == 1:  # 黑棋 - 使用實心圓形
                    oled.fill_rect(center_x - 2, center_y - 2, 5, 5, 1)
                elif self.board[y][x] == 2:  # 白棋 - 使用X形狀
                    # 繪製X形狀
                    oled.line(center_x - 2, center_y - 2, center_x + 2, center_y + 2, 1)
                    oled.line(center_x - 2, center_y + 2, center_x + 2, center_y - 2, 1)

        # 繪製光標
        cursor_x = BOARD_OFFSET_X + self.cursor_x * CELL_SIZE
        cursor_y = BOARD_OFFSET_Y + self.cursor_y * CELL_SIZE
        oled.rect(cursor_x - 2, cursor_y - 2, 5, 5, 1)

        # 顯示當前玩家
        if not self.game_over:
            oled.text("P" + str(self.current_player), 100, 0)
            # 添加玩家提示
            if self.current_player == 1:
                # 黑棋提示 - 實心方塊
                oled.fill_rect(90, 0, 3, 3, 1)
            else:
                # 白棋提示 - X形狀
                oled.line(90, 0, 92, 2, 1)
                oled.line(90, 2, 92, 0, 1)
        else:
            oled.text("P" + str(self.winner) + " Win!", 80, 0)

        oled.show()

def get_joystick_input(adc_x, adc_y):
    x = adc_x.read()
    y = adc_y.read()
    dx = dy = 0
    
    if abs(x - JOYSTICK_CENTER) > JOYSTICK_THRESHOLD:
        dx = 1 if x > JOYSTICK_CENTER else -1
    if abs(y - JOYSTICK_CENTER) > JOYSTICK_THRESHOLD:
        dy = 1 if y > JOYSTICK_CENTER else -1
    
    return dx, dy

def main():
    game = Gomoku()
    last_move_time = 0
    
    while True:
        # 獲取當前玩家的搖桿輸入
        if game.current_player == 1:
            dx, dy = get_joystick_input(vrx1, vry1)
            button_pressed = not button1.value()
        else:
            dx, dy = get_joystick_input(vrx2, vry2)
            button_pressed = not button2.value()

        # 移動光標
        if dx != 0 or dy != 0:
            game.move_cursor(dx, dy)
            sleep(0.1)  # 防止移動太快

        # 放置棋子
        if button_pressed:
            game.place_stone()
            sleep(0.2)  # 防止重複觸發

        # 更新顯示
        game.draw_board()
        sleep(0.05)

if __name__ == "__main__":
    main() 
