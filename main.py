# -*- coding: utf-8 -*-
"""
main.py
--------
Oyunun Pygame giriş noktası. Bu dosya SADECE görsel/girdi (I/O) işleriyle
ilgilenir; oyun mantığının tamamı systems/game_manager.py içinde yaşar.

Kontroller:
    Menu ekranı      -> ENTER: Oyunu başlat
    Intro diyalog     -> ENTER: Devam et / Savaşa gir
    Kod savaşı        -> Fare ile hatalı olduğunu düşündüğün satır(lar)a tıkla
                          (birden fazla satır için SHIFT + tıkla ile aralık seç)
                          Alt kutuya düzeltmeni yaz, ENTER ile gönder.
    Success diyalog    -> ENTER: Sıradaki hacker'a geç
    Final seçim        -> Y: Karanlık tarafa katıl (Kötü Son)
                          N: Reddet, dünyayı kurtar (İyi Son)
    Herhangi bir yerde -> ESC: Çıkış

Görsel tema: Matrix/terminal tarzı (siyah zemin, yeşil fosfor yazı) -
bu tema hem atmosfere uyuyor hem de çizim yükünü minimumda tutuyor.
"""

import sys
import textwrap
import pygame

from systems.game_manager import GameManager, GamePhase

# ------------------------------------------------------------------
# SABİTLER (renkler, boyutlar, tema)
# ------------------------------------------------------------------
SCREEN_W, SCREEN_H = 1000, 700
BG_COLOR = (5, 10, 5)
GREEN = (0, 255, 70)
DIM_GREEN = (0, 120, 40)
RED = (255, 60, 60)
WHITE = (230, 230, 230)
YELLOW = (255, 210, 0)
LINE_HEIGHT = 26
FONT_NAME = "consolas"  # monospace -> kod gorunumu icin sart


class HackerGameApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("SYSTEM BREACH // Hacker ve Sistem Guvenligi")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()

        self.font_small = pygame.font.SysFont(FONT_NAME, 16)
        self.font_mid = pygame.font.SysFont(FONT_NAME, 20)
        self.font_big = pygame.font.SysFont(FONT_NAME, 32, bold=True)

        self.gm = GameManager()

        # Kod savaşı ekranı için geçici durum
        self.selected_start = None
        self.selected_end = None
        self.fix_input_text = ""
        self.feedback_message = ""
        self.feedback_color = GREEN

    # ------------------------------------------------------------------
    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                running = self._handle_event(event)
                if not running:
                    break
            self._draw()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

    # ------------------------------------------------------------------
    # OLAY YÖNETİMİ (klavye / fare)
    # ------------------------------------------------------------------
    def _handle_event(self, event) -> bool:
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return False

        phase = self.gm.phase

        if phase == GamePhase.MENU:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.gm.start_game()

        elif phase == GamePhase.INTRO_DIALOGUE:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.gm.player_confirms_intro()
                self._reset_battle_state()

        elif phase == GamePhase.CODE_BATTLE:
            self._handle_battle_event(event)

        elif phase == GamePhase.SUCCESS_DIALOGUE:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.gm.player_confirms_success()

        elif phase == GamePhase.FINAL_CHOICE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    self.gm.player_chooses_ending(join_dark_side=True)
                elif event.key == pygame.K_n:
                    self.gm.player_chooses_ending(join_dark_side=False)

        elif phase == GamePhase.ENDING:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.gm.finish_game()

        elif phase == GamePhase.GAME_COMPLETE_MENU:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.gm = GameManager()  # oyunu sıfırdan başlat

        return True

    def _handle_battle_event(self, event) -> None:
        code_lines = self.gm.current_hacker.get_code_lines()

        # Fare ile satır seçimi
        if event.type == pygame.MOUSEBUTTONDOWN:
            line_idx = self._line_index_from_mouse(event.pos, len(code_lines))
            if line_idx is not None:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT and self.selected_start is not None:
                    lo, hi = sorted((self.selected_start, line_idx + 1))
                    self.selected_start, self.selected_end = lo, hi
                else:
                    self.selected_start = line_idx + 1
                    self.selected_end = line_idx + 1

        # Klavye ile düzeltme yazımı
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._submit_current_fix()
            elif event.key == pygame.K_BACKSPACE:
                self.fix_input_text = self.fix_input_text[:-1]
            elif event.key == pygame.K_TAB:
                self.fix_input_text += "    "
            else:
                if event.unicode and event.unicode.isprintable():
                    self.fix_input_text += event.unicode

    def _submit_current_fix(self) -> None:
        if self.selected_start is None:
            self.feedback_message = "Once hatali oldugunu dusundugun satira tikla!"
            self.feedback_color = YELLOW
            return

        result = self.gm.submit_fix(self.selected_start, self.selected_end, self.fix_input_text)
        self.feedback_message = result.message
        self.feedback_color = GREEN if result.success else RED
        if result.success:
            self._reset_battle_state()

    def _reset_battle_state(self) -> None:
        self.selected_start = None
        self.selected_end = None
        self.fix_input_text = ""
        self.feedback_message = ""

    def _line_index_from_mouse(self, pos, total_lines):
        x, y = pos
        code_area_top = 120
        if x < 40 or x > SCREEN_W - 40 or y < code_area_top:
            return None
        idx = (y - code_area_top) // LINE_HEIGHT
        if 0 <= idx < total_lines:
            return idx
        return None

    # ------------------------------------------------------------------
    # ÇİZİM
    # ------------------------------------------------------------------
    def _draw(self) -> None:
        self.screen.fill(BG_COLOR)
        phase = self.gm.phase

        if phase == GamePhase.MENU:
            self._draw_menu()
        elif phase == GamePhase.INTRO_DIALOGUE:
            self._draw_dialogue_screen()
        elif phase == GamePhase.CODE_BATTLE:
            self._draw_battle_screen()
        elif phase == GamePhase.SUCCESS_DIALOGUE:
            self._draw_dialogue_screen()
        elif phase == GamePhase.FINAL_CHOICE:
            self._draw_dialogue_screen(choice_mode=True)
        elif phase == GamePhase.ENDING:
            self._draw_dialogue_screen()
        elif phase == GamePhase.GAME_COMPLETE_MENU:
            self._draw_complete_screen()

        pygame.display.flip()

    def _draw_menu(self) -> None:
        title = self.font_big.render("SYSTEM BREACH", True, GREEN)
        subtitle = self.font_mid.render("Hacker ve Sistem Guvenligi", True, DIM_GREEN)
        hint = self.font_small.render("[ENTER] ile baslat   |   [ESC] cikis", True, WHITE)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 260))
        self.screen.blit(subtitle, (SCREEN_W // 2 - subtitle.get_width() // 2, 310))
        self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, 400))

    def _draw_complete_screen(self) -> None:
        text = self.font_big.render("TEBRIKLER - TUM SEVIYELER TAMAMLANDI", True, GREEN)
        self.screen.blit(text, (SCREEN_W // 2 - text.get_width() // 2, 300))
        hint = self.font_small.render("[ENTER] Yeniden basla", True, WHITE)
        self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, 360))

    def _draw_dialogue_screen(self, choice_mode: bool = False) -> None:
        hacker = self.gm.current_hacker
        box = self.gm.dialogue.current_box

        header = self.font_mid.render(self.gm.progress_text(), True, DIM_GREEN)
        self.screen.blit(header, (30, 20))

        name_text = self.font_big.render(f"{box.speaker}", True, YELLOW if not choice_mode else RED)
        self.screen.blit(name_text, (30, 70))

        company_text = self.font_small.render(f"[{hacker.company} - {hacker.language}]", True, DIM_GREEN)
        self.screen.blit(company_text, (30, 115))

        # Diyalog kutusu
        box_rect = pygame.Rect(30, 160, SCREEN_W - 60, 400)
        pygame.draw.rect(self.screen, (0, 20, 0), box_rect)
        pygame.draw.rect(self.screen, GREEN, box_rect, 2)

        wrapped = []
        for paragraph in box.text.split("\n"):
            wrapped.extend(textwrap.wrap(paragraph, width=90) or [""])

        for i, line in enumerate(wrapped):
            rendered = self.font_small.render(line, True, WHITE)
            self.screen.blit(rendered, (50, 180 + i * 22))

        if choice_mode:
            hint = self.font_mid.render("[Y] Karanlik tarafa katil   |   [N] Reddet, dunyayi kurtar", True, GREEN)
        else:
            hint = self.font_small.render("[ENTER] Devam et", True, DIM_GREEN)
        self.screen.blit(hint, (30, SCREEN_H - 50))

    def _draw_battle_screen(self) -> None:
        hacker = self.gm.current_hacker
        header = self.font_mid.render(
            f"{self.gm.progress_text()} | HATA TURU: {hacker.error_type}", True, DIM_GREEN
        )
        self.screen.blit(header, (30, 20))

        instructions = self.font_small.render(
            "Hatali satira tikla (SHIFT+tikla ile aralik sec), alt kutuya duzeltmeni yaz, ENTER'a bas.",
            True, WHITE,
        )
        self.screen.blit(instructions, (30, 55))

        # Kod alanı
        code_lines = hacker.get_code_lines()
        top = 120
        for i, line in enumerate(code_lines):
            line_no = i + 1
            is_selected = (
                self.selected_start is not None
                and self.selected_start <= line_no <= self.selected_end
            )
            color = YELLOW if is_selected else GREEN
            prefix = f"{line_no:>3} | "
            rendered = self.font_small.render(prefix + line, True, color)
            if is_selected:
                highlight_rect = pygame.Rect(35, top + i * LINE_HEIGHT - 2, SCREEN_W - 70, LINE_HEIGHT - 2)
                pygame.draw.rect(self.screen, (30, 30, 0), highlight_rect)
            self.screen.blit(rendered, (40, top + i * LINE_HEIGHT))

        # Düzeltme giriş kutusu
        input_y = SCREEN_H - 120
        input_rect = pygame.Rect(30, input_y, SCREEN_W - 60, 40)
        pygame.draw.rect(self.screen, (0, 20, 0), input_rect)
        pygame.draw.rect(self.screen, GREEN, input_rect, 2)
        input_label = self.font_small.render("Duzeltme:", True, DIM_GREEN)
        self.screen.blit(input_label, (30, input_y - 20))
        typed = self.font_small.render(self.fix_input_text + "_", True, WHITE)
        self.screen.blit(typed, (40, input_y + 10))

        # Geri bildirim mesajı
        if self.feedback_message:
            fb = self.font_small.render(self.feedback_message, True, self.feedback_color)
            self.screen.blit(fb, (30, SCREEN_H - 60))


if __name__ == "__main__":
    HackerGameApp().run()
