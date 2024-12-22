import pygame
import math
import random
from typing import List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

class GameState(Enum):
    INIT = "INIT"
    TRAVELING = "TRAVELING"
    FISHING = "FISHING"
    FIGHTING_MARLIN = "FIGHTING_MARLIN"
    RETURNING = "RETURNING"
    FIGHTING_SHARKS = "FIGHTING_SHARKS"
    GAME_OVER = "GAME_OVER"

@dataclass
class GameConfig:
    """游戏配置数据类"""
    SCREEN_WIDTH: int = 1024
    SCREEN_HEIGHT: int = 1024
    FPS: int = 60
    PLAYER_SPEED: float = 5.0
    SHARK_SPEED: float = 3.0
    MARLIN_SPEED: float = 4.0
    MAX_STAMINA: float = 100.0
    MAX_FUEL: float = 100.0
    STAMINA_RECOVER_RATE: float = 0.5
    DAMAGE_MULTIPLIER: float = 1.0

class GameObject:
    def __init__(self, position: List[float], image_path: str, target_size: Tuple[int, int]):
        self.position = position.copy()
        self.original_position = position.copy()
        self.target_size = target_size
        self.speed = [0.0, 0.0]
        self.angle = 0.0  # 朝向角度
        self.active = True
        self.debug_mode = False
        
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.original_image = self.image.copy()
            self.image = pygame.transform.scale(self.image, target_size)
            self.rect = self.image.get_rect()
            self.update_rect_position()
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            self.create_placeholder()

    def create_placeholder(self):
        """创建占位图形"""
        self.image = pygame.Surface(self.target_size, pygame.SRCALPHA)
        self.image.fill((255, 0, 0, 128))
        pygame.draw.rect(self.image, (255, 255, 255), self.image.get_rect(), 1)
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()

    def update_rect_position(self):
        """更新碰撞矩形位置"""
        self.rect.center = (int(self.position[0]), int(self.position[1]))

    def rotate(self, angle: float):
        """旋转图像"""
        self.angle = angle
        rotated = pygame.transform.rotate(self.original_image, -angle)
        self.image = pygame.transform.scale(rotated, self.target_size)
        self.rect = self.image.get_rect(center=self.rect.center)

    def move_towards(self, target_pos: List[float], speed: float):
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            # 此处确保赋值为 [x, y] 形式
            self.speed = [dx/distance * speed, dy/distance * speed]
            self.angle = math.degrees(math.atan2(-dy, dx))
            self.rotate(self.angle)

    def update(self):
        """更新对象状态"""
        if isinstance(self.speed, list) and isinstance(self.position, list):
            self.position[0] += self.speed[0]
            self.position[1] += self.speed[1]
            self.update_rect_position()

    def draw(self, screen: pygame.Surface):
        """绘制对象"""
        if not self.active:
            return
            
        screen.blit(self.image, self.rect)
        
        if self.debug_mode:
            # 绘制碰撞箱
            pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)
            # 绘制坐标
            font = pygame.font.Font(None, 24)
            text = f"({int(self.position[0])},{int(self.position[1])})"
            text_surf = font.render(text, True, (255, 255, 255))
            screen.blit(text_surf, (self.rect.x, self.rect.bottom + 5))

    def reset(self):
        """重置对象状态"""
        self.position = self.original_position.copy()
        self.speed = [0.0, 0.0]
        self.angle = 0.0
        self.active = True
        self.update_rect_position()

