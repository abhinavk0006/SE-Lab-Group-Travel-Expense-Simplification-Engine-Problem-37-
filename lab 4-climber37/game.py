import random
import pygame

WIDTH, HEIGHT = 480, 640
FPS = 60
BG = (20, 20, 40)
GRAVITY, JUMP_SPEED, MOVE_SPEED = 0.5, -13, 4
PLAYER_W, PLAYER_H = 36, 36
PLATFORM_H = 14
COIN_R = 7
LIVES_START = 3


def platform_color(index, total):
    """Return a gradually changing colour based on platform height."""
    if index == 0 or total <= 0:
        return None

    progress = max(0.0, min(1.0, index / total))

    # Gradually transition from green toward purple/blue.
    r = int(80 + 150 * progress)
    g = int(190 - 110 * progress)
    b = int(100 + 150 * progress)

    return (r, g, b)


def moving_platform_speed(index, total):
    """Return a horizontal movement speed for selected platforms."""
    if index == 0 or total <= 0:
        return 0

    # Every third platform moves.
    if index % 3 == 0:
        # Slightly increase movement speed as the player climbs.
        progress = max(0.0, min(1.0, index / total))
        return 1.0 + 0.75 * progress

    return 0


def on_coin_collected(coin, score):
    """Create a sparkle effect when a coin is collected."""
    coin.effect_timer = 15


class Platform:
    def __init__(self, index, total, x, y, w=120, movable=True):
        self.rect = pygame.Rect(x, y, w, PLATFORM_H)
        self.speed = (moving_platform_speed(index, total) or 0) if movable else 0
        self.bounds = (max(0, x - 60), min(WIDTH - w, x + 60))
        self.color = platform_color(index, total) or (100, 180, 100)

    def update(self):
        if not self.speed:
            return 0

        dx = self.speed

        if self.rect.x <= self.bounds[0] or self.rect.x >= self.bounds[1]:
            self.speed = -self.speed
            dx = self.speed

        self.rect.x = max(
            self.bounds[0],
            min(self.bounds[1], self.rect.x + dx)
        )

        return dx

    def draw(self, screen, cam_y):
        pygame.draw.rect(
            screen,
            self.color,
            self.rect.move(0, -cam_y),
            border_radius=4
        )


class Coin:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.taken = False
        self.effect_timer = 0

    def draw(self, screen, cam_y):
        if self.taken:
            return

        screen_pos = pygame.Vector2(
            self.pos.x,
            self.pos.y - cam_y
        )

        pygame.draw.circle(
            screen,
            (250, 210, 60),
            (int(screen_pos.x), int(screen_pos.y)),
            COIN_R
        )

        pygame.draw.circle(
            screen,
            (255, 240, 130),
            (int(screen_pos.x), int(screen_pos.y)),
            COIN_R - 3
        )


class CoinSparkle:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.timer = 18
        self.max_timer = 18

    def update(self):
        self.timer -= 1
        return self.timer > 0

    def draw(self, screen, cam_y):
        progress = 1 - (self.timer / self.max_timer)

        radius = int(6 + progress * 18)
        alpha = max(0, int(255 * (1 - progress)))

        sparkle_surface = pygame.Surface(
            (radius * 2 + 10, radius * 2 + 10),
            pygame.SRCALPHA
        )

        center = radius + 5

        pygame.draw.circle(
            sparkle_surface,
            (255, 220, 70, alpha),
            (center, center),
            radius,
            2
        )

        pygame.draw.line(
            sparkle_surface,
            (255, 245, 150, alpha),
            (center - radius, center),
            (center + radius, center),
            2
        )

        pygame.draw.line(
            sparkle_surface,
            (255, 245, 150, alpha),
            (center, center - radius),
            (center, center + radius),
            2
        )

        screen.blit(
            sparkle_surface,
            (
                int(self.pos.x - center),
                int(self.pos.y - cam_y - center)
            )
        )


def generate_platforms(num, start_y, width):
    platforms = [
        Platform(0, num, 0, start_y, width, movable=False)
    ]

    y = start_y - 100

    for i in range(1, num + 1):
        x = random.randint(20, width - 140)
        w = random.randint(80, 160)

        platforms.append(
            Platform(i, num, x, y, w)
        )

        y -= random.randint(70, 120)

    return platforms


