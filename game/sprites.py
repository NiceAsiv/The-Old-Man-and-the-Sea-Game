# -*- coding: utf-8 -*-
import pygame
import random
import math

# 颜色定义
BLUE = (0, 119, 190)
DEEP_BLUE = (0, 72, 186)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
from enum import Enum

class GameState(Enum):
    IDLE = "idle"
    MOVING = "moving"
    FISHING = "fishing"
    ATTACKING = "attacking"
    SHOPPING = "shopping"

class WeaponState(Enum):
    IDLE = "idle"
    AUTO_ATTACK = "auto_attack"
    DEAL_DAMAGE = "deal_damage"
    COOLDOWN = "cooldown"

class HookState(Enum):
    SWINGING = "swinging"
    EXTENDING = "extending"
    RETRACTING = "retracting"
    IDLE = "idle"

class FishState(Enum):
    SWIMMING = "swimming"
    CAUGHT = "caught"
    CAPTURED = "captured"
    EATEN = "eaten"

class SharkState(Enum):
    PATROLLING = "patrolling"
    SELECTED = "selected"
    CHASING = "chasing"
    ATTACKING = "attacking"
    DAMAGED = "damaged"
    RETREATING = "retreating"
    RECOVERING = "recovering"

class TradingState(Enum):
    IDLE = "idle"
    SELLING = "selling"
    UPGRADING = "upgrading"
    TRANSACTION_COMPLETE = "transaction_complete"

class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y, surface):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft=(x, y))
        self.x = float(x) # x坐标
        self.y = float(y) # y坐标
        self.speed = [0, 0]
        
    def move(self):
        self.x += self.speed[0]
        self.y += self.speed[1]
        self.rect.topleft = (int(self.x), int(self.y))

def create_fisherman_surface():
    # 加载并缩放老人图片
    original = pygame.image.load("assets/img/old_man.png")
    return pygame.transform.scale(original, (48, 48))

def create_marlin_surface():
    # 加载并缩放马林鱼图片
    original = pygame.image.load("assets/img/marlin_fish.png")
    return pygame.transform.scale(original, (100, 80))  # 调整大小为64x32

def create_shark_surface():
    # 加载并缩放鲨鱼图片 
    original = pygame.image.load("assets/img/shark.png")
    return pygame.transform.scale(original, (72, 40))  # 调整大小为72x40

def create_boat_surface():
    surface = pygame.Surface((64, 32), pygame.SRCALPHA)
    pygame.draw.polygon(surface, BROWN, [(0, 20), (64, 20), (56, 31), (8, 31)])
    pygame.draw.rect(surface, WHITE, (24, 0, 4, 20))
    pygame.draw.polygon(surface, WHITE, [(28, 2), (48, 10), (28, 18)])
    return surface

def create_hook_surface():
    surface = pygame.Surface((8, 16), pygame.SRCALPHA)
    pygame.draw.line(surface, GRAY, (4, 0), (4, 12), 2)
    pygame.draw.arc(surface, GRAY, (0, 8, 8, 8), 0, math.pi, 2)
    return surface

def create_fishing_line_surface():
    surface = pygame.Surface((2, 300), pygame.SRCALPHA)
    pygame.draw.line(surface, GRAY, (1, 0), (1, 300))
    return surface

def create_shop_surface():
    surface = pygame.Surface((200, 400), pygame.SRCALPHA)
    pygame.draw.rect(surface, DEEP_BLUE, (0, 0, 200, 400))
    return surface

def create_javelin_surface():
    surface = pygame.Surface((48, 48), pygame.SRCALPHA)
    pygame.draw.polygon(surface, WHITE, [(0, 24), (48, 24), (24, 48)])
    return surface


class Javelin(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, create_javelin_surface())
        self.rect = pygame.Rect(x, y, 8, 32)  # 修改碰撞框为细长形状
        self.attack_power = 1.0  # 基础攻击力
        self.speed = 12.0  # 飞行速度
        self.active = False  # 是否处于飞行状态
        self.angle = 0  # 飞行角度
        self.speed_x = 0  # x方向速度分量
        self.speed_y = 0  # y方向速度分量
        
    def auto_aim(self, start_pos, target):
        """自动瞄准目标"""
        self.active = True
        self.x, self.y = start_pos
        
        # 计算到目标的方向
        dx = target.x + target.rect.width/2 - start_pos[0]
        dy = target.y + target.rect.height/2 - start_pos[1]
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            # 计算速度分量
            self.speed_x = dx / distance * self.speed
            self.speed_y = dy / distance * self.speed
            # 计算角度用于旋转图像
            self.angle = math.degrees(math.atan2(dy, dx))
            
        # 旋转标枪图像
        self.image = pygame.transform.rotate(create_javelin_surface(), -self.angle)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
    def update(self, screen_width, screen_height):
        """更新标枪位置"""
        if not self.active:
            return False
            
        # 移动标枪
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.center = (self.x, self.y)
        
        # 检查是否超出屏幕
        if (self.x < 0 or self.x > screen_width or 
            self.y < 0 or self.y > screen_height):
            self.active = False
            return True
            
        return False
        
    def reset_position(self, fisherman):
        """重置标枪位置到渔夫身边"""
        self.active = False
        self.x = fisherman.x + 24
        self.y = fisherman.y + 24
        self.rect.center = (self.x, self.y)
        
                        
