import pygame
import random

pygame.init()

clock = pygame.time.Clock()

# Main variables
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600

# BG animation
bg_sprites = []
for i in range(18):
    if i < 10:
        bg = pygame.image.load(f"assets/img/BG/0{i}_bg.png")
    else:
        bg = pygame.image.load(f"assets/img/BG/{i}_bg.png")
    bg_sized = pygame.transform.scale(bg, (500, 600))
    bg_sprites.append(bg_sized)
bg_current = 0
bg_image = bg_sprites[bg_current]

# Main Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Warrior")

# Text
text_seconds = 30 * 4
text_timer = text_seconds

# End text Timer
end_text_timer = text_seconds

font = pygame.font.Font("assets/fonts/font.otf", 40)
main_text = font.render("Space Warrior", True, (255, 255, 255))
text_rect = main_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

# Sounds
gameplay_music = pygame.mixer.Sound("assets/sound/gameplay_music.mp3")
wave_sound = pygame.mixer.Sound("assets/sound/wave.mp3")
destroy_sound = pygame.mixer.Sound("assets/sound/destroy.mp3")
boss_music = pygame.mixer.Sound("assets/sound/boss_music.mp3")
final_wave_sound = pygame.mixer.Sound("assets/sound/final_wave.mp3")
game_win_sound = pygame.mixer.Sound("assets/sound/game_win.mp3")
player_death_sound = pygame.mixer.Sound("assets/sound/player_death.mp3")
gameover_sound = pygame.mixer.Sound("assets/sound/gameover.mp3")
shield_break_sound = pygame.mixer.Sound("assets/sound/shield_off.mp3")

# lists
powers = []
bullets = []

# Powers Spawners Timers
double_shoot_timer = random.randint(10 * 30, 30 * 30)
shield_timer = random.randint(10 * 30, 30 * 30)

#State
state = "title"
current_wave = None

# Gameover sound state
end_sound = False

#intro
intro_timer = 7 * 30
intro_image = pygame.image.load("assets/img/introduction.png")
intro_new_size = pygame.transform.scale(intro_image, (500, 600))

# Lives Image
heart = pygame.image.load("assets/img/Heart.png")


# Game Classes