def spawn_coins(platforms):
    coins = []

    for plat in platforms[1:]:
        if random.random() < 0.4:
            coins.append(
                Coin(
                    plat.rect.centerx,
                    plat.rect.top - 14
                )
            )

    return coins


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(
            x,
            y,
            PLAYER_W,
            PLAYER_H
        )

        self.vel_y = 0.0
        self.vel_x = 0
        self.on_ground = False
        self.standing_on = None
        self.color = (60, 120, 200)

    def move(self, keys):
        self.vel_x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -MOVE_SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = MOVE_SPEED

        if (
            keys[pygame.K_SPACE]
            or keys[pygame.K_w]
            or keys[pygame.K_UP]
        ) and self.on_ground:
            self.vel_y = JUMP_SPEED
            self.on_ground = False

    def update(self, platforms):
        self.vel_y = min(
            self.vel_y + GRAVITY,
            12
        )

        previous_bottom = self.rect.bottom

        self.rect.x = max(
            0,
            min(
                WIDTH - self.rect.width,
                self.rect.x + self.vel_x
            )
        )

        self.rect.y += int(self.vel_y)

        self.on_ground = False
        self.standing_on = None

        if self.vel_y >= 0:
            for plat in platforms:
                overlaps = (
                    self.rect.right > plat.rect.left
                    and self.rect.left < plat.rect.right
                )

                if (
                    overlaps
                    and previous_bottom <= plat.rect.top + 1
                    and self.rect.bottom >= plat.rect.top
                ):
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.standing_on = plat
                    break

    def draw(self, screen, cam_y):
        draw_rect = self.rect.move(
            0,
            -cam_y
        )

        pygame.draw.rect(
            screen,
            self.color,
            draw_rect,
            border_radius=6
        )

        pygame.draw.circle(
            screen,
            (255, 220, 180),
            (
                draw_rect.centerx,
                draw_rect.top + 10
            ),
            7
        )


class Game:
    def __init__(self):
        self.font = pygame.font.Font(
            None,
            26
        )

        self.big_font = pygame.font.Font(
            None,
            42
        )

        self.reset()

    def reset(self):
        self.platforms = generate_platforms(
            60,
            HEIGHT - 40,
            WIDTH
        )

        self.coins = spawn_coins(
            self.platforms
        )

        self.coin_effects = []

        self.player = Player(
            WIDTH // 2 - PLAYER_W // 2,
            HEIGHT - 100
        )

        self.cam_y = 0

        self.height = 0
        self.coin_score = 0
        self.lives = LIVES_START

        self.last_safe = pygame.Vector2(
            self.player.rect.x,
            self.player.rect.y
        )

        self.state = "play"

        self.top_y = self.platforms[-1].rect.y

    def score(self):
        return int(self.height) + self.coin_score

    def update(self, keys):
        if self.state != "play":
            return

        self.player.move(keys)

        for plat in self.platforms:
            dx = plat.update()

            if dx and self.player.standing_on is plat:
                self.player.rect.x += dx

        self.player.update(
            self.platforms
        )

        target_cam = (
            self.player.rect.centery
            - HEIGHT // 2
        )

        if target_cam < self.cam_y:
            self.cam_y = target_cam

        # Height now tracks the maximum height reached.
        current_height = max(
            0,
            (HEIGHT - 40 - self.player.rect.y) // 10
        )

        self.height = max(
            self.height,
            current_height
        )

        if self.player.on_ground:
            self.last_safe = pygame.Vector2(
                self.player.rect.x,
                self.player.rect.y
            )

        for coin in self.coins:
            if (
                not coin.taken
                and self.player.rect.collidepoint(
                    coin.pos
                )
            ):
                coin.taken = True
                self.coin_score += 50

                self.coin_effects.append(
                    CoinSparkle(coin.pos)
                )

                on_coin_collected(
                    coin,
                    self.score()
                )

        self.coins = [
            c for c in self.coins
            if not c.taken
        ]

        self.coin_effects = [
            effect
            for effect in self.coin_effects
            if effect.update()
        ]

        if (
            self.player.rect.top - self.cam_y
            > HEIGHT + 50
        ):
            self.lives -= 1

            if self.lives <= 0:
                self.state = "lose"

            else:
                self.player.rect.x = int(
                    self.last_safe.x
                )

                self.player.rect.y = int(
                    self.last_safe.y
                )

                self.player.vel_y = 0

        if self.player.rect.y <= self.top_y:
            self.state = "win"

    def draw(self, screen):
        screen.fill(BG)

        for plat in self.platforms:
            plat.draw(
                screen,
                self.cam_y
            )

        for coin in self.coins:
            coin.draw(
                screen,
                self.cam_y
            )

        for effect in self.coin_effects:
            effect.draw(
                screen,
                self.cam_y
            )

        self.player.draw(
            screen,
            self.cam_y
        )

        hud = self.font.render(
            f"Height: {self.height}m  "
            f"Coins: {self.coin_score // 50}  "
            f"Lives: {self.lives}",
            True,
            (200, 200, 200)
        )

        screen.blit(
            hud,
            (10, 10)
        )

        if self.state != "play":
            text = (
                "YOU REACHED THE TOP!"
                if self.state == "win"
                else "YOU FELL!"
            )

            color = (
                (80, 220, 80)
                if self.state == "win"
                else (220, 60, 60)
            )

            msg = self.big_font.render(
                text,
                True,
                color
            )

            sub = self.font.render(
                "Press R to Restart",
                True,
                (180, 180, 180)
            )

            screen.blit(
                msg,
                msg.get_rect(
                    center=(
                        WIDTH // 2,
                        HEIGHT // 2 - 20
                    )
                )
            )

            screen.blit(
                sub,
                sub.get_rect(
                    center=(
                        WIDTH // 2,
                        HEIGHT // 2 + 30
                    )
                )
            )


def main():
    pygame.init()

    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT)
    )

    pygame.display.set_caption(
        "Climber"
    )

    clock = pygame.time.Clock()

    game = Game()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_r
            ):
                game.reset()

        game.update(
            pygame.key.get_pressed()
        )

        game.draw(screen)

        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()