class Fisherman(GameObject):
    def __init__(self, position: List[float]):
        super().__init__(position, "../assets/old_man.png", (80, 160))
        self.stamina = GameConfig.MAX_STAMINA
        self.fishing_skill = 1.0
        self.strength = 10.0
        self.exp = 0.0
        self.level = 1
        self.has_marlin = False
        self.status_effects = []
        self.last_rest_time = 0
        
    def update(self):
        super().update()
        self.update_status_effects()
        self.natural_stamina_recovery()
        
    def fish(self) -> bool:
        if self.stamina < 5:
            return False
        self.stamina -= 5
        success_chance = 0.1 * self.fishing_skill * (self.stamina / GameConfig.MAX_STAMINA)
        return random.random() < success_chance

    def rest(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_rest_time > 1000:  # 1秒冷却
            self.stamina = min(GameConfig.MAX_STAMINA, 
                             self.stamina + GameConfig.STAMINA_RECOVER_RATE)
            self.last_rest_time = current_time

    def attack(self) -> float:
        if self.stamina < 10:
            return 0
        self.stamina -= 10
        base_damage = self.strength * (0.8 + random.random() * 0.4)
        crit_chance = 0.1 * (self.level / 10)
        if random.random() < crit_chance:
            base_damage *= 2
        return base_damage * GameConfig.DAMAGE_MULTIPLIER

    def gain_exp(self, amount: float):
        self.exp += amount
        while self.exp >= 100 * self.level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.exp -= 100 * (self.level - 1)
        self.strength *= 1.1
        self.fishing_skill *= 1.1
        
    def update_status_effects(self):
        current_time = pygame.time.get_ticks()
        self.status_effects = [effect for effect in self.status_effects 
                             if effect['end_time'] > current_time]
                             
    def natural_stamina_recovery(self):
        if len(self.status_effects) == 0:  # 无debuff时自然恢复
            self.stamina = min(GameConfig.MAX_STAMINA, 
                             self.stamina + GameConfig.STAMINA_RECOVER_RATE * 0.1)

class Boat(GameObject):
    def __init__(self, position: List[float]):
        super().__init__(position, "../assets/boat.png", (200, 100))
        self.fuel = GameConfig.MAX_FUEL
        self.durability = 100.0
        self.max_speed = GameConfig.PLAYER_SPEED
        self.cargo_capacity = 100.0
        self.cargo_weight = 0.0
        self.engine_level = 1
        self.hull_level = 1
        
    def move(self, direction: List[float]) -> bool:
        if self.fuel <= 0:
            return False
            
        # 计算实际速度（考虑货物重量）
        actual_speed = self.max_speed * (1 - self.cargo_weight / self.cargo_capacity)
        self.speed = [direction[0] * actual_speed, direction[1] * actual_speed]
        
        # 消耗燃料（速度越快消耗越多）
        speed_magnitude = math.sqrt(self.speed[0]**2 + self.speed[1]**2)
        fuel_consumption = 0.1 * (speed_magnitude / self.max_speed)
        self.fuel = max(0, self.fuel - fuel_consumption)
        
        return True
        
    def repair(self):
        repair_amount = 10 * (1 + 0.1 * (self.hull_level - 1))
        self.durability = min(100, self.durability + repair_amount)
        
    def refuel(self):
        self.fuel = min(GameConfig.MAX_FUEL, self.fuel + 20)
        
    def upgrade_engine(self):
        self.engine_level += 1
        self.max_speed *= 1.1
        
    def upgrade_hull(self):
        self.hull_level += 1
        self.cargo_capacity *= 1.1
        
    def take_damage(self, amount: float):
        self.durability = max(0, self.durability - amount)

class Marlin(GameObject):
    def __init__(self, position: List[float]):
        super().__init__(position, "../assets/marlin_fish.png", (160, 80))
        self.health = 100.0
        self.max_health = 100.0
        self.strength = 15.0
        self.speed = GameConfig.MARLIN_SPEED
        self.is_hooked = False
        self.escape_attempts = 3
        self.state = "patrolling"  # patrolling, chasing, fleeing
        self.patrol_points = []
        self.current_patrol_point = 0
        
    def update(self):
        super().update()
        if not self.is_hooked:
            self.update_ai_behavior()
            
    def update_ai_behavior(self):
        if self.state == "patrolling":
            if self.patrol_points:
                target = self.patrol_points[self.current_patrol_point]
                self.move_towards(target, self.speed)
                if self.rect.collidepoint(target):
                    self.current_patrol_point = (self.current_patrol_point + 1) % len(self.patrol_points)
                    
    def struggle(self) -> float:
        if not self.is_hooked or self.escape_attempts <= 0:
            return 0
        self.escape_attempts -= 1
        return self.strength * (0.8 + random.random() * 0.4)
        
    def take_damage(self, damage: float):
        self.health = max(0, self.health - damage)
        if random.random() < 0.2 or self.health <= 0:
            self.is_hooked = False
            
    def set_patrol_points(self, points: List[List[float]]):
        self.patrol_points = points
        self.current_patrol_point = 0

class Shark(GameObject):
    def __init__(self, position: List[float]):
        super().__init__(position, "../assets/shark.png", (120, 60))
        self.health = 80.0
        self.max_health = 80.0
        self.attack_power = 20.0
        self.speed = GameConfig.SHARK_SPEED
        self.aggression = random.random() * 0.5 + 0.5  # 50%-100%的攻击性
        self.state = "patrolling"
        self.target = None
        self.last_attack_time = 0
        self.attack_cooldown = 1000  # 1秒冷却
        
    def update(self):
        super().update()
        self.update_ai_behavior()
        
    def update_ai_behavior(self):
        current_time = pygame.time.get_ticks()
        if self.target and self.state == "chasing":
            if current_time - self.last_attack_time > self.attack_cooldown:
                # 检查是否在攻击范围内
                distance = math.sqrt((self.target.position[0] - self.position[0])**2 +
                                  (self.target.position[1] - self.position[1])**2)
                if distance < 50:  # 攻击范围
                    self.perform_attack()
                    self.last_attack_time = current_time
                else:
                    self.move_towards(self.target.position, self.speed)
        
    def perform_attack(self):
        if not self.target:
            return
        damage = self.attack_power * self.aggression * (0.8 + random.random() * 0.4)
        if isinstance(self.target, Boat):
            self.target.take_damage(damage)
        
    def take_damage(self, damage: float):
        self.health = max(0, self.health - damage)
        if self.health < self.max_health * 0.3:  # 低于30%血量可能逃跑
            if random.random() < 0.3:
                self.state = "fleeing"
                
    def set_target(self, target: GameObject):
        self.target = target
        if target:
            self.state = "chasing"
        else:
            self.state = "patrolling"

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.sound_cooldowns = {}
        self._load_sounds()
        
    def _load_sounds(self):
        sound_files = {
            'wave': "../assets/sound/Calm_ocean _waves.mp3",
            'attack': "../assets/sound/attack.mp3",
            'cheer': "../assets/sound/Cheers.mp3"
        }
        
        for name, path in sound_files.items():
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
                self.sound_cooldowns[name] = 0
            except Exception as e:
                print(f"Error loading sound {path}: {e}")
                
    def play_sound(self, sound_name: str, cooldown: int = 100):
        current_time = pygame.time.get_ticks()
        if (sound_name in self.sounds and 
            current_time - self.sound_cooldowns.get(sound_name, 0) > cooldown):
            self.sounds[sound_name].play()
            self.sound_cooldowns[sound_name] = current_time
            
    def play_background(self):
        if 'wave' in self.sounds:
            try:
                self.sounds['wave'].play(-1)  # -1表示循环播放
            except Exception as e:
                print(f"Error playing background sound: {e}")
                
    def stop_sound(self, sound_name: str):
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].stop()
            except Exception as e:
                print(f"Error stopping sound {sound_name}: {e}")
                
    def set_volume(self, sound_name: str, volume: float):
        """设置音量 (0.0 到 1.0)"""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].set_volume(volume)
            except Exception as e:
                print(f"Error setting volume for {sound_name}: {e}")
    
    def stop_all(self):
        """停止所有音效"""
        try:
            pygame.mixer.stop()
        except Exception as e:
            print(f"Error stopping all sounds: {e}")