# Player Class
class Player():
    def __init__(self, pos, size):
        self.size = size
        self.image = pygame.image.load("assets/img/player.png")
        self.new_size = pygame.transform.scale(self.image, size)
        self.rect = self.new_size.get_rect(topleft=pos)
        self.rect.w = size[0] * 0.46875
        self.rect.h = size[1] * 0.421875
        self.shoot_sound = pygame.mixer.Sound("assets/sound/player.mp3")
        self.zone = (400, 50)
        self.lives = 5
        self.speed = 7
        self.bullet_seconds = 12
        self.bullet_timer = 0

        #   Double shoot
        self.double_shoot_state = False
        self.double_shoot_seconds = 10 * 30
        self.double_shoot_timer = self.double_shoot_seconds

        # Engine Animation
        self.engine_sprites = []
        for i in range(8):
            sprite = pygame.image.load(f"assets/img/Player_engine/0{i}_player_engine.png")
            sprite = pygame.transform.scale(sprite, size)
            self.engine_sprites.append(sprite)

        self.engine_current_sprite = 0
        self.engine_image = self.engine_sprites[self.engine_current_sprite]

        # Shield Animation
        self.shield_sprites = []
        for i in range(20):
            if i < 10:
                sprite = pygame.image.load(f"assets/img/Player_shield/0{i}_player_shield.png")
            else:
                sprite = pygame.image.load(f"assets/img/Player_shield/{i}_player_shield.png")
            sprite = pygame.transform.scale(sprite, size)
            self.shield_sprites.append(sprite)
        self.shield_state = False
        self.shield_current_sprite = 0
        self.shield_image = self.shield_sprites[self.shield_current_sprite]

        # Death Animation
        self.death_sprites = []
        for i in range(18):
            if i < 10:
                sprite = pygame.image.load(f"assets/img/Player_death/0{i}_player_death.png")
            else:
                sprite = pygame.image.load(f"assets/img/Player_death/{i}_player_death.png")
            sprite = pygame.transform.scale(sprite, size)
            self.death_sprites.append(sprite)
        self.death_current_sprite = 0
        self.death_image = self.death_sprites[self.death_current_sprite]
        self.death_sound_state = False
    
    # Main loop for animations and movement
    def main_loop(self, keys):
        screen.blit(self.new_size, (self.rect.x - (self.size[0] - self.rect.w)/2, self.rect.y - (self.size[1] - self.rect.h)/2 - 2))
        
        try:
            if self.shield_state == True:
                screen.blit(self.shield_image, (self.rect.x - (self.size[0] - self.rect.w)/2, self.rect.y - (self.size[1] - self.rect.h)/2 - 2))
                self.shield_current_sprite += 0.2
                if self.shield_current_sprite >= len(self.shield_sprites):
                    self.shield_current_sprite = 0

                self.shield_image = self.shield_sprites[int(self.shield_current_sprite)]
        except:
            pass
        
        screen.blit(self.engine_image, (self.rect.x - (self.size[0] - self.rect.w)/2, self.rect.y - (self.size[1] - self.rect.h)/2 - 2))
        self.engine_current_sprite += 0.2
    
        if self.engine_current_sprite >= len(self.engine_sprites):
            self.engine_current_sprite = 0

        self.engine_image = self.engine_sprites[int(self.engine_current_sprite)]

        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.rect.x + 5 <= self.zone[0]:
            self.rect.x += self.speed
        elif (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.rect.x - 5 >= self.zone[1]:
            self.rect.x -= self.speed

        if self.double_shoot_timer == 0:
            self.double_shoot_state = False
        else:
            self.double_shoot_timer -= 1

    # Shooting method
    def shooting(self, keys):
        if self.bullet_timer > 0:
            self.bullet_timer -= 1

        if keys[pygame.K_SPACE] and self.bullet_timer == 0:
            if self.double_shoot_state == True:
                for i in range(2):
                    bullet = Bullet(5 + self.rect.x + 15 * i, self.rect.y, speed=-10, shooter="Player")
                    bullets.append(bullet)
            else:
                bullet = Bullet(self.rect.x + 13.5, self.rect.y, speed=-10, shooter="Player")
                bullets.append(bullet)
            self.shoot_sound.play()
            self.bullet_timer = self.bullet_seconds

    # Method to enable Shield
    def enable_shield(self):
        self.shield_state = True

    # Method to enable Double Shoot
    def double_shoot(self):
        self.double_shoot_state = True
        self.double_shoot_timer = self.double_shoot_seconds

    # Player Damaged method
    def damage(self):
        if self.shield_state == False:
            self.lives -= 1
        else:
            self.shield_state = False

    # Check if player dead
    def death_check(self):
        if self.lives == 0:
            global state
            state = "player_death"
            if self.death_sound_state == False:
                pygame.mixer.stop()
                player_death_sound.play()
                self.death_sound_state = True
            screen.blit(self.death_image, (self.rect.x - (self.size[0] - self.rect.w)/2, self.rect.y - (self.size[1] - self.rect.h)/2 - 2))
            self.death_current_sprite += 0.2
        
            if self.death_current_sprite >= len(self.death_sprites):
                return False
            else:
                self.death_image = self.death_sprites[int(self.death_current_sprite)]
        return True

# Player Object
player = Player((225, 450), (80, 80))

# Bullet Class
class Bullet():
    def __init__(self, x, y, speed, shooter):
        self.speed = speed
        self.shooter = shooter

        # Rocket animation if player is the shooter
        if shooter == "Player":
            # Bullet Animation
            self.size = (15, 30)
            self.bullet_sprites = []
            for i in range(4):
                sprite = pygame.image.load(f"assets/img/Player_bullet/0{i}_player_bullet.png")
                sprite = pygame.transform.scale(sprite, self.size)
                self.bullet_sprites.append(sprite)
            self.bullet_current_sprite = 0
            self.bullet_image = self.bullet_sprites[self.bullet_current_sprite]
            self.bullet = self.bullet_image.get_rect(topleft=(x, y))
            self.bullet.w = 0.78 * self.size[0]
            self.bullet.h = 0.625 * self.size[1]
        
        # Normal rect if enemy is the shooter
        else:
            self.bullet = pygame.Rect(x, y , 4, 13)
            self.color = (255, 87, 51)
    
    # Move bullet
    def move(self):
        if self.shooter == "Player":
            screen.blit(self.bullet_image, (self.bullet.x - (self.size[0] - self.bullet.w)/2, self.bullet.y - (self.size[1] - self.bullet.h)/2 - 2))
            self.bullet_current_sprite += 0.5
            if self.bullet_current_sprite >= len(self.bullet_sprites):
                self.bullet_current_sprite = 0
            self.bullet_image = self.bullet_sprites[int(self.bullet_current_sprite)]
        else:
            pygame.draw.rect(screen, self.color, self.bullet)
        self.bullet.y += self.speed

    # Method for deleting the bullet
    def delete(self):
        del self.bullet
        del self


# Enemy Class
class Enemy():
    def __init__(self, image, pos, size, stop, shoot_speed, shoot_delay, lives, sound):
        self.image = pygame.image.load(f"assets/img/{image}")
        self.new_size = pygame.transform.scale(self.image, size)
        self.rect = self.new_size.get_rect(topleft=pos)
        self.size = size
        self.stop = stop
        self.shoot_speed = shoot_speed
        self.shoot_delay = shoot_delay
        self.shoot_timer = random.randint(self.shoot_delay[0], self.shoot_delay[1])
        self.lives = lives
        self.sound = pygame.mixer.Sound(f"assets/sound/{sound}")
        self.state = 1
        self.direction = -3

        # Engine Animation
        self.engine_sprites = []
        for i in range(8):
            sprite = pygame.image.load(f"assets/img/Enemy_engine/0{i}_enemy_engine.png")
            sprite = pygame.transform.scale(sprite, (size[0]/2, size[1]/2))
            self.engine_sprites.append(sprite)

        self.engine_current_sprite = 0
        self.engine_image = self.engine_sprites[self.engine_current_sprite]

    # Method for movement and main loop
    def move(self):
        if self.rect.x != self.stop and self.state == 1:
            self.rect.x -= 5

        elif self.rect.x == self.stop and self.state == 1:
            self.state += 1

        else:
            if self.rect.x <= self.stop -100:
                self.direction = 3
            elif self.rect.x >= self.stop +100 - self.rect.w:
                self.direction = -3
            self.rect.x += self.direction

        self.shoot()

    # Method for shooting
    def shoot(self):
        if self.shoot_timer == 0:
            bullet = Bullet(self.rect.x + self.size[0]/2, self.rect.y, self.shoot_speed, "Enemy")
            bullets.append(bullet)
            self.sound.play()
            self.shoot_timer = random.randint(self.shoot_delay[0], self.shoot_delay[1])
        else:
            self.shoot_timer -= 1
    
    # Method to delete Enemy
    def delete(self):
        del self.rect
        del self

    # Method to enable engine animation
    def engine_animation(self):
        screen.blit(self.engine_image, (self.rect.x + self.size[0]/4, self.rect.y - self.size[1]/4 - 4))
        self.engine_current_sprite += 0.2
        if self.engine_current_sprite >= len(self.engine_sprites):
            self.engine_current_sprite = 0

        self.engine_image = self.engine_sprites[int(self.engine_current_sprite)]


# Boss Class
class Boss():
    def __init__(self):
        # self.image = pygame.image.load("assets/img/boss.png")
        self.size = (150, 150)
        # Boss Laser states
        self.sprites = []
        for i in range(34):
            if i < 10:
                sprite = pygame.image.load(f"assets/img/Boss_laser/0{i}_boss_laser.png")
            else:
                sprite = pygame.image.load(f"assets/img/Boss_laser/{i}_boss_laser.png")
            sprite = pygame.transform.scale(sprite, self.size)
            self.sprites.append(sprite)
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite] 
          
        # self.new_size = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect()
        self.rect.w = self.rect.w * 0.53125
        self.rect.h = self.rect.h * 0.765625
        self.rect.topleft=(SCREEN_WIDTH / 2 - self.rect.w / 2, -100)
        self.lives = 100
        self.stop = 200
        self.state = 1
        self.speed = 3
        self.direction = -self.speed
        self.gun_sound = pygame.mixer.Sound("assets/sound/enemy1.mp3")
        self.laser_charging_sound = pygame.mixer.Sound("assets/sound/laser_charging.mp3")
        self.laser_charging_sound_timer = 0
        self.laser_sound = pygame.mixer.Sound("assets/sound/laser.mp3")
        self.laser_sound_timer = 0
        self.shoot_timer = random.randint(25, 50)
        self.org_gun_timer = 3 * 30
        self.org_stop_timer = 3 * 30
        self.org_laser_timer = 1.5 * 30
        self.gun_timer = self.org_gun_timer
        self.stop_timer = self.org_stop_timer
        self.laser_timer = self.org_laser_timer
        self.orghealth = pygame.Rect(190, 10, 120, 10)
        self.health = pygame.Rect(190 + 5, 12.5, 110, 5)
        self.enemies = []
        self.enemies_state = 0

        #laser
        self.laser_sprites = []
        for i in range(4):
            sprite = pygame.image.load(f"assets/img/Laser/0{i}_laser.png")
            sprite_new_size = pygame.transform.scale(sprite, (50, 105.5))
            self.laser_sprites.append(sprite_new_size)

        self.current_laser_sprite = 0
        self.laser_image = self.laser_sprites[self.current_laser_sprite]
        self.laser_rect = self.laser_image.get_rect()
        x_offset = self.rect.w / 2 - 25
        y_offset = self.rect.h + self.laser_rect.h / 2
        self.laser_rect.topleft = (self.rect.x + x_offset, self.rect.y + y_offset)
        self.laser_rect.w = 20
        self.laser_rect.h = 650
        self.laser_state = False     

        # Engine Animation
        self.engine_sprites = []
        for i in range(8):
            sprite = pygame.image.load(f"assets/img/Boss_engine/0{i}_boss_engine.png")
            sprite = pygame.transform.scale(sprite, self.size)
            self.engine_sprites.append(sprite)
        self.current_engine_sprite = 0
        self.engine_image = self.engine_sprites[self.current_engine_sprite]

        # Death Animation
        self.death_sprites = []
        for i in range(18):
            if i < 10:
                sprite = pygame.image.load(f"assets/img/Boss_death/0{i}_boss_death.png")
            else:
                sprite = pygame.image.load(f"assets/img/Boss_death/{i}_boss_death.png")
            sprite = pygame.transform.scale(sprite, self.size)
            self.death_sprites.append(sprite)
        self.current_death_sprite = 0
        self.death_image = self.death_sprites[self.current_death_sprite]
        self.death_sound_timer = 0

    # Movement method
    def move(self):
        self.current_engine_sprite += 0.5
        if self.current_engine_sprite >= len(self.engine_sprites):
            self.current_engine_sprite = 0

        self.engine_image = self.engine_sprites[int(self.current_engine_sprite)]

        if self.rect.y != 50 and self.state == 1:
            self.rect.y += 5

        elif self.rect.y == 50 and self.state == 1:
            self.state += 1

        else:
            if self.rect.x <= self.stop -200:
                self.direction = self.speed
            elif self.rect.x >= self.stop +200:
                self.direction = -self.speed
            self.rect.x += self.direction

        try:
            self.move_enemies()
        except:
            pass
    
    # Boss shooting method
    def shoot(self):
        # Shooting Bullets
        if self.gun_timer != 0 and self.stop_timer != 0:
            if self.shoot_timer == 0:
                self.gun_sound.play()
                for i in range(3):
                    bullet_x = self.rect.x + i * self.rect.w / 3 + 5
                    bullet = Bullet(bullet_x, self.rect.y + 25, 16, "Enemy")
                    bullets.append(bullet)
                self.shoot_timer = 15
            else:
                self.shoot_timer -= 1   
            self.current_sprite = 0
            self.image = self.sprites[self.current_sprite]     
            self.gun_timer -= 1

        # Stop for charging
        elif self.gun_timer == 0 and self.stop_timer != 0:
            # charging sound timer
            if self.laser_charging_sound_timer == 0:
                self.laser_charging_sound.play()
                self.laser_charging_sound_timer = 60
            else:
                self.laser_charging_sound_timer -= 1
            
            # Animation
            if self.laser_timer != 0:
                self.current_sprite += 0.2
                if self.current_sprite >= 21:
                    self.current_sprite = 0
            else:
                self.current_sprite = 0
            self.image = self.sprites[int(self.current_sprite)]
            self.stop_timer -= 1

        # Laser time
        elif self.gun_timer == 0 and self.stop_timer == 0 and self.laser_timer != 0:
            self.laser_state = True

            # laser sound timer
            if self.laser_sound_timer == 0:
                self.laser_sound.play()
                self.laser_sound_timer = 30
            else:
                self.laser_sound_timer -= 1

            # Laser Animation
            x_offset = self.rect.x + self.rect.w / 2 - self.laser_rect.w / 2 - 1
            y_offset = self.rect.y + 90
            self.laser_rect.x = x_offset
            self.laser_rect.y = y_offset
            for i in range(7):
                screen.blit(self.laser_image, (self.laser_rect.x - 15, self.laser_rect.y + 100 * i + 20))
            pygame.draw.circle(screen, (249, 180, 45), (self.rect.x + self.rect.w / 2 -1, self.rect.y + 120), 13)

            self.current_laser_sprite += 0.2
            if self.current_laser_sprite >= len(self.laser_sprites):
                self.current_laser_sprite = 0

            self.laser_image = self.laser_sprites[int(self.current_laser_sprite)]
            
            # Boss Animation
            self.current_sprite += 0.2
            if self.current_sprite >= len(self.sprites) or self.current_sprite < 22:
                self.current_sprite = 22
            self.image = self.sprites[int(self.current_sprite)]

            self.laser_timer -= 1
            if self.laser_timer == 0:
                self.laser_state = False
                self.stop_timer = self.org_stop_timer
        
        # Replay
        else:
            self.stop_timer = self.org_stop_timer
            self.gun_timer = self.org_gun_timer
            self.laser_timer = self.org_laser_timer

    # Animation when boss dies method
    def death_animation(self):
        self.current_death_sprite += 0.2
        if self.current_death_sprite >= len(self.death_sprites):
            return True
        else:
            if self.death_sound_timer == 0:
                destroy_sound.play()
                self.death_sound_timer = 15
            else:
                self.death_sound_timer -= 1
            self.image = self.death_sprites[int(self.current_death_sprite)]
            screen.blit(self.image, (self.rect.x - (self.size[0] - self.rect.w)/2, self.rect.y - (self.size[1] - self.rect.h)/2))
            return False

    # Checking if boss is died
    def death_check(self):
        pygame.draw.rect(screen, (27, 49, 61), self.orghealth)
        pygame.draw.rect(screen, (255, 0, 0), self.health)

        # Spawn enemies if boss lives == 50
        if self.lives <= 50 and self.enemies_state == 0:
            self.spawn_enemies()
            self.enemies_state = 1
        for bullet in bullets:
            if self.rect.colliderect(bullet.bullet) and bullet.shooter == "Player":
                destroy_sound.play()
                bullet.delete()
                bullets.pop(bullets.index(bullet))
                self.lives -= 1
                self.health.w -= 1.1
                if self.lives == 0:
                    global state
                    state = "boss_death"
                    pygame.mixer.stop()
    
    # Spawning Enemies
    def spawn_enemies(self):
        for i in range(7):
            enemy = Enemy("enemy1.png", (500 + 50 * i, 180), (25, 25), 100 + 50 * i, 10, (45, 100), 1, "enemy1.mp3")
            self.enemies.append(enemy)

        for i in range(5):
            enemy = Enemy("enemy2.png", (500 + 50 * i, 230), (40, 40), 140 + 50 * i, 14, (20, 40), 2, "enemy1.mp3")
            self.enemies.append(enemy)
    
    # Boss enemies movement
    def move_enemies(self):
        for enemy in self.enemies:
            enemy.engine_animation()
            screen.blit(enemy.new_size, enemy.rect)
            enemy.move()
            for bullet in bullets:
                try:
                    if enemy.rect.colliderect(bullet.bullet) and bullet.shooter == "Player":
                        destroy_sound.play()
                        bullet.delete()
                        bullets.pop(bullets.index(bullet))
                        enemy.lives -= 1
                        if enemy.lives == 0:
                            enemy.delete()
                            self.enemies.pop(self.enemies.index(enemy))
                except:
                    pass