class Fisherman(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, create_fisherman_surface())
        self.name = "Asiv"
        self.attackFrequency = 1.0 # 攻击频率
        self.sharksKilled = 0
        self.marlinWeight = 0.0
        self.money = 0
        self.attack_power = 1.0
        self.hook_strength = 1.0
        self.fishing_speed = 1.0
        self.is_attacking = False  # 是否正在攻击
        self.rect = pygame.Rect(x, y, 48, 48)
        self.javelin = Javelin(x + 24, y + 24)  # 创建标枪
        self.javelin_cooldown = 0
        self.JAVELIN_COOLDOWN_TIME = 500  # 0.5秒冷却时间
        
    def can_attack(self, current_time):
        """检查是否可以发射标枪"""
        return current_time >= self.javelin_cooldown

class Boat(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, create_boat_surface())
        self.direction = "right"
        self.speed = [0, 0]
        self.itemCount = 0

class Marlin(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, create_marlin_surface())
        self.initial_weight = random.uniform(100, 300)  # 初始重量
        self.weight = self.initial_weight  # 当前重量
        self.being_caught = False  # 是否被钓中
        self.being_attacked = False  # 是否被鲨鱼攻击
        self.speed = [random.uniform(-2, 2), random.uniform(-1, 1)]
        self.rect = pygame.Rect(x, y, 100, 80)
        
    def move(self):
        if not self.being_caught:  # 只有在未被钓到时才移动
            self.x += self.speed[0]
            self.y += self.speed[1]
            
            # 边界检查和反弹
            if self.x < 0 or self.x > 1200 - self.rect.width:
                self.speed[0] *= -1
            if self.y < 0 or self.y > 768 - self.rect.height:
                self.speed[1] *= -1
                
            self.rect.topleft = (int(self.x), int(self.y))

class Shark(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, create_shark_surface())
        self.initial_weight = random.uniform(200, 500)
        self.weight = self.initial_weight
        self.vitality = 150 # 生命值
        self.foodCapacity = self.weight * 0.2 # 食物容量
        self.attackFrequency = 1.5 # 攻击频率
        self.attackPower = 1.0
        self.speed = [0, 0]
        self.target = None
        self.state = SharkState.PATROLLING
        self.rect = pygame.Rect(x, y, 72, 40)
        self.target = None
        self.is_attacking = False

class Hook(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, create_hook_surface())
        self.angle = -90 # 钩子角度 默认朝下
        self.length = 0
        self.max_length = 400  
        self.extension_speed = 4
        self.retraction_speed = 1
        self.state = HookState.IDLE
        self.caught_fish = None
        
    def swing(self):
        
        self.state = HookState.SWINGING
                
class Shop:
    def __init__(self):
        # 加载图标
        self.icons = {
            "hook_strength": pygame.image.load("assets/icons/strength.png"),
            "fishing_speed": pygame.image.load("assets/icons/speed.png"),
            "attack_power": pygame.image.load("assets/icons/attack.png")
        }
        # 调整图标大小
        for key in self.icons:
            self.icons[key] = pygame.transform.scale(self.icons[key], (48, 48))
        self.selected_item = None
        self.marlin_price = 1  # 马林鱼价格 1金币/重量单位
        self.fish_price_multiplier = 1.0 # 马林鱼价格倍数
        self.update_interval = 10000   # 价格更新间隔 ms 10s
        self.last_update = 0 # 上次更新时间    
        self.upgrades = {
            "hook_strength": {
                "name": "Hook Strength",
                "cost": 100,
                "level": 1,
                "max_level": 5,
                "increment": 0.2,
                "description": "Increases fishing power"
            },
            "fishing_speed": {
                "name": "Fishing Speed",
                "cost": 150,
                "level": 1,
                "max_level": 5,
                "increment": 0.2,
                "description": "Speeds up fishing"
            },
            "attack_power": {
                "name": "Attack Power",
                "cost": 200,
                "level": 1,
                "max_level": 5,
                "increment": 0.3,
                "description": "Increases shark damage"
            }
        }
        
    def update_fish_price(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.update_interval:
            self.fish_price_multiplier = random.uniform(0.8, 1.5)
            self.last_update = current_time
