from dataclasses import dataclass
from enum import Enum
import pygame
import math
import random
from typing import List, Tuple

# 游戏状态枚举
class GameState(Enum):
    INIT = "INIT"
    TRAVELING = "TRAVELING"
    FISHING = "FISHING"
    FIGHTING_MARLIN = "FIGHTING_MARLIN"
    RETURNING = "RETURNING"
    FIGHTING_SHARKS = "FIGHTING_SHARKS"
    GAME_OVER = "GAME_OVER"

# 基础游戏对象类
class GameObject:
    def __init__(self, position: List[float], image_path: str, scale_divisor: int = None):
        self.position = position
        self.image = pygame.image.load(image_path).convert_alpha()
        self.original_image = self.image
        
        # 按比例缩放
        if scale_divisor:
            new_size = (self.image.get_width() // scale_divisor, 
                       self.image.get_height() // scale_divisor)
            self.image = pygame.transform.scale(self.image, new_size)
            
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.speed = [0, 0]
        
    def update(self):
        self.position[0] += self.speed[0]
        self.position[1] += self.speed[1]
        self.rect.center = self.position
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        
    def set_position(self, pos):
        self.position = list(pos)
        self.rect.center = self.position

# 老人类
class Fisherman(GameObject):
    def __init__(self, position: List[float]):
        super().__init__(position, "../assets/old_man.png", 0.2)
        self.stamina = 100  # 体力值
        self.fishing_skill = 1  # 钓鱼技能
        self.strength = 10  # 力量值
        self.has_marlin = False
        
    def fish(self) -> bool:
        """钓鱼动作，返回是否钓到鱼"""
        self.stamina -= 1
        return random.random() < 0.1 * self.fishing_skill
        
    def rest(self):
        """休息恢复体力"""
        self.stamina = min(100, self.stamina + 5)
        
    def attack(self) -> int:
        """攻击动作，返回伤害值"""
        damage = self.strength * (0.5 + random.random())
        self.stamina -= 2
        return int(damage)

# 小船类
class Boat(GameObject):
    def __init__(self, position: List[float]):
        super().__init__(position, "../assets/boat.png", 0.2)
        self.fuel = 100
        self.durability = 100
        self.max_speed = 5
        self.direction = 0  # 方向角度
        
    def move(self, direction: List[float]):
        """移动船只"""
        if self.fuel > 0:
            self.speed = [direction[0] * self.max_speed, 
                         direction[1] * self.max_speed]
            self.fuel -= 0.1
            return True
        return False
        
    def repair(self):
        """修理船只"""
        self.durability = min(100, self.durability + 10)
        
    def refuel(self):
        """补充燃料"""
        self.fuel = min(100, self.fuel + 20)

# 马林鱼类
class Marlin(GameObject):
    def __init__(self, position: List[float]):
        super().__init__(position, "../assets/marha_fish.png", 0.33)
        self.health = 100
        self.strength = 15
        self.is_hooked = False
        self.escape_attempts = 3
        
    def struggle(self) -> int:
        """挣扎动作，返回对渔夫造成的伤害"""
        if self.escape_attempts > 0:
            self.escape_attempts -= 1
            return int(self.strength * (0.5 + random.random()))
        return 0
        
    def take_damage(self, damage: int):
        """受到伤害"""
        self.health -= damage
        if random.random() < 0.2:  # 20%概率挣脱
            self.is_hooked = False

# 鲨鱼类
class Shark(GameObject):
    def __init__(self, position: List[float]):
        super().__init__(position, "../assets/shark.png", 0.5)
        self.health = 80
        self.attack_power = 20
        self.attack_range = 50
        
    def approach(self, target_pos: List[float]):
        """接近目标"""
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.speed = [dx/dist * 3, dy/dist * 3]
            
    def attack(self) -> int:
        """攻击动作，返回伤害值"""
        return int(self.attack_power * (0.8 + random.random() * 0.4))
        
    def take_damage(self, damage: int):
        """受到伤害"""
        self.health -= damage

# 音效管理器
class SoundManager:
    def __init__(self):
        self.sounds = {
            'wave': pygame.mixer.Sound("../assets/sound/Calm_ocean _waves.mp3"),
            'attack': pygame.mixer.Sound("../assets/sound/attack.mp3"),
            'cheer': pygame.mixer.Sound("../assets/sound/Cheers.mp3")
        }
        
    def play_sound(self, sound_name: str):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
            
    def play_background(self):
        self.sounds['wave'].play(-1)  # 循环播放
        
    def stop_all(self):
        pygame.mixer.stop()

# 视频播放器
class VideoPlayer:
    def __init__(self):
        self.current_video = None
        
    def play_video(self, video_path: str):
        # 使用之前定义的视频播放适配器来播放视频
        pass
        
    def stop_video(self):
        if self.current_video:
            self.current_video.stop()
            self.current_video = None