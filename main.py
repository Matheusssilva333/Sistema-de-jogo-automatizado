
import pygame
import random
import time # Para os delays

# --- Configurações do Jogo ---
WIDTH, HEIGHT = 800, 600
FPS = 60
TITLE = "RPG Auto Battle"

# --- Cores ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (80, 160, 220)
GRAY = (100, 100, 100)
BG_COLOR = (25, 25, 35)

# --- Classes do Jogo ---
class Player:
    def __init__(self, nome="Herói"): # Nome padrão
        self.nome = nome
        self.nivel = 1
        self.experiencia = 0
        self.vida_max = 120
        self.vida = self.vida_max
        self.mana_max = 50
        self.mana = self.mana_max
        self.ataque = 15
        self.defesa = 3
        self.velocidade = 5 # Determina quem ataca primeiro
        self.x, self.y = 150, HEIGHT // 2 # Posição na tela
        self.width, self.height = 60, 80
        self.cor = BLUE

    def esta_vivo(self):
        return self.vida > 0

    def calcular_dano(self):
        return max(1, self.ataque + random.randint(-2, 4))

    def receber_dano(self, dano):
        dano_final = max(0, dano - self.defesa)
        self.vida = max(0, self.vida - dano_final)
        return dano_final

    def subir_de_nivel(self):
        self.nivel += 1
        self.vida_max += 20
        self.vida = self.vida_max # Cura completa ao subir de nível
        self.mana_max += 10
        self.mana = self.mana_max
        self.ataque += 3
        self.defesa += 1
        self.velocidade += 1
        return f"Parabéns! {self.nome} subiu para o Nível {self.nivel}!"

    def desenhar(self, surface):
        # Corpo do jogador (círculo)
        pygame.draw.circle(surface, self.cor, (self.x + self.width // 2, self.y + self.height // 2), self.width // 2)
        # Olhos (pequenos círculos)
        pygame.draw.circle(surface, WHITE, (self.x + self.width // 2 - 10, self.y + self.height // 2 - 10), 5)
        pygame.draw.circle(surface, WHITE, (self.x + self.width // 2 + 10, self.y + self.height // 2 - 10), 5)
        pygame.draw.circle(surface, BLACK, (self.x + self.width // 2 - 10, self.y + self.height // 2 - 10), 2)
        pygame.draw.circle(surface, BLACK, (self.x + self.width // 2 + 10, self.y + self.height // 2 - 10), 2)
        # Boca (linha)
        pygame.draw.line(surface, WHITE, (self.x + self.width // 2 - 10, self.y + self.height // 2 + 10), (self.x + self.width // 2 + 10, self.y + self.height // 2 + 10), 2)


class Enemy:
    def __init__(self, nivel_jogador):
        self.nome = random.choice(["Goblin", "Orc", "Esqueleto", "Zumbi", "Aranha Gigante"])
        self.nivel = nivel_jogador + random.randint(-1, 1) # Nível do inimigo próximo ao do jogador
        if self.nivel < 1: self.nivel = 1
        self.vida_max = 50 + (self.nivel * 10)
        self.vida = self.vida_max
        self.ataque = 5 + (self.nivel * 2)
        self.defesa = 2 + (self.nivel * 1)
        self.velocidade = 4 # Velocidade base do inimigo
        self.experiencia_recompensa = 10 * self.nivel
        self.x, self.y = 550, HEIGHT // 2 # Posição na tela
        self.width, self.height = 70, 90
        self.cor = RED

    def esta_vivo(self):
        return self.vida > 0

    def calcular_dano(self):
        return max(1, self.ataque + random.randint(-3, 3))

    def receber_dano(self, dano):
        dano_final = max(0, dano - self.defesa)
        self.vida = max(0, self.vida - dano_final)
        return dano_final

    def desenhar(self, surface):
        # Corpo do inimigo (triângulo)
        pontos = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(surface, self.cor, pontos)
        # Olho (círculo)
        pygame.draw.circle(surface, WHITE, (self.x + self.width // 2, self.y + self.height // 3), 8)
        pygame.draw.circle(surface, BLACK, (self.x + self.width // 2, self.y + self.height // 3), 4)


# --- Funções de Desenho da HUD ---
def desenhar_barra(surface, x, y, w, h, valor, valor_max, cor):
    pygame.draw.rect(surface, GRAY, (x, y, w, h))
    preenchido = int((valor / valor_max) * w)
    pygame.draw.rect(surface, cor, (x, y, preenchido, h))
    pygame.draw.rect(surface, BLACK, (x, y, w, h), 2)

def desenhar_texto(surface, texto, x, y, font, cor=WHITE, alinhamento="esquerda"):
    render = font.render(texto, True, cor)
    if alinhamento == "centro":
        x -= render.get_width() // 2
    surface.blit(render, (x, y))


# --- Loop Principal do Jogo ---
def main(nome_jogador):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # Fontes
    font_pequena = pygame.font.SysFont("Arial", 16)
    font_media = pygame.font.SysFont("Arial", 20)
    font_grande = pygame.font.SysFont("Arial", 28, bold=True)

    # Cria o jogador
    jogador = Player(nome_jogador)

    # Variáveis de estado da batalha
    inimigo_atual = None
    logs_batalha = []
    estado_jogo = "exploracao" # ou "batalha", "fim_de_jogo"
    turno_batalha = 0
    ultimo_ataque_tempo = 0
    intervalo_ataque = 1500 # ms entre ataques automáticos
    efeito_ataque_jogador = 0 # 0: nenhum, 1: atacando
    efeito_ataque_inimigo = 0 # 0: nenhum, 1: atacando

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.K_ESCAPE:
                running = False
            
            if estado_jogo == "exploracao":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: # Inicia uma batalha
                    inimigo_atual = Enemy(jogador.nivel)
                    logs_batalha.clear()
                    logs_batalha.insert(0, f"!!! Uma batalha começou entre {jogador.nome} e {inimigo_atual.nome} !!!")
                    estado_jogo = "batalha"
                    turno_batalha = 0
                    ultimo_ataque_tempo = pygame.time.get_ticks() # Reseta o timer do ataque
            elif estado_jogo == "fim_de_jogo":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: # Reinicia ou volta para exploração
                    jogador = Player(jogador.nome) # Reinicia o jogador
                    estado_jogo = "exploracao"
                    logs_batalha.clear()
                    inimigo_atual = None

        # --- Lógica do Jogo ---
        if estado_jogo == "batalha" and jogador.esta_vivo() and inimigo_atual.esta_vivo():
            agora = pygame.time.get_ticks()
            if agora - ultimo_ataque_tempo > intervalo_ataque:
                turno_batalha += 1
                logs_batalha.insert(0, f"--- Turno {turno_batalha} ---")

                # Determina quem ataca primeiro baseado na velocidade
                if jogador.velocidade >= inimigo_atual.velocidade:
                    # Jogador ataca
                    efeito_ataque_jogador = 1
                    dano_causado_jogador = jogador.calcular_dano()
                    dano_recebido_inimigo = inimigo_atual.receber_dano(dano_causado_jogador)
                    logs_batalha.insert(0, f"{jogador.nome} ataca {inimigo_atual.nome} causando {dano_recebido_inimigo} de dano.")
                    time.sleep(0.2) # Pequeno delay para visualização do ataque
                    efeito_ataque_jogador = 0

                    if not inimigo_atual.esta_vivo():
                        logs_batalha.insert(0, f"{inimigo_atual.nome} foi derrotado!")
                        jogador.experiencia += inimigo_atual.experiencia_recompensa
                        logs_batalha.insert(0, f"{jogador.nome} ganhou {inimigo_atual.experiencia_recompensa} de experiência.")
                        if jogador.experiencia >= jogador.nivel * 100: # XP necessário para subir de nível
                            msg_nivel = jogador.subir_de_nivel()
                            logs_batalha.insert(0, msg_nivel)
                        estado_jogo = "exploracao" # Volta para exploração após a vitória
                        inimigo_atual = None # Remove o inimigo derrotado
                    else:
                        # Inimigo ataca (se ainda estiver vivo)
                        efeito_ataque_inimigo = 1
                        dano_causado_inimigo = inimigo_atual.calcular_dano()
                        dano_recebido_jogador = jogador.receber_dano(dano_causado_inimigo)
                        logs_batalha.insert(0, f"{inimigo_atual.nome} ataca {jogador.nome} causando {dano_recebido_jogador} de dano.")
                        time.sleep(0.2) # Pequeno delay para visualização do ataque
                        efeito_ataque_inimigo = 0

                        if not jogador.esta_vivo():
                            logs_batalha.insert(0, f"{jogador.nome} foi derrotado... Fim de jogo.")
                            estado_jogo = "fim_de_jogo"
                else: # Inimigo ataca primeiro
                    # Inimigo ataca
                    efeito_ataque_inimigo = 1
                    dano_causado_inimigo = inimigo_atual.calcular_dano()
                    dano_recebido_jogador = jogador.receber_dano(dano_causado_inimigo)
                    logs_batalha.insert(0, f"{inimigo_atual.nome} ataca {jogador.nome} causando {dano_recebido_jogador} de dano.")
                    time.sleep(0.2) # Pequeno delay para visualização do ataque
                    efeito_ataque_inimigo = 0

                    if not jogador.esta_vivo():
                        logs_batalha.insert(0, f"{jogador.nome} foi derrotado... Fim de jogo.")
                        estado_jogo = "fim_de_jogo"
                    else:
                        # Jogador ataca (se ainda estiver vivo)
                        efeito_ataque_jogador = 1
                        dano_causado_jogador = jogador.calcular_dano()
                        dano_recebido_inimigo = inimigo_atual.receber_dano(dano_causado_jogador)
                        logs_batalha.insert(0, f"{jogador.nome} ataca {inimigo_atual.nome} causando {dano_recebido_inimigo} de dano.")
                        time.sleep(0.2) # Pequeno delay para visualização do ataque
                        efeito_ataque_jogador = 0

                        if not inimigo_atual.esta_vivo():
                            logs_batalha.insert(0, f"{inimigo_atual.nome} foi derrotado!")
                            jogador.experiencia += inimigo_atual.experiencia_recompensa
                            logs_batalha.insert(0, f"{jogador.nome} ganhou {inimigo_atual.experiencia_recompensa} de experiência.")
                            if jogador.experiencia >= jogador.nivel * 100: # XP necessário para subir de nível
                                msg_nivel = jogador.subir_de_nivel()
                                logs_batalha.insert(0, msg_nivel)
                            estado_jogo = "exploracao" # Volta para exploração após a vitória
                            inimigo_atual = None # Remove o inimigo derrotado
                
                ultimo_ataque_tempo = agora # Atualiza o tempo do último ataque

        # Limita o histórico de logs
        logs_batalha = logs_batalha[:10]

        # --- Renderização ---
        screen.fill(BG_COLOR)

        # Desenha o jogador
        jogador.desenhar(screen)
        desenhar_barra(screen, jogador.x - 30, jogador.y + 50, 120, 12, jogador.vida, jogador.vida_max, GREEN)
        desenhar_texto(screen, jogador.nome, jogador.x + jogador.width // 2, jogador.y + 70, font_media, alinhamento="centro")
        desenhar_texto(screen, f"Nível: {jogador.nivel}", jogador.x + jogador.width // 2, jogador.y + 90, font_pequena, alinhamento="centro")
        desenhar_texto(screen, f"XP: {jogador.experiencia}/{jogador.nivel * 100}", jogador.x + jogador.width // 2, jogador.y + 105, font_pequena, alinhamento="centro")

        # Desenha o inimigo (se houver)
        if inimigo_atual:
            inimigo_atual.desenhar(screen)
            desenhar_barra(screen, inimigo_atual.x - 30, inimigo_atual.y + 50, 120, 12, inimigo_atual.vida, inimigo_atual.vida_max, RED)
            desenhar_texto(screen, inimigo_atual.nome, inimigo_atual.x + inimigo_atual.width // 2, inimigo_atual.y + 70, font_media, alinhamento="centro")
            desenhar_texto(screen, f"Nível: {inimigo_atual.nivel}", inimigo_atual.x + inimigo_atual.width // 2, inimigo_atual.y + 90, font_pequena, alinhamento="centro")

        # Efeitos visuais de ataque
        if efeito_ataque_jogador == 1:
            pygame.draw.line(screen, WHITE, (jogador.x + jogador.width, jogador.y + jogador.height // 2), (inimigo_atual.x, inimigo_atual.y + inimigo_atual.height // 2), 3)
        if efeito_ataque_inimigo == 1:
            pygame.draw.line(screen, WHITE, (inimigo_atual.x, inimigo_atual.y + inimigo_atual.height // 2), (jogador.x, jogador.y + jogador.height // 2), 3)

        # Desenha os logs de batalha
        y_log = HEIGHT - 30
        for log in logs_batalha:
            desenhar_texto(screen, log, 20, y_log, font_pequena)
            y_log -= 20

        # Mensagens de estado do jogo
        if estado_jogo == "exploracao":
            desenhar_texto(screen, "Pressione ESPAÇO para EXPLORAR (encontrar um inimigo)", WIDTH // 2, HEIGHT // 2, font_grande, WHITE, alinhamento="centro")
        elif estado_jogo == "fim_de_jogo":
            desenhar_texto(screen, "FIM DE JOGO! Pressione ESPAÇO para RECOMEÇAR", WIDTH // 2, HEIGHT // 2, font_grande, RED, alinhamento="centro")
        elif estado_jogo == "batalha" and not jogador.esta_vivo():
             desenhar_texto(screen, "VOCÊ FOI DERROTADO! Pressione ESPAÇO para RECOMEÇAR", WIDTH // 2, HEIGHT // 2, font_grande, RED, alinhamento="centro")
        elif estado_jogo == "batalha" and not inimigo_atual.esta_vivo():
             desenhar_texto(screen, "INIMIGO DERROTADO! Pressione ESPAÇO para EXPLORAR", WIDTH // 2, HEIGHT // 2, font_grande, GREEN, alinhamento="centro")

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    nome_jogador = input("Digite o nome do seu herói: ")
    main(nome_jogador)