# Wave Class
class Wave():
    def __init__(self, enemies_type, space=50):
        self.space = space
        self.enemies_type = enemies_type
        self.enemies = []

    # Creating enemies Method
    def create_enemies(self):
        current = 0
        for i in range(len(self.enemies_type)):
            for j in range(self.enemies_type[i]["count"]):
                if j % 7 == 0:
                    current = j
                enemy = Enemy(self.enemies_type[i]["image"], (500 + (j-current) * self.space, 50 + i * 50), self.enemies_type[i]["size"], self.enemies_type[i]["stop"] + j * self.space, self.enemies_type[i]["shoot_speed"], self.enemies_type[i]["shoot_delay"], self.enemies_type[i]["lives"], self.enemies_type[i]["sound"])
                self.enemies.append(enemy)

    # Main loop method for movement and death checks
    def main_loop(self):
        for enemy in self.enemies:
            enemy.engine_animation()
            screen.blit(enemy.new_size, enemy.rect)
            enemy.move()
            for bullet in bullets:
                try:
                    if enemy.rect.colliderect(bullet.bullet) and bullet.shooter == "Player":
                        destroy_sound.play()
                        bullet.delete()
                        bullets.pop(bullets.index(bullet))
                        enemy.lives -= 1
                        if enemy.lives == 0:
                            enemy.delete()
                            self.enemies.pop(self.enemies.index(enemy))
                except:
                    pass
    
    # Checking if alla enemies are dead
    def wave_over_check(self):
        if len(self.enemies) == 0:
            return True
        else:
            return False
        

