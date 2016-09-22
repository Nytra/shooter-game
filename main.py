import pygame, sys, math, random, time
from pygame.locals import *
from widgets import Button

pygame.mixer.pre_init(44100, 16, 2, 2048)
pygame.mixer.init()
pygame.init()

class dummy_sound_object:
	def play(self):
		pass

def player(x, y, colour, index):
	#player_rect = pygame.draw.rect(screen, blue, (x, y, 20, 20))
	if not (x, y, index) in cache:
		player = pygame.sprite.Sprite()
		player.rect = pygame.Rect(x, y, p_width, p_height)
		player.image = pygame.Surface((p_width, p_height))
		player.image.fill(colour)
		cache[(x, y, index)] = player
	return cache[(x, y, index)]

def get_bullet():
	if not "bullet" in cache:
		bullet = pygame.sprite.Sprite()
		bullet.image = pygame.Surface((bullet_w, bullet_h))
		bullet.image.fill(blue)
		cache["bullet"] = bullet
	return cache["bullet"]

def get_enemy(x, y, colour):
	if not (x, y) in cache:
		enemy = pygame.sprite.Sprite()
		enemy.rect = pygame.Rect(x, y, enemy_w, enemy_h)
		enemy.image = pygame.Surface((enemy_w, enemy_h))
		enemy.image.fill(colour)
		cache[(x, y)] = enemy
	return cache[(x, y)]

def render_message(text, font, colour):
	if not text in cache:
		cache[text] = font.render(text, True, colour)
	return cache[text]

def get_powerup(x, y, colour):
	if not (x, y) in cache:
		powerup = pygame.sprite.Sprite()
		powerup.rect = pygame.Rect(x, y, powerup_w, powerup_h)
		powerup.image = pygame.Surface((powerup_w, powerup_h))
		powerup.image.fill(colour)
		cache[(x, y)] = powerup
	return cache[(x, y)]

