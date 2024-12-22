from abc import ABC, abstractmethod
from typing import List
import random
from dataclasses import dataclass
import time
import pygame
import sys

# 视频播放相关的适配器模式实现
class VideoPlayer(ABC):
    @abstractmethod
    def play(self, video_path: str):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def stop(self):
        pass

class MP4Player:
    def playMP4(self, file_path: str):
        print(f"Playing MP4 video: {file_path}")

    def pauseMP4(self):
        print("Pausing MP4 video")

    def stopMP4(self):
        print("Stopping MP4 video")

class AVIPlayer:
    def startAVI(self, file_path: str):
        print(f"Starting AVI video: {file_path}")

    def pauseAVI(self):
        print("Pausing AVI video")

    def endAVI(self):
        print("Ending AVI video")

class GIFPlayer:
    def showGIF(self, file_path: str):
        print(f"Showing GIF animation: {file_path}")

    def freezeGIF(self):
        print("Freezing GIF animation")

    def closeGIF(self):
        print("Closing GIF animation")

# 视频播放适配器
class MP4PlayerAdapter(VideoPlayer):
    def __init__(self):
        self.mp4_player = MP4Player()

    def play(self, video_path: str):
        self.mp4_player.playMP4(video_path)

    def pause(self):
        self.mp4_player.pauseMP4()

    def stop(self):
        self.mp4_player.stopMP4()

class AVIPlayerAdapter(VideoPlayer):
    def __init__(self):
        self.avi_player = AVIPlayer()

    def play(self, video_path: str):
        self.avi_player.startAVI(video_path)

    def pause(self):
        self.avi_player.pauseAVI()

    def stop(self):
        self.avi_player.endAVI()

class GIFPlayerAdapter(VideoPlayer):
    def __init__(self):
        self.gif_player = GIFPlayer()

    def play(self, video_path: str):
        self.gif_player.showGIF(video_path)

    def pause(self):
        self.gif_player.freezeGIF()

    def stop(self):
        self.gif_player.closeGIF()

class Resource:
    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity

class Fish:
    def __init__(self, type_: str, position: str):
        self.type = type_
        self.position = position

    def swim(self):
        print(f"{self.type} is swimming at {self.position}")

class Shark(Fish):
    def __init__(self, type_: str, position: str, weight: float, vitality: float,
                 food_capacity: float, attack_frequency: float):
        super().__init__(type_, position)
        self.weight = weight
        self.vitality = vitality
        self.food_capacity = food_capacity
        self.attack_frequency = attack_frequency

    def feed(self):
        print(f"{self.type} shark is feeding")

    def take_damage(self, damage: float):
        self.vitality -= damage
        print(f"Shark took {damage} damage, remaining vitality: {self.vitality}")

    def bleed(self):
        print("Shark is bleeding")

class Marlin(Fish):
    def __init__(self, type_: str, position: str, weight: float, vitality: float,
                 food_capacity: float):
        super().__init__(type_, position)
        self.weight = weight
        self.vitality = vitality
        self.food_capacity = food_capacity

    def feed(self):
        print(f"{self.type} marlin is feeding")

    def take_damage(self, damage: float):
        self.vitality -= damage
        print(f"Marlin took {damage} damage, remaining vitality: {self.vitality}")

    def bleed(self):
        print("Marlin is bleeding")

class Boat:
    def __init__(self, coordinates: str, direction: str, speed: float,
                 capacity: int, fuel: float):
        self.coordinates = coordinates
        self.direction = direction
        self.speed = speed
        self.capacity = capacity
        self.fuel = fuel
        self.video_player = MP4PlayerAdapter()  # 默认使用MP4播放器

    def sail(self):
        self.fuel -= 1
        print(f"Sailing {self.direction} at speed {self.speed}, fuel remaining: {self.fuel}")
        self.video_player.play("sailing.mp4")

    def stop(self):
        print("Boat stopped")
        self.video_player.stop()

    def return_to_shore(self):
        print("Returning to shore")
        self.video_player.play("return.mp4")

    def upgrade(self):
        self.capacity += 1
        self.speed += 0.5
        print(f"Boat upgraded: capacity={self.capacity}, speed={self.speed}")

class Merchant:
    def __init__(self, name: str, inventory: List[Resource]):
        self.name = name
        self.inventory = inventory

    def trade(self, fisherman):
        print(f"Trading with {fisherman.name}")

class Weather:
    def __init__(self, condition: str, visibility: float, fish_activity_rate: float):
        self.condition = condition
        self.visibility = visibility
        self.fish_activity_rate = fish_activity_rate
        self.video_player = GIFPlayerAdapter()  # 天气动画使用GIF

    def affect_fisherman(self, fisherman):
        if self.condition == "storm":
            fisherman.ATK *= 0.8
        self.video_player.play(f"weather_{self.condition}.gif")

    def affect_fish(self, fish):
        if self.condition == "sunny":
            fish.swim()

