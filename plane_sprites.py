#coding=utf8
import random
import pygame

# 屏幕大小的 常量
SCREEN_RECT = pygame.Rect(0, 0, 480, 700)

# 刷新的帧数
FRAME_PER_SECOND = 60

# 创建敌机的定时器常量
CREATE_ENEMY_EVENT = pygame.USEREVENT

# 英雄发射子弹事件
HERO_FIRE_EVENT = pygame.USEREVENT + 1

# 创建开火敌机的定时常量
CREATE_FIRING_ENEMY_EVENT = pygame.USEREVENT + 2

# 创建开火敌机开火的定时常量
CREATE_ENEMY_FIRE_EVENT = pygame.USEREVENT + 3

# BOOS出现
BOOS_EVENT = pygame.USEREVENT + 4

# 开火
BOSS_FIRING_EVENT = pygame.USEREVENT + 5


class GameSprite(pygame.sprite.Sprite):
    """飞机大战游戏精灵"""

    def __init__(self, image_path, speed=1):
        # 调用父类的初始化方法
        super().__init__()

        # 定义游戏精灵的三个属性 图像、位置、速度
        self.image = pygame.image.load(image_path)
        # rect名不能改，否则在其他模块中访问不到该属性
        self.rect = self.image.get_rect()
        self.speed = speed

    def update(self, *args):
        # 在屏幕垂直方向上移动
        self.rect.y += self.speed


class Background(GameSprite):
    """游戏背景精灵"""

    def __init__(self, is_alt=False):
        # 1. 调用父类方法实现精灵的创建
        super().__init__("./images/backGround.png", speed=1)

        # 2. 判断是否是交替图像，如果是，需要设置初始设置
        if is_alt:
            self.rect.y = -SCREEN_RECT.height

    def update(self, *args):
        # 1.调用父类方法的实现
        super().update()

        # 2.判断是否移除屏幕，如果移除屏幕，将图像设置到屏幕上方
        if self.rect.y >= SCREEN_RECT.height:
            self.rect.y = -self.rect.height


class Enemy(GameSprite):
    """敌机精灵"""

    def __init__(self):
        # 1. 调用父类方法，创建敌机精灵，同时指定敌机图片
        super().__init__("./images/enemy4.png")

        # 2. 指定敌机的初始随机速度
        self.speed = random.randint(3, 5)

        # 3. 指定敌机的初始随机位置
        self.rect.bottom = 0  # 如果不设置底部位置，敌机出现的很突兀
        self.rect.x = random.randint(0, SCREEN_RECT.width - self.rect.width)

        # 4. 敌机要移动
        self.move = random.randint(-1, 1)

    def update(self, *args):
        # 1. 调用父类方法，保持垂直方向的飞行
        super().update()
        self.rect.x += self.move
        # 2. 判断是否飞出屏幕，如果是，需要从精灵组删除敌机
        # 如果敌人移动到屏幕两边将会回来继续殴打英雄
        if self.rect.left < SCREEN_RECT.left or self.rect.right > SCREEN_RECT.right:
            self.move = - self.move
        elif self.rect.y >= SCREEN_RECT.height:
            self.kill()

    # def __del__(self):
    #     # print("敌机被销毁 %s " % self.rect)
    #     pass


class Hero(GameSprite):
    """英雄精灵"""

    def __init__(self):
        # 1. 调用父类方法，设置图片和速度
        super().__init__("./images/Hero.png", speed=0)

        # 2. 设置英雄的初始位置
        self.rect.centerx = SCREEN_RECT.centerx  # rect的centerx属性代表着rect对象的x轴中心
        self.rect.bottom = SCREEN_RECT.bottom - 100

        # 定义发射子弹
        self.bullet = 0
        self.bullet_group = pygame.sprite.Group()

    def update(self, *args):
        # 英雄不能离开屏幕
        if self.rect.left < SCREEN_RECT.left:
            self.rect.left = SCREEN_RECT.left
        elif self.rect.right > SCREEN_RECT.right:
            self.rect.right = SCREEN_RECT.right
        elif self.rect.top < SCREEN_RECT.top:
            self.rect.top = SCREEN_RECT.top
        elif self.rect.bottom > SCREEN_RECT.bottom:
            self.rect.bottom = SCREEN_RECT.bottom

    def left_to_right(self, go_left=True):
        self.speed = 10
        self.rect.x += self.speed if go_left else -self.speed

    def up_to_down(self, go_up=True):
        self.speed = 10
        self.rect.y -= self.speed if go_up else -self.speed

    def fire(self):
        # for i in (0, 1, 2):
        self.bullet = Bullet(image_path="./images/bullet2.png",
                             speed=-20,
                             top=self.rect.top - 30,
                             centerx=self.rect.centerx - 3)
        self.bullet_group.add(self.bullet)

        # print("发射子弹...")

    def stop(self):
        self.speed = 0
        pass