def game_loop():
	global cache, bullet_w, bullet_h

	move_up = False
	move_left = False
	move_down = False
	move_right = False

	x = RESOLUTION[0] // 2
	y = RESOLUTION[1] * 0.8
	shoot = False
	bullets = []
	enemies = []
	powerups = []
	direction = "up"

	score = 0
	score_increment = 1

	FPS = 60

	death_msg = "YOU DIED"
	dead = False

	enemy_speed = 1
	level = 1
	enemy_limit = level * 2
	powerup_limit = 1
	powerup_times = []

	player_colour = blue
	player_index = 0
	enemy_colour = red

	difficulty_changed = True
	force_shoot = False

	player_safe_range = 100
	new_level = True

	while True:

		# BEGIN DEFINE MESSAGES

		score_msg = "Score: %d" % score
		enemy_speed_msg = "Enemy Speed: %d px/f" % enemy_speed
		#enemy_limit_msg = "Enemy Limit: %d" % enemy_limit
		remaining_msg = "Enemies Remaining: %d" % enemy_limit
		fps_msg = "FPS: %d" % clock.get_fps()

		# END DEFINE MESSAGES

		# BEGIN EVENT HANDLING

		for event in pygame.event.get(): # BUG: Inputs queue while dead
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN and not dead:
				if event.key == pygame.K_w:
					move_up = True
				if event.key == pygame.K_a:
					move_left = True
				if event.key == pygame.K_s:
					move_down = True
				if event.key == pygame.K_d:
					move_right = True
				if event.key == pygame.K_p:
					shoot = True
				if event.key == pygame.K_o: # FOR DEBUGGING PURPOSES ONLY
					if force_shoot:
						force_shoot = False
					else:
						force_shoot = True
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					sys.exit()
			if event.type == pygame.KEYUP and not dead:
				if event.key == pygame.K_w:
					move_up = False
				if event.key == pygame.K_a:
					move_left = False
				if event.key == pygame.K_s:
					move_down = False
				if event.key == pygame.K_d:
					move_right = False
			if event.type == pygame.MOUSEBUTTONUP:
				mx, my = pygame.mouse.get_pos()
				if test_button.check_press((mx, my)):
					test_button.press()
					if test_button.pressed:
						test_button.set_text("On", status_font, blue)
					else:
						test_button.set_text("Off", status_font, blue)

		# END EVENT HANDLING

		screen.fill(bg_colour) # clear the screen

		# BEGIN PLAYER MOVEMENT LOGIC

		if move_up:
			y -= player_speed
			direction = "up"
			player_index += 1
		if move_left:
			x -= player_speed
			direction = "left"
			player_index += 1
		if move_down:
			y += player_speed
			direction = "down"
			player_index += 1
		if move_right:
			x += player_speed
			direction = "right"
			player_index += 1

		# END PLAYER MOVEMENT LOGIC

		# BEGIN SCREEN BOUNDARY LOGIC (KEEPS THE PLAYER ON THE SCREEN)

		if x < 0:
			x = 0
		if x > RESOLUTION[0] - p_width:
			x = RESOLUTION[0] - p_width
		if y < 0:
			y = 0
		if y > RESOLUTION[1] - p_height:
			y = RESOLUTION[1] - p_height

		# END SCREEN BOUNDARY LOGIC (KEEPS THE PLAYER ON THE SCREEN)

		# BEGIN DRAW PLAYER CROSSHAIR 

		if direction == "up":
			dir_pointer = pygame.draw.circle(screen, blue, (int(x + (p_width // 2)), int(y - (p_height // 4))), 2)
		if direction == "left":
			dir_pointer = pygame.draw.circle(screen, blue, (int(x - (p_width // 4)), int(y + (p_height // 2))), 2)
		if direction == "down":
			dir_pointer = pygame.draw.circle(screen, blue, (int(x + (p_width // 2)), int(y + (int(p_height * 1.25)))), 2)
		if direction == "right":
			dir_pointer = pygame.draw.circle(screen, blue, (int(x + int(p_width * 1.25)), int(y + (p_height // 2))), 2)

		# END DRAW PLAYER CROSSHAIR

		# BEGIN INCREASE DIFFICULTY LOGIC

		if enemy_limit <= 0: # if all enemies have been eliminated
			level += 1
			enemy_limit = level * 2
			#enemy_speed += 1
			enemies = []
			bullets = []
			new_level = True
			cache = {} # clear the cache to reduce memory usage

		# END INCREASE DIFFICULTY LOGIC

		# BEGIN SPAWN ENEMY LOGIC 

		if len(enemies) < enemy_limit and new_level == True: # this code is broken, safe range doesn't work properly
			for e in range(enemy_limit):
				index = e
				enemy_x = random.randrange(0, RESOLUTION[0] - enemy_w)
				if not enemy_x > x + player_safe_range or not enemy_x < x - player_safe_range: # place enemy at least (safe range) px away from player
					if enemy_x > x:
						diff = enemy_x - x
						enemy_x += diff
					elif enemy_x < x:
						diff = x - enemy_x
						enemy_x -= diff
					else:
						if enemy_x > RESOLUTION[0] - enemy_w:
							enemy_x -= player_safe_range
						else:
							enemy_x += player_safe_range

				enemy_y = random.randrange(0, RESOLUTION[1] - enemy_h)
				if not enemy_y > y + player_safe_range or not enemy_y < y - player_safe_range:
					if enemy_y > y:
						diff = enemy_y - y
						enemy_y += diff
					elif enemy_y < y:
						diff = y - enemy_y
						enemy_y -= diff
					else:
						if enemy_y > RESOLUTION[1] - enemy_h:
							enemy_y -= player_safe_range
						else:
							enemy_y += player_safe_range

				enemy_dir = random.choice(("up", "down", "left", "right"))
				enemies.append([get_enemy(enemy_x, enemy_y, enemy_colour), enemy_x, enemy_y, enemy_dir, index])
			new_level = False

		# END SPAWN ENEMY LOGIC

		# BEGIN ENEMY MOVEMENT LOGIC

		for enemy in enemies:
			eo, ex, ey, ed, eindex = enemy
			if ed == "up":
				ey -= enemy_speed
			if ed == "left":
				ex -= enemy_speed
			if ed == "down":
				ey += enemy_speed
			if ed == "right":
				ex += enemy_speed

			if ex > RESOLUTION[0] - enemy_w: # if the enemy has reached a boundary, send them off in a different direction
				ex = RESOLUTION[0] - enemy_w
				ed = random.choice(("up", "left", "down"))
			if ex < 0:
				ex = 0
				ed = random.choice(("up", "down", "right"))
			if ey < 0:
				ey = 0
				ed = random.choice(("down", "left", "right"))
			if ey > RESOLUTION[1] - enemy_h:
				ey = RESOLUTION[1] - enemy_h
				ed = random.choice(("up", "left", "right"))

			num = random.randint(1, 1000) # small chance of changing direction
			if num > 990:
				ed = random.choice(("up", "down", "left", "right"))

			enemies.remove(enemy)
			enemies.append([eo, ex, ey, ed, eindex])

		# END ENEMY MOVEMENT LOGIC

		# BEGIN SHOOTING LOGIC

		if shoot or force_shoot: # force_shoot is for debugging only
			shot_snd.play()
			bullet = get_bullet() # get the sprite object

			if direction == "up" or direction == "down": # this does work but i would like to have the bullet appear in the same position on any side of the player
				bullet.rect = pygame.Rect(x + 5, y, bullet_w, bullet_h)
				bullets.append([bullet, x + 5, y, direction])
			if direction == "left" or direction == "right":
				bullet.rect = pygame.Rect(x, y + 5, bullet_w, bullet_h)
				bullets.append([bullet, x, y + 5, direction])

			shoot = False 

		# END SHOOTING LOGIC

		# BEGIN POWERUP LOGIC

		num = random.randint(1, 10000)
		if num > 9950 and len(powerups) < powerup_limit and len(powerup_times) < 1:
			rx = random.randrange(1, RESOLUTION[0] - powerup_w)
			ry = random.randrange(1, RESOLUTION[1] - powerup_h)
			powerup = get_powerup(rx, ry, green)
			powerups.append([powerup, rx, ry, green, len(powerups)])

		for powerup in powerups:
			po, px, py, pc, pindex = powerup
			screen.blit(po.image, (px, py))
			if po.rect.colliderect(player(x, y, player_colour, player_index).rect):
				#print("powerup gained")
				powerups.remove(powerup)
				# do powerup stuff here
				score += 5

				starttime = pygame.time.get_ticks()
				powerup_times.append(starttime)
		if len(powerup_times) > 0:
			for t in powerup_times:
				if pygame.time.get_ticks() - t >= 5000: # ms
					score_increment = 1
					player_colour = blue
					powerup_times.remove(t)
				else:
					player_colour = green
					player_index += 1
					score_increment = 5
		else:
			score_increment = 1
			player_colour = blue


		# END POWERUP LOGIC

		for b in range(len(bullets)): # move bullets
			bullet = bullets[b]
			if bullet[3] == "up":
				bullet[2] = bullets[b][2] - bullet_speed
			elif bullet[3] == "left":
				bullet[1] = bullets[b][1] - bullet_speed
			elif bullet[3] == "down":
				bullet[2] = bullets[b][2] + bullet_speed
			elif bullet[3] == "right":
				bullet[1] = bullets[b][1] + bullet_speed

		for enemy in enemies: # detect collision between bullets and enemies, remove bullets that have left the screen
			eo, ex, ey, ed, eindex = enemy
			if len(bullets) > 0:
				enemy_rect = get_enemy(ex, ey, enemy_colour).rect
				for bullet in bullets:
					bo, bx, by, bdir = bullet
					bullet_rect = pygame.draw.rect(screen, red, (bx, by, bullet_w, bullet_h)) # ???
					if enemy_rect.colliderect(bullet_rect):
						score += score_increment
						enemy_limit -= 1
						difficulty_changed = False
						bullets.remove(bullet)
						try:
							enemies.remove(enemy)
						except ValueError as error:
							print("A ValueError occurred when removing enemy from list.", enemy)
					elif bx < 0 or bx > RESOLUTION[0] or by < 0 or by > RESOLUTION[1]:
						bullets.remove(bullet)

		# BEGIN GAME DIFFICULTY LOGIC

		if not difficulty_changed:
			if score % 5 == 0 and score > 0:
				pass
			if score % 20 == 0 and score > 0:
				pass
			difficulty_changed = True

		# END GAME DIFFICULTY LOGIC


		for bullet in bullets: # draw bullets
			#bullet_rect = pygame.draw.rect(screen, red, (bullet[0], bullet[1], bullet_w, bullet_h))
			screen.blit(bullet[0].image, (bullet[1], bullet[2]))

		for enemy in enemies:
			eo, ex, ey, ed, eindex = enemy
			ex = int(ex)
			ey = int(ey)

			x = int(x)
			y = int(y)

			enemy_rect = get_enemy(ex, ey, enemy_colour).rect #pygame.draw.rect(screen, red, (ex, ey, enemy_w, enemy_h))
			player_rect = player(x, y, player_colour, player_index).rect

			screen.blit(eo.image, (ex, ey))

			if player_rect.colliderect(enemy_rect):
				pygame.display.update()
				# player death
				screen.fill(red)

				death_render = big_alert_font.render(death_msg, True, black)
				death_rect = death_render.get_rect()
				death_rect.center = (RESOLUTION[0] // 2, RESOLUTION[1] // 2)
				screen.blit(death_render, death_rect)
				pygame.display.update()
				dead = True

				flag = True
				starttime = pygame.time.get_ticks()
				cache = {}

				while flag:

					if pygame.time.get_ticks() - starttime >= 2000: # wait 2000 ms
						flag = False

				game_loop()

		p = player(x, y, player_colour, player_index) # get the player sprite object
		screen.blit(p.image, (x, y)) # draw the player

		#screen.blit(test_button.button.image, (test_button.x, test_button.y))
		#screen.blit(test_button.text_render, (test_button.x, test_button.y))

		score_render = render_message(score_msg, status_font, black) 
		speed_render = render_message(enemy_speed_msg, status_font, black) 
		remaining_render = render_message(remaining_msg, status_font, black) 
		fps_render = render_message(fps_msg, status_font, black) 
		
		screen.blit(score_render, (0, 0))
		screen.blit(speed_render, (0, 20))
		screen.blit(remaining_render, (0, 40))
		screen.blit(fps_render, (0, 60))

		pygame.display.update() # push everything to the screen
		clock.tick(FPS)

white = 255, 255, 255
black = 0, 0, 0
red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255
bg_colour = white

# get opts

args = sys.argv
if "-mute" in args:
	shot_snd = dummy_sound_object()
if "-nomusic" in args or "-mute" in args:
	pass
else:
	pygame.mixer.music.load("music.ogg")
	pygame.mixer.music.set_volume(0.5)
	pygame.mixer.music.play(-1)
	shot_snd = pygame.mixer.Sound("shot.ogg")

pygame.mixer.music.set_volume(0)

pygame.display.set_caption("Square Shooting Simulator 2016")

#shot_snd = pygame.mixer.Sound("shot.ogg")

if "-fullscreen" in args:
	flags = HWSURFACE | DOUBLEBUF | FULLSCREEN #| DOUBLEBUF
else:
	flags = HWSURFACE | DOUBLEBUF

bpp = 16
infoObject = pygame.display.Info()
RESOLUTION = (infoObject.current_w, infoObject.current_h) 
#RESOLUTION = (800, 600)
screen = pygame.display.set_mode((RESOLUTION[0], RESOLUTION[1]), flags, bpp)
screen.fill(bg_colour)

clock = pygame.time.Clock()

status_font = pygame.font.SysFont("monospace", 16)
big_alert_font = pygame.font.SysFont("monospace", 80)

test_button = Button((500, 0, 100, 50), red, text="button", font=status_font)

p_width	= 20 # p is short for player
p_height = 20
enemy_x = 40
enemy_y = 40
enemy_w = 20
enemy_h = 20
bullet_w = 10
bullet_h = 10
player_speed = 5
bullet_speed = 15
powerup_w = 10
powerup_h = 10

cache = {} # used for storing frequently used game objects which improves performance

game_loop()