class RivalFisherman:
    def __init__(self, name: str, skill_level: int, catch_rate: float):
        self.name = name
        self.skill_level = skill_level
        self.catch_rate = catch_rate
        self.video_player = AVIPlayerAdapter()  # 竞争场景使用AVI

    def compete(self, fisherman):
        print(f"Competing with {fisherman.name}")
        self.video_player.play("competition.avi")

class Fisherman:
    def __init__(self, name: str, ATK: int, attack_frequency: float):
        self.name = name
        self.ATK = ATK
        self.attack_frequency = attack_frequency
        self.sharks_killed = 0
        self.marlin_weight = 0
        self.resources: List[Resource] = []
        self.boat = Boat("0,0", "N", 10, 100, 1000)
        self.video_player = MP4PlayerAdapter()  # 捕鱼场景使用MP4

    def operation(self):
        print(f"{self.name} is operating the boat")
        self.boat.sail()

    def attack(self, shark: Shark):
        damage = self.ATK * self.attack_frequency
        shark.take_damage(damage)
        if shark.vitality <= 0:
            self.sharks_killed += 1
            print(f"Shark killed! Total sharks killed: {self.sharks_killed}")
            self.video_player.play("shark_killed.mp4")

    def catch(self, fish: Fish):
        if isinstance(fish, Marlin):
            self.marlin_weight += fish.weight
            print(f"Caught marlin! Total weight: {self.marlin_weight}")
            self.video_player.play("catch_marlin.mp4")

    def find_fish(self) -> Fish:
        fish_type = random.choice(["Marlin", "Shark"])
        position = f"{random.randint(0, 100)},{random.randint(0, 100)}"
        
        if fish_type == "Marlin":
            return Marlin("Blue", position, 100, 100, 50)
        else:
            return Shark("Great White", position, 200, 150, 100, 0.5)

    def upgrade_equipment(self):
        self.ATK += 5
        self.attack_frequency += 0.1
        print(f"Equipment upgraded: ATK={self.ATK}, attack_frequency={self.attack_frequency}")

    def trade_with_merchant(self, merchant: Merchant):
        merchant.trade(self)
        


def main():
    pygame.init()
    screen_width, screen_height = 1024, 1024
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("老人与海")

    # 加载2048*2048背景
    background = pygame.image.load("../assets/backgroud.jpg").convert()
    #缩放到窗口大小
    background = pygame.transform.scale(background, (screen_width, screen_height))
    
    #缩小到原来的20%
    old_man_img = pygame.image.load("../assets/old_man.png").convert_alpha()
    old_man_img = pygame.transform.scale(old_man_img, (old_man_img.get_width() // 5, old_man_img.get_height() // 5))

    boat_img = pygame.image.load("../assets/boat.png").convert_alpha()
    boat_img = pygame.transform.scale(boat_img, (boat_img.get_width() // 5, boat_img.get_height() // 5))

    shark_img = pygame.image.load("../assets/shark.png").convert_alpha()
    shark_img = pygame.transform.scale(shark_img, (shark_img.get_width() // 2, shark_img.get_height() // 2))

    marlin_img = pygame.image.load("../assets/marha_fish.png").convert_alpha()
    marlin_img = pygame.transform.scale(marlin_img, (marlin_img.get_width() // 3, marlin_img.get_height() // 3))

    pygame.mixer.music.load("../assets/sound/Calm_ocean _waves.mp3")
    pygame.mixer.music.play(-1)

    clock = pygame.time.Clock()

    # 简单初始坐标设置（水平居中，海平面大致位于 y=400）
    global game_state
    game_state = "TRAVELING"

   
    fisherman_pos = [400, 360]  # 老人在海平面
    boat_pos = [400, 420]  # 船在海平面
    marlin_pos = [200, 700]                               # 马林鱼在海中
    shark_pos = [600, 800]                                # 鲨鱼在海中

    # 贴图偏移量
    bg_offset_x = 0
    bg_offset_y = 0

    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            fisherman_pos[0] -= 5
        if keys[pygame.K_RIGHT]:
            fisherman_pos[0] += 5

        run_sequence(fisherman_pos, boat_pos, marlin_pos, shark_pos)

        # 绘制背景（截取部分图像）
        screen.blit(background, (0, 0), (bg_offset_x, bg_offset_y, screen_width, screen_height))

        # 绘制角色
        screen.blit(old_man_img, fisherman_pos)
        screen.blit(boat_img, boat_pos)
        screen.blit(marlin_img, marlin_pos)
        screen.blit(shark_img, shark_pos)
        
        pygame.display.update()

if __name__ == "__main__":
    main()