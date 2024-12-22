import pygame
from typing import List, Dict, Any
import time
import math
from game_entities import *
import pygame
from typing import List, Dict, Any
import time
import math

class GameManager:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = GameState.INIT
        self.score = 0
        self.day = 1
        
        # 初始化游戏对象
        self.fisherman = Fisherman([400, 360])
        self.boat = Boat([380, 420])
        self.marlin = Marlin([200, 700])
        self.sharks: List[Shark] = []
        
        # 初始化管理器
        self.sound_manager = SoundManager()
        self.video_player = VideoPlayer()
        
        # 初始化音乐
        pygame.mixer.music.load("../assets/sound/Calm_ocean _waves.mp3")
        pygame.mixer.music.play(-1)

        # 加载背景
        self.background = pygame.image.load("../assets/backgroud.jpg").convert()
        self.background = pygame.transform.scale(self.background, 
                                              (screen_width, screen_height))
                                              
        # 初始化游戏对象的位置
        self.fisherman = Fisherman([400, 360])  # 老人在海平面
        self.boat = Boat([400, 420])           # 船在海平面
        self.marlin = Marlin([300, 400])       # 马林鱼在海中
        self.sharks = [Shark([600, 800])]      # 初始鲨鱼
        
        # 游戏统计数据
        self.stats = {
            'distance_traveled': 0,
            'marlin_caught': 0,
            'sharks_defeated': 0,
            'days_at_sea': 0
        }
        
        # 初始化UI元素
        self.font = pygame.font.Font(None, 36)
        
    def start_game(self):
        """开始新游戏"""
        self.state = GameState.INIT
        self.sound_manager.play_background()
        self.reset_game_objects()
        
    def reset_game_objects(self):
        """重置所有游戏对象到初始状态"""
        self.fisherman.set_position([400, 360])
        self.boat.set_position([380, 420])
        self.marlin.set_position([200, 700])
        self.sharks.clear()
        
    def update(self):
        """更新游戏状态"""
        # 更新所有游戏对象
        self.fisherman.update()
        self.boat.update()
        self.marlin.update()
        for shark in self.sharks:
            shark.update()
            
        # 状态特定的更新逻辑
        if self.state == GameState.TRAVELING:
            self._update_traveling()
        elif self.state == GameState.FISHING:
            self._update_fishing()
        elif self.state == GameState.FIGHTING_MARLIN:
            self._update_fighting_marlin()
        elif self.state == GameState.FIGHTING_SHARKS:
            self._update_fighting_sharks()
            
        # 检查游戏结束条件
        self._check_game_over()
        
    def _update_traveling(self):
        """更新航行状态"""
        # 计算航行距离
        distance = math.sqrt(sum(x*x for x in self.boat.speed))
        self.stats['distance_traveled'] += distance
        
        # 检查是否到达钓鱼点
        if self.stats['distance_traveled'] > 1000:  # 示例距离
            self.state = GameState.FISHING
            
    def _update_fishing(self):
        """更新钓鱼状态"""
        if self.fisherman.fish():
            self.state = GameState.FIGHTING_MARLIN
            self.sound_manager.play_sound('cheer')
            
    def _update_fighting_marlin(self):
        """更新与马林鱼搏斗状态"""
        if self.marlin.is_hooked:
            damage = self.marlin.struggle()
            self.fisherman.stamina -= damage
            
            if self.fisherman.attack() > 0:
                self.sound_manager.play_sound('attack')
                
    def _update_fighting_sharks(self):
        """更新与鲨鱼搏斗状态"""
        for shark in self.sharks:
            shark.approach(self.boat.position)
            if self._check_collision(shark.rect, self.boat.rect):
                damage = shark.attack()
                self.boat.durability -= damage
                self.sound_manager.play_sound('attack')
                
    def _check_collision(self, rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
        """检查两个矩形是否碰撞"""
        return rect1.colliderect(rect2)
        
    def _check_game_over(self):
        """检查游戏是否结束"""
        if (self.fisherman.stamina <= 0 or 
            self.boat.durability <= 0 or 
            self.boat.fuel <= 0):
            self.state = GameState.GAME_OVER
            
    def render(self, screen: pygame.Surface):
        """渲染游戏画面"""
        # 清空屏幕
        screen.fill((135, 206, 235))  # 天蓝色背景
        
        # 绘制背景
        screen.blit(self.background, (0, 0))
        
        # 按照深度顺序绘制游戏对象
        # 先画远处的物体
        if self.state in [GameState.FISHING, GameState.FIGHTING_MARLIN]:
            self.marlin.draw(screen)
        for shark in self.sharks:
            shark.draw(screen)
            
        # 然后画船和人物
        self.boat.draw(screen)
        self.fisherman.draw(screen)
        
        # 绘制UI
        self._render_ui(screen)
        
        # Debug信息
        debug_info = f"Fisherman pos: {self.fisherman.position}"
        debug_surf = self.font.render(debug_info, True, (255, 255, 255))
        screen.blit(debug_surf, (10, 100))
        
    def _render_ui(self, screen: pygame.Surface):
        """渲染UI元素"""
        # 状态栏
        status_text = f"Day: {self.day}  Score: {self.score}"
        status_surf = self.font.render(status_text, True, (255, 255, 255))
        screen.blit(status_surf, (10, 10))
        
        # 体力条
        pygame.draw.rect(screen, (255, 0, 0), 
                        (10, 40, self.fisherman.stamina * 2, 20))
        
        # 船只状态
        boat_text = f"Fuel: {int(self.boat.fuel)}  Durability: {self.boat.durability}"
        boat_surf = self.font.render(boat_text, True, (255, 255, 255))
        screen.blit(boat_surf, (10, 70))
        
    def handle_input(self, keys):
        """处理输入"""
        # 移动控制
        dx = dy = 0
        if keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_RIGHT]:
            dx = 1
        if keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_DOWN]:
            dy = 1
            
        # 根据游戏状态处理输入
        if self.state == GameState.TRAVELING:
            if dx != 0 or dy != 0:
                self.boat.move([dx, dy])
                self.fisherman.set_position([
                    self.boat.position[0] + 20,
                    self.boat.position[1] - 60
                ])
                
        elif self.state == GameState.FIGHTING_MARLIN:
            if keys[pygame.K_SPACE]:
                damage = self.fisherman.attack()
                self.marlin.take_damage(damage)
                self.sound_manager.play_sound('attack')
                
    def spawn_shark(self):
        """生成新的鲨鱼"""
        # 在屏幕边缘随机位置生成鲨鱼
        side = random.randint(0, 3)  # 0:上, 1:右, 2:下, 3:左
        
        if side == 0:  # 上边
            x = random.randint(0, self.screen_width)
            y = -100
        elif side == 1:  # 右边
            x = self.screen_width + 100
            y = random.randint(0, self.screen_height)
        elif side == 2:  # 下边
            x = random.randint(0, self.screen_width)
            y = self.screen_height + 100
        else:  # 左边
            x = -100
            y = random.randint(0, self.screen_height)
            
        new_shark = Shark([float(x), float(y)])
        self.sharks.append(new_shark)
        
    def update_day_cycle(self):
        """更新游戏日夜循环"""
        self.stats['days_at_sea'] += 1
        self.day += 1
        
        # 每天恢复一些体力
        self.fisherman.rest()
        
        # 每天有概率生成鲨鱼
        if random.random() < 0.3:  # 30%概率生成鲨鱼
            self.spawn_shark()
            
    def calculate_score(self):
        """计算游戏得分"""
        base_score = self.stats['marlin_caught'] * 1000  # 每条马林鱼1000分
        shark_score = self.stats['sharks_defeated'] * 500  # 每条鲨鱼500分
        distance_score = int(self.stats['distance_traveled'] / 100)  # 每100距离1分
        survival_score = self.stats['days_at_sea'] * 100  # 每天生存100分
        
        self.score = base_score + shark_score + distance_score + survival_score
        
    def show_game_over(self, screen: pygame.Surface):
        """显示游戏结束画面"""
        # 创建半透明背景
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # 显示游戏结束文本和统计信息
        game_over_text = self.font.render("Game Over", True, (255, 255, 255))
        score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        stats_text = self.font.render(
            f"Days at Sea: {self.stats['days_at_sea']}  Marlin: {self.stats['marlin_caught']}  "
            f"Sharks: {self.stats['sharks_defeated']}", 
            True, (255, 255, 255)
        )
        
        screen.blit(game_over_text, 
                   (self.screen_width//2 - game_over_text.get_width()//2, 
                    self.screen_height//2 - 60))
        screen.blit(score_text, 
                   (self.screen_width//2 - score_text.get_width()//2, 
                    self.screen_height//2))
        screen.blit(stats_text, 
                   (self.screen_width//2 - stats_text.get_width()//2, 
                    self.screen_height//2 + 60))
        
    def save_high_score(self):
        """保存最高分数"""
        try:
            with open("high_score.txt", "r") as f:
                high_score = int(f.read())
        except:
            high_score = 0
            
        if self.score > high_score:
            with open("high_score.txt", "w") as f:
                f.write(str(self.score))
                
    def play_ending_video(self):
        """播放结束视频"""
        if self.stats['marlin_caught'] > 0:
            self.video_player.play_video("../assets/video/Oil_Painting_Film_Excerpt.mp4")
            
    def add_achievement(self, achievement_name: str):
        """添加成就"""
        if not hasattr(self, 'achievements'):
            self.achievements = set()
            
        self.achievements.add(achievement_name)
        achievement_text = self.font.render(f"Achievement Unlocked: {achievement_name}", 
                                          True, (255, 215, 0))
        # 显示成就通知
        
    def check_achievements(self):
        """检查是否达成新成就"""
        # 检查各种成就条件
        if self.stats['marlin_caught'] >= 1:
            self.add_achievement("First Catch")
            
        if self.stats['sharks_defeated'] >= 5:
            self.add_achievement("Shark Hunter")
            
        if self.stats['days_at_sea'] >= 7:
            self.add_achievement("Sea Veteran")
            
        if self.score >= 5000:
            self.add_achievement("Master Fisherman")