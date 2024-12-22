import pygame
import sys
import math
from game_entities import GameState, GameConfig
from game_manager import GameManager
from scene_manager import SceneManager  # 新增

def main():
    pygame.init()
    screen = pygame.display.set_mode((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
    pygame.display.set_caption("老人与海")
    clock = pygame.time.Clock()

    # 创建GameManager和SceneManager
    game_manager = GameManager(GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT)
    scene_manager = SceneManager(game_manager)

    running = True
    debug_mode = False

    # 调试网格函数
    def draw_grid(surface, cell_size=50):
        for x in range(0, GameConfig.SCREEN_WIDTH, cell_size):
            pygame.draw.line(surface, (100, 100, 100), (x, 0), (x, GameConfig.SCREEN_HEIGHT))
        for y in range(0, GameConfig.SCREEN_HEIGHT, cell_size):
            pygame.draw.line(surface, (100, 100, 100), (0, y), (GameConfig.SCREEN_WIDTH, y))

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F3:
                    debug_mode = not debug_mode

        # 交给SceneManager进行场景切换更新
        if not scene_manager.update(events):
            running = False
        
        # 获取键盘输入并处理
        keys = pygame.key.get_pressed()
        scene_manager.handle_input(keys)

        # 渲染场景
        screen.fill((0, 105, 148))
        if debug_mode:
            draw_grid(screen)
        scene_manager.render(screen)

        # 额外调试信息
        if debug_mode:
            font = pygame.font.Font(None, 24)
            info_text = [
                f"FPS: {int(clock.get_fps())}",
                f"Game State: {game_manager.state.value}",
                f"Fisherman pos: {game_manager.fisherman.position}",
                f"Boat pos: {game_manager.boat.position}",
                f"Marlin pos: {game_manager.marlin.position}",
                f"Sharks: {len(game_manager.sharks)}"
            ]
            for i, line in enumerate(info_text):
                text_surf = font.render(line, True, (255, 255, 255))
                screen.blit(text_surf, (10, 10 + i * 20))

        pygame.display.flip()
        clock.tick(GameConfig.FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()