# -*- coding: utf-8 -*-
import pygame
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from game_entities import GameState, GameConfig

class Scene(ABC):
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.next_scene = None

    @abstractmethod
    def update(self, events: list) -> Optional[str]:
        """更新场景，返回下一个场景名称或None"""
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface):
        """渲染场景"""
        pass

    def handle_input(self, keys):
        """处理输入"""
        pass


class MenuScene(Scene):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.font = pygame.font.Font(None, 74)
        self.menu_items = ['Start', 'Settings', 'Quit']
        self.selected_item = 0

    def update(self, events: list) -> Optional[str]:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                elif event.key == pygame.K_DOWN:
                    self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                elif event.key == pygame.K_RETURN:
                    if self.selected_item == 0:
                        return 'game'
                    elif self.selected_item == 1:
                        return 'settings'
                    elif self.selected_item == 2:
                        return 'quit'
        return None

    def render(self, screen: pygame.Surface):
        screen.fill((0, 0, 0))
        for i, item in enumerate(self.menu_items):
            color = (255, 255, 0) if i == self.selected_item else (255, 255, 255)
            text = self.font.render(item, True, color)
            x = GameConfig.SCREEN_WIDTH // 2 - text.get_width() // 2
            # 让菜单项在垂直方向依次排列
            y = GameConfig.SCREEN_HEIGHT // 2 + i * 80 - (len(self.menu_items) * 80) // 2
            screen.blit(text, (x, y))


class SettingsScene(Scene):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.font = pygame.font.Font(None, 60)

    def update(self, events: list) -> Optional[str]:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_RETURN]:
                    return 'menu'
        return None

    def render(self, screen: pygame.Surface):
        screen.fill((50, 50, 50))
        text = self.font.render("Settings, press ESC to return to menu", True, (255, 255, 255))
        x = GameConfig.SCREEN_WIDTH // 2 - text.get_width() // 2
        y = GameConfig.SCREEN_HEIGHT // 2 - text.get_height() // 2
        screen.blit(text, (x, y))


class GameScene(Scene):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.debug_mode = False
        self.paused = False

    def update(self, events: list) -> Optional[str]:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'menu'
                elif event.key == pygame.K_F3:
                    self.debug_mode = not self.debug_mode
                elif event.key == pygame.K_p:
                    self.paused = not self.paused

        if not self.paused:
            self.game_manager.update()

        if self.game_manager.state == GameState.GAME_OVER:
            return 'game_over'

        return None

    def render(self, screen: pygame.Surface):
        self.game_manager.render(screen)
        # 显示暂停遮罩
        if self.paused:
            s = pygame.Surface((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
            s.set_alpha(128)
            s.fill((0, 0, 0))
            screen.blit(s, (0, 0))
            font = pygame.font.Font(None, 74)
            text = font.render("PAUSED", True, (255, 255, 255))
            screen.blit(text, (GameConfig.SCREEN_WIDTH // 2 - text.get_width() // 2,
                               GameConfig.SCREEN_HEIGHT // 2 - text.get_height() // 2))

    def handle_input(self, keys):
        if not self.paused:
            self.game_manager.handle_input(keys)


class GameOverScene(Scene):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.font = pygame.font.Font(None, 74)

    def update(self, events: list) -> Optional[str]:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return 'game'
                elif event.key == pygame.K_ESCAPE:
                    return 'menu'
        return None

    def render(self, screen: pygame.Surface):
        # 保持背景显示
        self.game_manager.render(screen)
        # 加半透明遮罩
        s = pygame.Surface((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
        s.set_alpha(128)
        s.fill((0, 0, 0))
        screen.blit(s, (0, 0))
        # 显示文字
        text = self.font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(text, (GameConfig.SCREEN_WIDTH // 2 - text.get_width() // 2,
                           GameConfig.SCREEN_HEIGHT // 2 - text.get_height() // 2))
        instructions = pygame.font.Font(None, 36).render(
            "按 R 重新开始，ESC 返回菜单", True, (255, 255, 255)
        )
        screen.blit(instructions, (GameConfig.SCREEN_WIDTH // 2 - instructions.get_width() // 2,
                                   GameConfig.SCREEN_HEIGHT // 2 + 50))


class SceneManager:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.scenes = {
            'menu': MenuScene(game_manager),
            'settings': SettingsScene(game_manager),
            'game': GameScene(game_manager),
            'game_over': GameOverScene(game_manager)
        }
        self.current_scene = 'menu'

    def update(self, events: list) -> bool:
        next_scene = self.scenes[self.current_scene].update(events)
        if next_scene == 'quit':
            return False
        elif next_scene in self.scenes:
            self.current_scene = next_scene
        return True

    def render(self, screen: pygame.Surface):
        self.scenes[self.current_scene].render(screen)

    def handle_input(self, keys):
        self.scenes[self.current_scene].handle_input(keys)