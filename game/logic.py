# -*- coding: utf-8 -*-
from typing import List

from sprites import Shop, Marlin
import math
import random
from sprites import Boat, Fisherman, Hook, Marlin, Shark
from sprites import Shop ,SharkState ,HookState
class GameLogic:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.score = 0 # 游戏得分 total_marlin_weight and sharks_defeated are also scores
        self.current_marlin_weight = 0
        self.sharks_defeated = 0
        self.is_caught_marlin = False
        self.attacking_shark = None
        self.shop = Shop()
        self.fisherman = None # 渔夫对象
        self.sounds = None
    
    def set_fisherman(self, fisherman):
        self.fisherman = fisherman
    def set_sounds(self, sounds):
        self.sounds = sounds    
    def update_hook(self, hook: Hook, fisherman: Fisherman, marlins: List[Marlin], sharks: List[Shark]):
        if hook.state == HookState.IDLE:
            hook.x = fisherman.x + 16
            hook.y = fisherman.y + 16

        elif hook.state == HookState.EXTENDING:
            # 检测是否钓到马林鱼
            for marlin in marlins:
                if not marlin.being_caught and hook.rect.colliderect(marlin.rect):
                    hook.caught_fish = marlin
                    marlin.being_caught = True  # 设置马林鱼为被钓到状态
                    hook.state = HookState.RETRACTING
                    self.update_shark_behavior(sharks, hook, fisherman, marlins)
                    break

            hook.length = min(hook.length + hook.extension_speed, hook.max_length)
            if hook.length >= hook.max_length:
                hook.state = HookState.RETRACTING

        elif hook.state == HookState.RETRACTING:
            if hook.caught_fish:
                # 始终更新鱼的位置，无论是否有攻击中的鲨鱼
                retraction_speed = (hook.retraction_speed * fisherman.fishing_speed) / (hook.caught_fish.weight / 100)
                hook.length = max(0, hook.length - retraction_speed)

                angle_rad = math.radians(hook.angle)
                hook.caught_fish.x = fisherman.x + 16 + math.cos(angle_rad) * hook.length
                hook.caught_fish.y = fisherman.y + 16 + math.sin(angle_rad) * hook.length
                hook.caught_fish.rect.topleft = (int(hook.caught_fish.x), int(hook.caught_fish.y))

                if hook.length <= 0:
                    hook.state = HookState.IDLE
                    if isinstance(hook.caught_fish, Marlin):
                        self.handle_caught_marlin(hook.caught_fish, fisherman)
                    hook.caught_fish.being_caught = False
                    hook.caught_fish = None
            else:
                hook.length = max(0, hook.length - 7 * fisherman.fishing_speed)
                if hook.length <= 0:
                    hook.state = HookState.IDLE

        # 更新钩子位置
        angle_rad = math.radians(hook.angle)
        hook.x = fisherman.x + 16 + math.cos(angle_rad) * hook.length
        hook.y = fisherman.y + 16 + math.sin(angle_rad) * hook.length
        hook.rect.topleft = (int(hook.x), int(hook.y))
        
    def update_shark_behavior(self, sharks: List[Shark], hook: Hook, fisherman: Fisherman, marlins: List[Marlin]):
        if hook.caught_fish:
            # 当钓到鱼时，找到最近的鲨鱼
            self.attacking_shark = self.find_nearest_shark_to_attack(sharks, hook.caught_fish.x, hook.caught_fish.y)
            if self.attacking_shark:
                # 根据鲨鱼状态处理不同行为
                if self.attacking_shark.state == SharkState.PATROLLING:
                    # 发现猎物,切换到追逐状态
                    self.attacking_shark.state = SharkState.CHASING
                    self.attacking_shark.target = hook.caught_fish
                
                elif self.attacking_shark.state == SharkState.CHASING:
                    # 计算到猎物的距离和方向
                    dx = hook.caught_fish.x - self.attacking_shark.x
                    dy = hook.caught_fish.y - self.attacking_shark.y
                    dist = math.hypot(dx, dy)
                    
                    if dist > 0:
                        # 更新速度向量,使其朝向猎物游动
                        speed = 3.0 if self.attacking_shark.vitality > 50 else 2.0
                        self.attacking_shark.speed = [dx / dist * speed, dy / dist * speed]
                        
                    # 当接近猎物时切换到攻击状态
                    if dist < 30:
                        self.attacking_shark.state = SharkState.ATTACKING
                        
                elif self.attacking_shark.state == SharkState.ATTACKING:
                    # 攻击状态下检查自身血量
                    if self.attacking_shark.vitality <= 50:
                        # 血量低于50%时进入撤退状态
                        self.attacking_shark.state = SharkState.RETREATING
                    else:
                        # 继续攻击
                        self.handle_shark_attack(self.attacking_shark, hook.caught_fish, fisherman)
                        
                elif self.attacking_shark.state == SharkState.RETREATING:
                    # 撤退状态 - 远离战斗区域
                    dx = self.attacking_shark.x - hook.caught_fish.x
                    dy = self.attacking_shark.y - hook.caught_fish.y
                    dist = math.hypot(dx, dy)
                    
                    if dist > 0:
                        # 加快撤退速度
                        speed = 4.0
                        self.attacking_shark.speed = [dx / dist * speed, dy / dist * speed]
                        
                    # 当远离足够距离后进入恢复状态
                    if dist > 200:
                        self.attacking_shark.state = SharkState.RECOVERING
                        
                elif self.attacking_shark.state == SharkState.RECOVERING:
                    # 恢复状态 - 缓慢恢复生命值
                    self.attacking_shark.vitality = min(150, self.attacking_shark.vitality + 0.5)
                    # 生命值恢复到75%后重新开始巡逻
                    if self.attacking_shark.vitality >= 112:
                        self.attacking_shark.state = SharkState.PATROLLING
                        self.attacking_shark.target = None
                        
            # 更新鲨鱼位置
            self.attacking_shark.x = max(0, min(self.attacking_shark.x + self.attacking_shark.speed[0], 
                                            self.screen_width - self.attacking_shark.rect.width))
            self.attacking_shark.y = max(0, min(self.attacking_shark.y + self.attacking_shark.speed[1], 
                                            self.screen_height - self.attacking_shark.rect.height))
            self.attacking_shark.rect.topleft = (int(self.attacking_shark.x), int(self.attacking_shark.y))
        else:
            # 当目标鱼被钓走后，让鲨鱼回到巡逻状态
            if self.attacking_shark:  # 添加这个检查
                if self.attacking_shark.state != SharkState.PATROLLING:
                    # 如果不在巡逻状态，给一个随机方向
                    angle = random.uniform(0, 2 * math.pi)
                    self.attacking_shark.speed = [
                        math.cos(angle) * 2,
                        math.sin(angle) * 2
                    ]
                    self.attacking_shark.state = SharkState.PATROLLING
                    self.attacking_shark.target = None
                    
                # 更新位置（和巡逻状态的鲨鱼一样移动）
                self.attacking_shark.x += self.attacking_shark.speed[0]
                self.attacking_shark.y += self.attacking_shark.speed[1]
                
                # 屏幕边界检查
                self.attacking_shark.x = max(0, min(self.attacking_shark.x, 
                                                self.screen_width - self.attacking_shark.rect.width))
                self.attacking_shark.y = max(0, min(self.attacking_shark.y, 
                                                self.screen_height - self.attacking_shark.rect.height))
                self.attacking_shark.rect.topleft = (int(self.attacking_shark.x), 
                                                int(self.attacking_shark.y))


                    
        # 让所有处于巡逻状态的鲨鱼自由移动
        for shark in sharks:
            if shark.state == SharkState.PATROLLING:
                # 随机改变方向（2%概率）
                if random.random() < 0.02:
                    angle = random.uniform(0, 2 * math.pi)
                    shark.speed[0] = math.cos(angle) * 2  # 增加速度到2
                    shark.speed[1] = math.sin(angle) * 2
                    
                # 移动鲨鱼
                shark.x += shark.speed[0]
                shark.y += shark.speed[1]
                
                # 屏幕边界检查
                shark.x = max(0, min(shark.x, self.screen_width - shark.rect.width))
                shark.y = max(0, min(shark.y, self.screen_height - shark.rect.height))
                shark.rect.topleft = (int(shark.x), int(shark.y))
                
                # 如果鲨鱼没有速度，给它一个随机初始速度
                if shark.speed[0] == 0 and shark.speed[1] == 0:
                    angle = random.uniform(0, 2 * math.pi)
                    shark.speed[0] = math.cos(angle) * 2
                    shark.speed[1] = math.sin(angle) * 2

    def handle_shark_attack(self, shark: Shark, marlin: Marlin, fisherman: Fisherman):
        if self.attacking_shark and self.attacking_shark.state == SharkState.ATTACKING:
            # 设置攻击状态
            marlin.being_attacked = True
            
            # 计算鲨鱼对马林鱼的伤害
            base_damage = shark.attackPower * 5  # 基础伤害
            vitality_multiplier = 1.0 if shark.vitality > 50 else 0.5  # 生命值影响
            actual_damage = base_damage * vitality_multiplier
            
            # 暴击机制 (5%概率)
            if random.random() < 0.05:
                actual_damage *= 1.5
                
            # 限制每次伤害不超过马林鱼当前重量的10%
            max_damage = marlin.weight * 0.1
            actual_damage = min(actual_damage, max_damage)
            
            # 对马林鱼造成伤害并更新重量
            marlin.weight = max(0, marlin.weight - actual_damage)
        
            # 对马林鱼造成伤害
            marlin.weight -= actual_damage
            if self.sounds:
                self.sounds["attack"].play()
                
            if marlin.weight <= 0:
                shark.foodCapacity += marlin.initial_weight * 0.2  # 鲨鱼获得食物
                shark.is_attacking = False
                shark.state = SharkState.PATROLLING
                return True  # 马林鱼被吃掉
                    
        return False

    def find_nearest_shark_to_attack(self, sharks: List[Shark], x, y) -> Shark:
        nearest_shark = None
        min_dist = float("inf")
        for shark in sharks:
            dist = math.hypot(shark.x - x, shark.y - y)
            if dist < min_dist:
                min_dist = dist
                nearest_shark = shark
        return nearest_shark
    
    def update_javelin(self, current_time):
        """更新标枪状态"""
        if self.fisherman.javelin.active:
            # 更新标枪位置
            if self.fisherman.javelin.update(self.screen_width, self.screen_height):
                self.fisherman.javelin.reset_position(self.fisherman)
                
            # 检查是否击中鲨鱼
            if (self.attacking_shark and 
                self.fisherman.javelin.rect.colliderect(self.attacking_shark.rect)):
                # 计算伤害
                damage = (self.fisherman.javelin.attack_power * 
                        self.fisherman.attack_power)
                if random.random() < 0.1:  # 10%暴击率
                    damage *= 2
                    
                self.attacking_shark.vitality -= damage
                self.fisherman.javelin.reset_position(self.fisherman)
                
                # 检查鲨鱼状态
                if self.attacking_shark.vitality <= 0:
                    self.sharks_defeated += 1
                    self.score += 100
                    self.attacking_shark = None
                elif self.attacking_shark.vitality <= 50:
                    self.attacking_shark.state = SharkState.RETREATING

    def auto_attack(self, current_time):
        """自动攻击最近的鲨鱼"""
        if (self.attacking_shark and 
            self.attacking_shark.state == SharkState.ATTACKING and
            not self.fisherman.javelin.active and
            self.fisherman.can_attack(current_time)):
            
            # 发射标枪
            self.fisherman.javelin.auto_aim(
                (self.fisherman.x + 24, self.fisherman.y + 24),
                self.attacking_shark
            )
            # 设置冷却时间
            self.fisherman.javelin_cooldown = current_time + self.fisherman.JAVELIN_COOLDOWN_TIME
            
    def handle_caught_marlin(self, marlin, fisherman):
        self.current_marlin_weight += marlin.weight  # 累加重量
        self.score += marlin.weight
        if self.sounds:
            self.sounds["cheers"].play()
        
    def sell_marlin(self, fisherman):
        if self.current_marlin_weight > 0:
            # 根据商店当前价格系数计算卖价
            price = self.shop.fish_price_multiplier * self.current_marlin_weight * 2
            money_earned = int(price)
            fisherman.money += money_earned
            # 卖出后清零当前马林鱼重量
            self.current_marlin_weight = 0
            return money_earned
        return 0