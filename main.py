
import pygame
import random

# ---------------- CONFIG ---------------- #
WIDTH, HEIGHT = 800, 600
FPS = 60
TITLE = "RPG Auto Battle"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
GRAY = (100, 100, 100)
BG_COLOR = (25, 25, 35)

# ---------------- ENTIDADES ---------------- #
class Player:
    def __init__(self, name="Herói", hp=120, atk=15, defense=3):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.x, self.y = 150, 300
        self.width, self.height = 60, 80

    def is_alive(self):
        return self.hp > 0

    def attack(self):
        return max(1, self.atk + random.randint(-2, 4))

    def take_damage(self, dmg):
        final = max(0, dmg - self.defense)
        self.hp = max(0, self.hp - final)
        return final


class Enemy:
    def __init__(self, name="Goblin", hp=100, atk=10, defense=2):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.x, self.y = 550, 300
        self.width, self.height = 70, 90

    def is_alive(self):
        return self.hp > 0

    def attack(self):
        return max(1, self.atk + random.randint(-3, 3))

    def take_damage(self, dmg):
        final = max(0, dmg - self.defense)
        self.hp = max(0, self.hp - final)
        return final


# ---------------- COMBATE AUTOMÁTICO ---------------- #
class AutoAttack:
    def __init__(self, attacker, target, interval_ms=1200):
        self.attacker = attacker
        self.target = target
        self.interval = interval_ms
        self.active = False
        self.last_attack = 0

    def toggle(self):
        self.active = not self.active
        self.last_attack = pygame.time.get_ticks()

    def update(self):
        if not self.active or not self.attacker.is_alive() or not self.target.is_alive():
            return None

        now = pygame.time.get_ticks()
        if now - self.last_attack >= self.interval:
            dmg = self.attacker.attack()
            taken = self.target.take_damage(dmg)
            self.last_attack = now
            return f"{self.attacker.name} atacou automaticamente e causou {taken} de dano."
        return None


# ---------------- HUD ---------------- #
def draw_bar(surface, x, y, w, h, value, max_value, color):
    pygame.draw.rect(surface, GRAY, (x, y, w, h))
    filled = int((value / max_value) * w)
    pygame.draw.rect(surface, color, (x, y, filled, h))
    pygame.draw.rect(surface, BLACK, (x, y, w, h), 2)

def draw_text(surface, text, x, y, font, color=WHITE):
    render = font.render(text, True, color)
    surface.blit(render, (x, y))


# ---------------- MAIN ---------------- #
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)
    big_font = pygame.font.SysFont("Arial", 28, bold=True)

    player = Player(name="Matheus", hp=120, atk=15, defense=3)
    enemy = Enemy(name="Orc", hp=110, atk=10, defense=2)
    auto = AutoAttack(player, enemy)

    logs = []
    running = True

    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_SPACE and player.is_alive() and enemy.is_alive():
                    dmg = player.attack()
                    taken = enemy.take_damage(dmg)
                    logs.insert(0, f"{player.name} atacou manualmente e causou {taken} de dano.")

                if event.key == pygame.K_a:
                    auto.toggle()
                    logs.insert(0, f"Ataque automático {'ativado' if auto.active else 'pausado'}.")

                if event.key == pygame.K_s and enemy.is_alive() and player.is_alive():
                    dmg = enemy.attack()
                    taken = player.take_damage(dmg)
                    logs.insert(0, f"{enemy.name} atacou e causou {taken} de dano.")

        # Atualiza ataque automático
        result = auto.update()
        if result:
            logs.insert(0, result)

        logs = logs[:6]  # limite de histórico

        # --- Renderização ---
        screen.fill(BG_COLOR)

        # Jogador
        pygame.draw.rect(screen, (80, 160, 220), (player.x, player.y - player.height//2, player.width, player.height))
        draw_bar(screen, player.x, player.y + 50, 120, 12, player.hp, player.max_hp, GREEN)
        draw_text(screen, player.name, player.x, player.y + 70, font)

        # Inimigo
        pygame.draw.rect(screen, (180, 60, 60), (enemy.x, enemy.y - enemy.height//2, enemy.width, enemy.height))
        draw_bar(screen, enemy.x, enemy.y + 50, 120, 12, enemy.hp, enemy.max_hp, RED)
        draw_text(screen, enemy.name, enemy.x, enemy.y + 70, font)

        # Logs
        y = HEIGHT - 25
        for line in logs:
            draw_text(screen, line, 20, y, font)
            y -= 20

        # Instruções
        draw_text(screen, "Espaço: ataque manual | A: auto-ataque | S: inimigo ataca | ESC: sair", 20, 20, font)

        # Fim de jogo
        if not enemy.is_alive():
            draw_text(screen, "Inimigo derrotado!", WIDTH//2 - 100, HEIGHT//2 - 40, big_font, GREEN)
            auto.active = False
        elif not player.is_alive():
            draw_text(screen, "Você foi derrotado.", WIDTH//2 - 100, HEIGHT//2 - 40, big_font, RED)
            auto.active = False

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()


