# -*- coding: utf-8 -*-
from logic import GameLogic
from sprites import Boat, Fisherman, Hook, Marlin, Shark, HookState
import pygame
import random
import math
import time
from sprites import (Boat, Fisherman, Hook, Marlin, Shark, 
                    DEEP_BLUE, WHITE) 
from video_player import VideoPlayer
import os
from moviepy.editor import *

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen_width = 1200
        self.screen_height = 768
        self.screen = pygame.display.set_mode((self.screen_width, 
                                             self.screen_height))
        pygame.display.set_caption("老人与海")        
        self.game_logic = GameLogic(self.screen_width, self.screen_height)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        self.sounds = {
            'cheers': pygame.mixer.Sound('assets/sound/Cheers.mp3'),
            'attack': pygame.mixer.Sound('assets/sound/attack.mp3'),
            'ocean': pygame.mixer.Sound('assets/sound/Calm_ocean_waves.mp3')
        }
        self.sounds['ocean'].set_volume(0.5)
        # 初始化游戏对象
        self.init_game_objects()
        self.has_played_intro = False
            
                
    def init_game_objects(self):
        self.boat = Boat(self.screen_width//2, self.screen_height//2)
        self.fisherman = Fisherman(self.boat.x + 16, self.boat.y - 16)
        self.game_logic.set_fisherman(self.fisherman)
        self.hook = Hook(self.fisherman.x, self.fisherman.y)
        self.marlins = [Marlin(random.randint(0, self.screen_width), 
                              random.randint(0, self.screen_height)) 
                       for _ in range(3)]
        self.sharks = [Shark(random.randint(0, self.screen_width), 
                           random.randint(0, self.screen_height)) 
                      for _ in range(2)]
        
        self.game_logic.set_sounds(self.sounds)
    
    def play_intro(self):
        """播放游戏介绍视频"""
        video_file = os.path.join("assets", "video", "intro.mp4")
        player = VideoPlayer(self.screen)
        player.play_video(video_file)
        
                        
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # 船只移动控制
        self.boat.speed = [0, 0]
        if keys[pygame.K_LEFT]:
            self.boat.speed[0] = -2
        elif keys[pygame.K_RIGHT]:
            self.boat.speed[0] = 2
        if keys[pygame.K_UP]:
            self.boat.speed[1] = -2
        elif keys[pygame.K_DOWN]:
            self.boat.speed[1] = 2
            
        # 钓鱼控制
        if keys[pygame.K_SPACE]:
            if self.hook.state == HookState.IDLE:
                self.hook.state = HookState.SWINGING
        elif keys[pygame.K_RETURN]:
            if self.hook.state == HookState.SWINGING:
                self.hook.state = HookState.EXTENDING
            elif self.game_logic.attacking_shark:
                self.fisherman.is_attacking = True
        else:
            self.fisherman.is_attacking = False
            
    def draw_ui(self):
        # 显示得分和状态
        score_text = f"Score: {self.game_logic.score}"
        money_text = f"Golds: {self.game_logic.fisherman.money}"
        marlin_text = f"fished marlin: {self.game_logic.current_marlin_weight:.2f} kg"
        sharks_text = f"sharks killed: {self.game_logic.sharks_defeated}"
        
        y = 10
        for text in [score_text, money_text, marlin_text, sharks_text]:
            surface = self.font.render(text, True, WHITE)
            self.screen.blit(surface, (10, y))
            y += 30
            
        if self.hook.state == HookState.IDLE:  # 使用枚举而不是字符串
            hint_text = "Press SPACE to cast the hook"
            hint_surface = self.font.render(hint_text, True, (255, 255, 0))
            self.screen.blit(hint_surface, (self.screen_width//2 - hint_surface.get_width()//2, 
                                    self.screen_height - 50))
        elif self.hook.state == HookState.SWINGING:  # 使用枚举而不是字符串
            hint_text = "Press ENTER to extend the hook"
            hint_surface = self.font.render(hint_text, True, (255, 255, 0))
            self.screen.blit(hint_surface, (self.screen_width//2 - hint_surface.get_width()//2, 
                                    self.screen_height - 50))
            
    def draw_shop_menu(self):
        # 绘制商店背景
        shop_surface = pygame.Surface((350, self.screen_height), pygame.SRCALPHA)
        pygame.draw.rect(shop_surface, (0, 0, 0, 180), (0, 0, 350, self.screen_height))
        self.screen.blit(shop_surface, (self.screen_width - 350, 0))
        
        # 绘制商店标题
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("SHOP", True, (255, 215, 0))
        self.screen.blit(title, (self.screen_width - 320, 20))
        
        # 绘制商店物品
        y = 80
        for idx, (item, data) in enumerate(self.game_logic.shop.upgrades.items()):
            # 绘制物品背景
            item_bg = pygame.Surface((320, 100), pygame.SRCALPHA)
            if self.game_logic.fisherman.money >= data['cost']:
                bg_color = (255, 255, 255, 30)
            else:
                bg_color = (255, 0, 0, 30)
            pygame.draw.rect(item_bg, bg_color, (0, 0, 320, 100), border_radius=10)
            self.screen.blit(item_bg, (self.screen_width - 335, y))
            
            # 绘制图标
            icon = self.game_logic.shop.icons[item]
            self.screen.blit(icon, (self.screen_width - 325, y + 26))
            
            # 绘制物品信息
            name = f"{data['name']}"
            level = f"Level: {data['level']}/{data['max_level']}"
            cost = f"Cost: {data['cost']} Gold"
            description = data['description']
            
            # 使用不同字体大小
            name_surface = self.font.render(name, True, WHITE)
            level_surface = pygame.font.Font(None, 24).render(level, True, (200, 200, 200))
            cost_surface = pygame.font.Font(None, 28).render(cost, True, (255, 215, 0))
            desc_surface = pygame.font.Font(None, 24).render(description, True, (180, 180, 180))
            
            # 调整文本位置
            self.screen.blit(name_surface, (self.screen_width - 265, y + 15))
            self.screen.blit(level_surface, (self.screen_width - 265, y + 40))
            self.screen.blit(cost_surface, (self.screen_width - 265, y + 65))
            self.screen.blit(desc_surface, (self.screen_width - 265, y + 90))
            
            
            # 绘制按键提示
            key_hint = f"Press {idx + 1}"
            key_surface = pygame.font.Font(None, 20).render(key_hint, True, (255, 255, 0))
            key_rect = key_surface.get_rect()
            key_rect.topright = (self.screen_width - 40, y + 15)
            self.screen.blit(key_surface, key_rect)
            
            y += 140  # 增加间距
            
    def draw_fishing_line(self):
        if self.hook.state != HookState.IDLE:
            # 计算钓鱼线的起点（渔夫位置）
            start_pos = (self.fisherman.x + 16, self.fisherman.y + 16)
            # 计算钓鱼线的终点（钩子位置）
            end_pos = (self.hook.x + 4, self.hook.y)
            
            # 绘制钓鱼线
            pygame.draw.line(self.screen, (128, 128, 128), start_pos, end_pos, 2)
            
            # 如果处于摆动状态，显示角度指示器
            if self.hook.state == HookState.SWINGING:
                # 绘制角度指示器的半透明扇形
                radius = 50
                start_angle = math.radians(-80)
                end_angle = math.radians(80)
                points = [(self.fisherman.x + 16, self.fisherman.y + 16)]
                
                for angle in range(-80, 81, 5):
                    rad = math.radians(angle)
                    x = self.fisherman.x + 16 + math.cos(rad) * radius
                    y = self.fisherman.y + 16 + math.sin(rad) * radius
                    points.append((x, y))
                
                points.append((self.fisherman.x + 16, self.fisherman.y + 16))
                pygame.draw.polygon(self.screen, (255, 255, 255, 30), points)
                   
    def run(self):
        running = True
        while running:
            if not self.has_played_intro:
                 self.play_intro()
            self.has_played_intro = True
            current_time = pygame.time.get_ticks()  # 获取当前时间
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.game_logic.shop.purchase_upgrade("hook_strength", 
                                                           self.fisherman)
                    elif event.key == pygame.K_2:
                        self.game_logic.shop.purchase_upgrade("fishing_speed", 
                                                           self.fisherman)
                    elif event.key == pygame.K_3:
                        self.game_logic.shop.purchase_upgrade("attack_power", 
                                                           self.fisherman)
            
            self.handle_input()
            
            # 更新游戏对象
            self.boat.move()
            self.fisherman.x = self.boat.x + 16
            self.fisherman.y = self.boat.y - 16
            self.fisherman.rect.topleft = (int(self.fisherman.x), 
                                         int(self.fisherman.y))
            
            # 更新标枪状态
            self.game_logic.update_javelin(current_time)
            
            # 自动攻击
            self.game_logic.auto_attack(current_time)
            
            # 更新钓鱼钩状态
            self.game_logic.update_hook(self.hook, self.fisherman, self.marlins, self.sharks)
            
            # 更新商店
            self.game_logic.shop.update_fish_price()
            
            # 更新鱼类
            for marlin in self.marlins[:]:
                marlin.move()
            
            # 更新鲨鱼和AI行为
            self.game_logic.update_shark_behavior(self.sharks, self.hook, self.fisherman, self.marlins)
            
            # 补充马林鱼和鲨鱼
            while len(self.marlins) < 3:
                self.marlins.append(Marlin(random.randint(0, self.screen_width), 
                                         random.randint(0, self.screen_height)))
            while len(self.sharks) < 2:
                self.sharks.append(Shark(random.randint(0, self.screen_width), 
                                       random.randint(0, self.screen_height)))
            
            # 绘制
            self.screen.fill(DEEP_BLUE)
            
            for marlin in self.marlins:
                self.screen.blit(marlin.image, marlin.rect)
            for shark in self.sharks:
                self.screen.blit(shark.image, shark.rect)
            
            self.draw_fishing_line()
            
            self.screen.blit(self.boat.image, self.boat.rect)
            self.screen.blit(self.fisherman.image, self.fisherman.rect)
            
            # 绘制标枪
            if self.fisherman.javelin.active:
                self.screen.blit(self.fisherman.javelin.image, 
                                self.fisherman.javelin.rect)
                
            if self.hook.state != "idle":
                self.screen.blit(self.hook.image, self.hook.rect)
            
            self.draw_ui()
            self.draw_shop_menu()
            
            pygame.display.flip()
            self.clock.tick(60)
        pygame.mixer.quit()    
        pygame.quit()
        
if __name__ == "__main__":
    game = Game()
    game.run()