# Waves
waves = [
    Wave([{"image":"enemy1.png", "sound":"enemy1.mp3", "count": 3, "size": (25, 25), "shoot_speed":10, "shoot_delay":(45, 100), "stop":200, "lives":1}]),
    Wave([{"image":"enemy1.png", "sound":"enemy1.mp3", "count": 3, "size": (25, 25), "shoot_speed":10, "shoot_delay":(45, 100), "stop":200, "lives":1}, {"image":"enemy1.png", "sound":"enemy1.mp3", "count": 3, "size": (25, 25), "shoot_speed":10, "shoot_delay":(45, 100), "stop":200, "lives":1}]),
    Wave([{"image":"enemy1.png", "sound":"enemy1.mp3", "count": 7, "size": (25, 25), "shoot_speed":10, "shoot_delay":(45, 100), "stop":100, "lives":1}]),
    Wave([{"image":"enemy2.png", "sound":"enemy2.mp3", "count": 3, "size": (40, 40), "shoot_speed":14, "shoot_delay":(20, 40), "stop":135, "lives":2}], space=100),
    Wave([{"image":"enemy2.png", "sound":"enemy2.mp3", "count": 5, "size": (40, 40), "shoot_speed":14, "shoot_delay":(20, 40), "stop":150, "lives":2}, {"image":"enemy1.png", "sound":"enemy1.mp3", "count": 7, "size": (25, 25), "shoot_speed":10, "shoot_delay":(45, 100), "stop":100, "lives":1}]),
    Wave([{"image":"enemy1.png", "sound":"enemy1.mp3", "count": 7, "size": (25, 25), "shoot_speed":10, "shoot_delay":(35, 90), "stop":100, "lives":1}, {"image":"enemy2.png", "sound":"enemy2.mp3", "count": 5, "size": (40, 40), "shoot_speed":14, "shoot_delay":(20, 40), "stop":150, "lives":2}, {"image":"enemy1.png", "sound":"enemy1.mp3", "count": 7, "size": (25, 25), "shoot_speed":10, "shoot_delay":(35, 90), "stop":100, "lives":1}]),
    Wave([{"image":"enemy3.png", "sound":"enemy1.mp3", "count": 3, "size": (35, 35), "shoot_speed":18, "shoot_delay":(30, 60), "stop":200, "lives":1}, {"image":"enemy1.png", "sound":"enemy1.mp3", "count": 7, "size": (25, 25), "shoot_speed":10, "shoot_delay":(35, 90), "stop":100, "lives":1}, {"image":"enemy1.png", "sound":"enemy1.mp3", "count": 7, "size": (25, 25), "shoot_speed":10, "shoot_delay":(35, 90), "stop":100, "lives":1}]),
]
        
        
# Power Class
class Power():
    def __init__(self, image, func):
        # Power Main variables
        self.image = pygame.image.load(f"assets/img/{image}")
        self.new_size = pygame.transform.scale(self.image, (25, 25))
        self.rect = self.new_size.get_rect(topleft=(random.randint(30, 400), -20))
        self.func = func

    # Move power if and delete if out of screen
    def move(self):
        self.rect.y += 3
        if self.rect.y >= 600:
            return True
    
    # Method to check if there collistion with player
    def player_col(self):
        if self.rect.colliderect(player.rect):
            self.func()
            return True
        
    # Method to delete power
    def delete(self):
        del self.rect
        del self