class VideoPlayer:
    def __init__(self):
        self.current_video = None
        self.is_playing = False
        self.video_surface = None
        self.video_rect = None
        self.frame_count = 0
        self._load_success = False
        
    def load_video(self, video_path: str, target_size: Tuple[int, int] = None):
        """加载视频文件"""
        try:
            # 这里使用了适配器模式，支持多种视频格式
            video_extension = video_path.split('.')[-1].lower()
            
            if video_extension == 'mp4':
                self.current_video = MP4PlayerAdapter()
            elif video_extension == 'avi':
                self.current_video = AVIPlayerAdapter()
            elif video_extension == 'gif':
                self.current_video = GIFPlayerAdapter()
            else:
                raise ValueError(f"Unsupported video format: {video_extension}")
                
            self.current_video.load(video_path)
            if target_size:
                self.video_rect = pygame.Rect((0, 0), target_size)
            self._load_success = True
            
        except Exception as e:
            print(f"Error loading video {video_path}: {e}")
            self._load_success = False
        
    def play(self):
        """播放视频"""
        if self._load_success and self.current_video:
            try:
                self.current_video.play()
                self.is_playing = True
            except Exception as e:
                print(f"Error playing video: {e}")
                
    def pause(self):
        """暂停视频"""
        if self.is_playing and self.current_video:
            try:
                self.current_video.pause()
                self.is_playing = False
            except Exception as e:
                print(f"Error pausing video: {e}")
                
    def stop(self):
        """停止视频"""
        if self.current_video:
            try:
                self.current_video.stop()
                self.is_playing = False
            except Exception as e:
                print(f"Error stopping video: {e}")
                
    def update(self, screen: pygame.Surface):
        """更新视频帧"""
        if self.is_playing and self.current_video:
            try:
                frame = self.current_video.get_frame()
                if frame:
                    if self.video_rect:
                        frame = pygame.transform.scale(frame, self.video_rect.size)
                    screen.blit(frame, self.video_rect or (0, 0))
                    self.frame_count += 1
            except Exception as e:
                print(f"Error updating video frame: {e}")
                
    def is_finished(self) -> bool:
        """检查视频是否播放完成"""
        if self.current_video:
            return self.current_video.is_finished()
        return True

# 视频播放适配器
class VideoPlayerAdapter:
    def load(self, path: str):
        pass
        
    def play(self):
        pass
        
    def pause(self):
        pass
        
    def stop(self):
        pass
        
    def get_frame(self) -> Optional[pygame.Surface]:
        pass
        
    def is_finished(self) -> bool:
        pass

class MP4PlayerAdapter(VideoPlayerAdapter):
    def __init__(self):
        self.mp4_player = None
        self.current_frame = None
        self.frame_index = 0
        
    def load(self, path: str):
        try:
            # 实际项目中需要使用支持MP4的库
            pass
        except Exception as e:
            print(f"Error loading MP4: {e}")
            
    def get_frame(self) -> Optional[pygame.Surface]:
        if self.mp4_player:
            try:
                # 获取当前帧
                pass
            except Exception:
                return None
        return None

class GIFPlayerAdapter(VideoPlayerAdapter):
    def __init__(self):
        self.frames = []
        self.current_frame = 0
        self.frame_count = 0
        self.frame_delay = 0
        self.last_update = 0
        
    def load(self, path: str):
        try:
            # 加载GIF文件
            pass
        except Exception as e:
            print(f"Error loading GIF: {e}")
            
    def get_frame(self) -> Optional[pygame.Surface]:
        if not self.frames:
            return None
            
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.frame_delay:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.last_update = current_time
            
        return self.frames[self.current_frame]