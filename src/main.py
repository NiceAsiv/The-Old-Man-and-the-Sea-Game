import pygame
import sys
import time

from game_entities import GameObject, Fisherman, Boat, Marlin, Shark, GameState
from game_manager import GameManager

def main():
    # 初始化Pygame
    pygame.init()
    screen_width, screen_height = 1024, 1024
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("老人与海")
    
    # 创建游戏管理器
    game_manager = GameManager(screen_width, screen_height)
    
    # 游戏循环
    clock = pygame.time.Clock()
    last_day_update = time.time()
    
    while True:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        # 获取键盘输入
        keys = pygame.key.get_pressed()
        
        # 检查是否需要更新天数
        current_time = time.time()
        if current_time - last_day_update >= 60:  # 每60秒为一天
            game_manager.update_day_cycle()
            last_day_update = current_time
        
        # 更新游戏状态
        if game_manager.state != GameState.GAME_OVER:
            game_manager.handle_input(keys)
            game_manager.update()
            game_manager.check_achievements()
            
            # 渲染游戏画面
            game_manager.render(screen)
        else:
            # 显示游戏结束画面
            game_manager.show_game_over(screen)
            game_manager.save_high_score()
            
            # 检查是否重新开始
            if keys[pygame.K_r]:
                game_manager = GameManager(screen_width, screen_height)
                last_day_update = time.time()
        
        # 更新显示
        pygame.display.flip()
        
        # 控制帧率
        clock.tick(60)

if __name__ == "__main__":
    main()