# Functions

# function for next wave
def next_wave():
    global main_text, text_rect, text_timer, text_seconds, current_wave, state

    # Current wave state check
    if current_wave == None:
        global waves
        current_wave = waves[0]
        state = "loading"
    elif waves.index(current_wave) + 1 < len(waves):
        current_wave = waves[waves.index(current_wave) + 1]
        state = "loading"
    else:
        state = "boss"

    pygame.mixer.stop()

    # Printing wave number on the screen
    if state == "loading":
        wave_sound.play()
        main_text = font.render(f"Wave {waves.index(current_wave) + 1}", True, (136, 8, 8))
        text_rect = main_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        text_timer = text_seconds
    elif state == "boss":
        final_wave_sound.play()
        main_text = font.render(f"Final Wave", True, (136, 8, 8))
        text_rect = main_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        text_timer = text_seconds


# function to play again after loss
def play_again():
    global text_timer, player, double_shoot_timer, shield_timer, current_wave, state, waves, end_sound
    current_wave = None
    pygame.mixer.stop()
    double_shoot_timer = random.randint(15 * 30, 60 * 30)
    shield_timer = random.randint(20 * 30, 70 * 30)
    text_timer = text_seconds
    player = Player((225, 450), (80, 80))
    state = "start"
    end_sound = False

