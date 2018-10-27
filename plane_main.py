# lu 2018/7/26
# 飞机大战2.0版本
# 新增了敌机的水平移动
# 新增了会开火的敌机
# 飞机大战3.0版本：
# 1. 增加了英雄飞机的垂直移动
# 2. 准备增加分数的功能
# 3. 根据玩家玩的时间来确定敌机数量
# 4. BOSS战
from plane_sprites import *
import time

class PlaneGame(object):
    """主游戏"""

    def start_game(self):
        """所有游戏都可以使用这个框架 只要修改内部的方法"""
        # print("游戏开始")
        while True:
            # 1.设置刷新帧率
            self.colck.tick(FRAME_PER_SECOND)

            # MY:设置定时器，跟踪玩家的进程
            self.__timer()

            # 2.事件监听
            self.__event_handle()

            # 3.碰撞检测
            self.__check_collide()

            # 4.更新/绘制精灵组
            self.__update_sprites()

            # 5.更新显示
            pygame.display.update()

    def __init__(self):
        # 用于判断死不死的列表
        self.game_over = []

        self.damage = []

        # print("游戏初始化")
        # 1. 创建游戏窗口
        # 如果要设置固定的数值，就不能把数值写死
        self.screen = pygame.display.set_mode(SCREEN_RECT.size)

        # 2. 创建游戏时钟
        self.colck = pygame.time.Clock()

        # 3. 调用私有方法，完成精灵和精灵组的创建
        self.__create_sprites()

        # MY:设置时间变量 跟踪玩家进程
        self.start_time = time.time()

    def __create_sprites(self):
        """创建精灵"""

        # 创建背景精灵和精灵组
        background = Background()
        background2 = Background(is_alt=True)
        # 计分板对象
        self.score_board = ScoreBoard()
        self.ui_group = pygame.sprite.Group(background, background2, self.score_board)
        # 此时不在初始化内部，这个属性还是实例属性么？

        # 创建敌机精灵组 和 开火敌机
        self.enemies_group = pygame.sprite.Group()
        self.firing_enemies_group = pygame.sprite.Group()

        # 创建英雄精灵
        self.hero = Hero()  # 为了用于检测，将英雄定义为属性
        self.hero_group = pygame.sprite.Group(self.hero)

        # Boss精灵组
        self.boss_group = pygame.sprite.Group()
        self.boss = None

        # # 用于所有物体的更新. 如果将所有精灵加进来，暂时无法改善
        # self.all_enemies = pygame.sprite.Group()

    def __event_handle(self):
        """事件监听[玩家事件，游戏事件]"""
        # 玩家事件列表
        # 使用键盘提供的方法获取键盘的按键 - 按键元组
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:  # 这里应用了元组的索引，那么这个索引是怎样进行的？（这个元组中的数据是？）
            self.hero.left_to_right()
        elif key_pressed[pygame.K_LEFT]:
            self.hero.left_to_right(False)
        elif key_pressed[pygame.K_UP]:
            self.hero.up_to_down()
        elif key_pressed[pygame.K_DOWN]:
            self.hero.up_to_down(False)
        else:  # 这里的else还包括了不按任何按键的时候！，如果去掉的话飞机会一直飞一直飞
            self.hero.stop()

        # 游戏事件列表
        for event in pygame.event.get():
            # 判断是否退出
            if event.type == pygame.QUIT:
                PlaneGame.__game_over()

            elif event.type == CREATE_ENEMY_EVENT:
                # 创建敌机精灵
                enemy = Enemy()
                # 添加到敌机精灵组
                self.enemies_group.add(enemy)

            elif event.type == CREATE_FIRING_ENEMY_EVENT:
                # print("敌人来了")
                # 创建开火敌机
                firing_enemy = FiringEnemy()
                # 添加到敌机精灵组
                self.firing_enemies_group.add(firing_enemy)
            elif event.type == CREATE_ENEMY_FIRE_EVENT:
                # print("发射！！")
                for firing_enemy in self.firing_enemies_group:
                    firing_enemy.fire()
                    # print("发射子弹")

            elif event.type == BOOS_EVENT:
                self.boss = Boss(100)  # 该boss100血量， 以后可以根据事件来确定boss血量
                self.boss_group.add(self.boss)
            elif event.type == BOSS_FIRING_EVENT:
                # 创建boos实例，调用boss打架方法
                self.boss.fire()

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.hero.fire()

    def __check_collide(self):
        """检测碰撞"""
        # 1. 子弹与敌机的碰撞
        if pygame.sprite.groupcollide(self.hero.bullet_group, self.enemies_group, True, True) or \
                pygame.sprite.groupcollide(self.hero.bullet_group, self.firing_enemies_group, True, True):
            # 更新玩家分数
            self.score_board.player_scored()

        # 2. 英雄与敌机的碰撞
        self.game_over.extend(pygame.sprite.spritecollide(self.hero, self.enemies_group, True))
        self.game_over.extend(pygame.sprite.spritecollide(self.hero, self.firing_enemies_group, True))
        # 英雄与敌机子弹碰撞
        for firing_enemy in self.firing_enemies_group:
            self.game_over.extend(pygame.sprite.spritecollide(self.hero, firing_enemy.bullet_group, True))

        # MY: Boos战..
        if self.boss is not None:
            # Boss子弹也有伤害..
            self.game_over.extend(pygame.sprite.spritecollide(self.hero, self.boss.bullet_group, True))
            # 子弹打到Boss扣血..
            if len(self.damage) != self.boss.hp:
                self.damage.extend(pygame.sprite.groupcollide(self.hero.bullet_group, self.boss_group, True, True))
            else:
                # 游戏胜利！！！
                winning_flag = WinFlag()
                self.ui_group.add(winning_flag)
                self.enemies_group.empty()
                self.firing_enemies_group.empty()
                self.boss.defeated()

        # 3. 判断列表长度
        if len(self.game_over) > 0:
            # 让英雄牺牲
            self.hero.kill()
            # 游戏结束
            PlaneGame.__game_over()

    def __update_sprites(self):
        """更新精灵组"""

        self.ui_group.update()
        self.ui_group.draw(self.screen)

        self.enemies_group.update()
        self.enemies_group.draw(self.screen)

        self.hero_group.update()
        self.hero_group.draw(self.screen)

        self.hero.bullet_group.update()
        self.hero.bullet_group.draw(self.screen)

        self.firing_enemies_group.update()
        self.firing_enemies_group.draw(self.screen)

        for firing_enemy in self.firing_enemies_group:
            firing_enemy.bullet_group.update()
            firing_enemy.bullet_group.draw(self.screen)

        if self.boss is not None:
            self.boss_group.update()
            self.boss_group.draw(self.screen)
            self.boss.bullet_group.update()
            self.boss.bullet_group.draw(self.screen)

    @staticmethod
    def __game_over():
        """游戏结束，静态方法"""
        print("英雄牺牲，游戏结束")
        pygame.quit()
        exit()

    # --------------一下功能自己开发-----------------------
    def __timer(self):
        # 按照MVC的思路，这个功能应该不属于这里，但是无所谓了...
        # 根据玩家表现来设置敌人数量，三个值分别表示
        # 1. 生成敌人频率
        # 2. 生成开火敌人频率
        # 3. 开火敌人开火频率
        current_time = time.time()
        if int(current_time - self.start_time) == 1:
            pygame.time.set_timer(CREATE_ENEMY_EVENT, 2000)
            pygame.time.set_timer(CREATE_FIRING_ENEMY_EVENT, 3000)
            pygame.time.set_timer(CREATE_ENEMY_FIRE_EVENT, 1000)
        elif int(current_time - self.start_time) == 30:
            pygame.time.set_timer(CREATE_ENEMY_EVENT, 1500)
            pygame.time.set_timer(CREATE_FIRING_ENEMY_EVENT, 2500)
            pygame.time.set_timer(CREATE_ENEMY_FIRE_EVENT, 900)
        elif int(current_time - self.start_time) == 60:
            pygame.time.set_timer(CREATE_ENEMY_EVENT, 1000)
            pygame.time.set_timer(CREATE_FIRING_ENEMY_EVENT, 2000)
            pygame.time.set_timer(CREATE_ENEMY_FIRE_EVENT, 1000)
        elif int(current_time - self.start_time) == 80:
            pygame.time.set_timer(CREATE_ENEMY_EVENT, 800)
            pygame.time.set_timer(CREATE_FIRING_ENEMY_EVENT, 1000)
            pygame.time.set_timer(CREATE_ENEMY_FIRE_EVENT, 1000)
        elif int(current_time - self.start_time) == 100:
            # BOSS出场，杂兵伴其左右
            pygame.time.set_timer(CREATE_ENEMY_EVENT, 0)
            pygame.time.set_timer(CREATE_FIRING_ENEMY_EVENT, 1500)
            pygame.time.set_timer(CREATE_ENEMY_FIRE_EVENT, 1000)
            # TODO:Boss的事件只能生成一次，目前我只能使用单例来创建Boss... 无形中增加了CPU的消耗
            pygame.time.set_timer(BOOS_EVENT, 100)
            pygame.time.set_timer(BOSS_FIRING_EVENT, 1200)
        else:
            pass


if __name__ == '__main__':
    pygame.init()
    # 创建游戏对象（只能在本文件中使用）
    # pygame.mixer.get_init()
    # pygame.mixer.music.load("./Virtual Riot - Energy Drink.mp3")
    # pygame.mixer.music.play(-1)
    game = PlaneGame()
    # 启动游戏循环
    game.start_game()
