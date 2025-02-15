import pygame
import os
from moviepy.editor import VideoFileClip
import numpy as np

class VideoPlayer:
    def __init__(self, screen):
        """
        初始化视频播放器
        
        Args:
            screen: pygame的屏幕对象
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
    def play_video(self, video_path):
        """
        播放视频文件
        
        Args:
            video_path: 视频文件的路径
        """
        if not os.path.exists(video_path):
            print(f"Error: Video file not found at {video_path}")
            return False
            
        try:
            # 加载视频
            video = VideoFileClip(video_path)
            
            # 计算视频缩放比例以适应屏幕
            video_ratio = video.w / video.h
            screen_ratio = self.screen_width / self.screen_height
            
            if screen_ratio > video_ratio:
                # 屏幕更宽，以高度为基准
                new_height = self.screen_height
                new_width = int(new_height * video_ratio)
            else:
                # 屏幕更高，以宽度为基准
                new_width = self.screen_width
                new_height = int(new_width / video_ratio)
                
            # 调整视频大小
            video = video.resize((new_width, new_height))
            
            # 计算视频在屏幕上的位置（居中显示）
            x_offset = (self.screen_width - new_width) // 2
            y_offset = (self.screen_height - new_height) // 2
            
            # 播放视频
            for frame in video.iter_frames():
                # 检查退出事件
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        video.close()
                        return False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                            video.close()
                            return True
                
                # 转换帧为pygame surface
                frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                
                # 清空屏幕
                self.screen.fill((0, 0, 0))
                
                # 绘制帧
                self.screen.blit(frame_surface, (x_offset, y_offset))
                pygame.display.flip()
                
                # 控制帧率
                pygame.time.wait(int(1000/video.fps))
            
            video.close()
            return True
            
        except Exception as e:
            print(f"Error playing video: {str(e)}")
            return False