# Main Game loop
running = True
while running:
    screen.fill((0, 0, 0))

    # background animation
    screen.blit(bg_image, (0, 0))
    bg_current += 0.3

    if bg_current >= len(bg_sprites):
        bg_current = 0

    bg_image = bg_sprites[int(bg_current)]

    # Dont show player in states "title", "start", "intro" and "gameover"
    if (state != "title" and state != "start")  and (state != "intro" and state != "gameover"):
        for i in range(player.lives):
            screen.blit(heart, (0 + i * 20, 0))
    # Text
    if text_timer == 0:
        main_text = font.render("", True, (255, 255, 255))
        text_rect = main_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

        if state == "title":
            state = "intro"

        elif state == "start":
            next_wave()

        elif state == "loading" and len(current_wave.enemies) == 0:
            current_wave.create_enemies()
            gameplay_music.play()
            state = "gameplay"

        elif state == "boss":
            boss_music.play()
            state = "boss_fight"
            boss = Boss()

        elif state == "playagian":
            current_wave.create_enemies()
            state = "gameplay"

    else:
        text_timer -= 1

    # States Handle
    if state == "intro":
        screen.blit(intro_new_size, (0, 0))

    if intro_timer == 0 and state == "intro":
        main_text = font.render("Destroy The Enemies", True, (255, 255, 255))
        text_rect = main_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        state = "start"
        text_timer = text_seconds
    else:
        intro_timer -= 1

    if state == "end":
        if end_text_timer != 0:
            font = pygame.font.Font("assets/fonts/font.otf", 20)
            main_text = font.render("Congratulations! You have Completed the Game!", True, (0, 255, 0))
            text_rect = main_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            end_text_timer -= 1
        else:
            font = pygame.font.Font("assets/fonts/font.otf", 20)
            main_text = font.render("Developer: Abdullah", True, (255, 255, 255))
            text_rect = main_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))


    if state == "gameover":
        main_text = font.render("Game Over! press Enter!", True, (255, 20, 50))
        text_rect = main_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

    # Text print on screen
    screen.blit(main_text, text_rect)

    # Wave handler
    if current_wave != None and state == "gameplay":
        try:
            current_wave.main_loop()
        except:
            pass
        # Next Wave
        if state == "gameplay":
            if current_wave.wave_over_check() and text_timer == 0:
                next_wave()

    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key pressed
    keys = pygame.key.get_pressed()

    # Play again if ENTER pressed
    if state == "gameover" and keys[pygame.K_RETURN]:
        play_again()

    # Player Movement and Powers Timers
    if state == "gameplay" or state == "boss_fight":
        # Power
        if double_shoot_timer == 0:
            shoot_power = Power("double_pickup.png", player.double_shoot)
            powers.append(shoot_power)
            double_shoot_timer = random.randint(25 * 30, 60 * 30)
        else:
            double_shoot_timer -= 1

        if shield_timer == 0:
            shield_power = Power("pickup_shield.png", player.enable_shield)
            powers.append(shield_power)
            shield_timer = random.randint(50 * 30, 70 * 30)
        else:
            shield_timer -= 1

        # Player
        player.main_loop(keys)

        player.shooting(keys)

        # Power Handle
        if len(powers) > 0:
            for power in powers:
                screen.blit(power.new_size, power.rect)
                out_check = power.move()
                col_check = power.player_col()
                if out_check or col_check:
                    power.delete()
                    powers.pop(powers.index(power))
    
    # Check if player dead
    try:
        if not player.death_check():
            state = "gameover"
    except:
        pass
    
    # Gameover Sound
    if state == "gameover" and end_sound == False:
        pygame.mixer.stop()
        gameover_sound.play()
        end_sound = True

    # Bullets
    if len(bullets) > 0:
        for bullet in bullets:
            bullet.move()

            if bullet.bullet.y < 0 or bullet.bullet.y > 600:
                bullet.delete()
                bullets.pop(bullets.index(bullet))
            try:
                if (player.rect.colliderect(bullet.bullet) and bullet.shooter == "Enemy") and (state == "gameplay" or state == "boss_fight"):
                    if player.shield_state:
                        shield_break_sound.play
                    else:
                        destroy_sound.play()
                    player.damage()
                    bullet.delete()
                    bullets.pop(bullets.index(bullet))
            except:
                pass

    try: 
        if state == "gameover":
            for power in powers:
                powers.pop[powers.index(power)]
                power.delete()
            for enemy in current_wave.enemies:
                current_wave.enemies.pop(current_wave.enemies.index(enemy))
                del enemy.rect
                del enemy
    except:
        pass

    
    # Boss
    try:
        if state == "boss_death":
            is_dead = boss.death_animation()
            if is_dead:
                del boss.rect
                del boss
                state = "end"
                pygame.mixer.stop()
                game_win_sound.play()
        else:
            screen.blit(boss.engine_image, (boss.rect.x - (boss.size[0] - boss.rect.w)/2, boss.rect.y - (boss.size[1] - boss.rect.h)/2))
            screen.blit(boss.image, (boss.rect.x - (boss.size[0] - boss.rect.w)/2, boss.rect.y - (boss.size[1] - boss.rect.h)/2))
            if state == "boss_fight":

                boss.move()
                boss.death_check()
                boss.shoot()
                if player.rect.colliderect(boss.laser_rect) and boss.laser_state:
                    player.damage()

            if state == "gameover":
                del boss.rect
                del boss
    except:
        pass
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()