class Bullet(GameSprite):
    # 子弹从英雄头部飞出, 在这里我定义了一个参数，直接在子弹生成时
    def __init__(self, image_path, speed, top, centerx):
        super().__init__(image_path=image_path, speed=speed)
        self.rect.top = top
        self.rect.centerx = centerx

    def update(self, *args):
        # 调用父类方法，让子弹沿垂直方法飞行
        super().update()

        # 销毁子弹 为了让英雄和敌机的子弹都能够正常摧毁 设置两个判断
        if self.rect.bottom < SCREEN_RECT.top or self.rect.top > SCREEN_RECT.bottom:
            self.kill()

    # def __del__(self):
    #     print("子弹没了")


class FiringEnemy(Enemy):
    """能发射子弹的敌机！"""

    # 发射子弹的敌机的出场逻辑与父类完全一致，因此只要添加子弹功能，并且要在生成子弹时注意数量
    def __init__(self):
        # 出场逻辑不变
        super().__init__()

        # 添加子弹
        self.bullet = 0
        self.bullet_group = pygame.sprite.Group()

    # def update(self, *args): # 敌机运动逻辑不变

    def fire(self):
        """敌机开火方法"""
        # 创建子弹对象 - 只在方法中生成
        bullet = Bullet(image_path="./images/enmeybullet.png",
                        speed=10,
                        top=self.rect.bottom,
                        centerx=self.rect.centerx)

        # 添加到子弹组
        self.bullet_group.add(bullet)


# ---------------以下功能自己添加————————————————————————

# 完全不能显示分数，因为一定要先更新背景图片，再更细其他！
class ScoreBoard(pygame.sprite.Sprite):
    """记录玩家分数的UI ， 这里的代码参考了example的alien"""

    def __init__(self):
        """设置一些文字属性"""
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 30)
        self.font.set_bold(True)  # 字体是否加粗
        self.color = pygame.color.Color(2, 43, 53)
        # 记录玩家的分数
        self.PLAYER_SCORE = 0
        self.update()
        self.rect = self.image.get_rect().move(380, 0)

    def update(self):
        """调用font对象的render方法，更新文字"""
        self.image = self.font.render("Score:" + str(self.PLAYER_SCORE), True, self.color)

    def player_scored(self):
        self.PLAYER_SCORE += 1


class WinFlag(ScoreBoard):
    instance = None

    the_first = True

    def __init__(self):
        if not WinFlag.the_first:
            return
        super(WinFlag, self).__init__()
        self.font = pygame.font.Font(None, 70)
        self.color = pygame.color.Color("red")
        self.rect = self.image.get_rect().move(120, 250)
        WinFlag.the_first = False

    def update(self):
        self.image = self.font.render("YOU WIN!", True, self.color)

    def __new__(cls, *args, **kwargs):
        if WinFlag.instance is None:
            WinFlag.instance = super().__new__(cls)
            return WinFlag.instance
        return WinFlag.instance


class Boss(GameSprite):
    instance = None
    is_first = True

    def __new__(cls, *args, **kwargs):
        if Boss.instance is None:
            Boss.instance = GameSprite.__new__(cls)
            return Boss.instance

        return Boss.instance

    def __init__(self, hp):

        if not Boss.is_first:
            return

        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("./images/Boss.png")  # Boss图片实在是太不认真了...
        self.speed = 2
        self.hp = hp

        # 保证生成Boos Rect
        self.rect = self.image.get_rect()
        self.rect.bottom = 0  # Boos缓缓从上面飞出来
        self.rect.centerx = SCREEN_RECT.centerx

        # Boos子弹精灵组
        self.bullet_group = pygame.sprite.Group()

        # 保证初始化
        Boss.is_first = False

        print("boss登场")

    def update(self, *args):
        # Boss不能飞下来，只能在上面，因此将y值定死
        if self.rect.top >= SCREEN_RECT.top:
            self.rect.y = SCREEN_RECT.top
            # Boss水平移动 - 来回移动
            self.rect.x += self.speed
            if self.rect.left == SCREEN_RECT.left or self.rect.right == SCREEN_RECT.right:
                self.speed = - self.speed

        # Boss 出场
        self.rect.y += 1

    def fire(self):
        """boss开火方法，个人感觉Boos的子弹应该有很多种..."""
        # print("我开火！")
        bullet = Bullet(image_path="./images/enmeybullet.png",
                        speed=10,
                        top=self.rect.bottom,
                        centerx=self.rect.centerx)

        # 添加到子弹组
        self.bullet_group.add(bullet)

    def defeated(self):
        self.bullet_group.empty()
        self.kill()
