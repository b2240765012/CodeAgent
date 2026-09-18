# -*- coding: utf-8 -*-
"""
game_manager.py
-----------------
GameManager: Oyunun "beyni". JSON'dan tüm hacker'ları yükler, hangi hacker'ın
sırada olduğunu takip eder, CodeChallenge ve DialogueSystem'i birbirine bağlar.

main.py (pygame döngüsü) SADECE bu sınıfla konuşur; JSON'u veya diğer
sistemleri doğrudan bilmesine gerek kalmaz. Bu, arayüzü (pygame yerine
başka bir motor) değiştirmek istersek GameManager'ı olduğu gibi
tekrar kullanabilmemizi sağlar.
"""

from __future__ import annotations
import json
import os
from enum import Enum, auto
from typing import Optional

from systems.hacker import Hacker
from systems.code_challenge import CodeChallenge, ChallengeResult
from systems.dialogue_system import DialogueSystem, DialogueState


class GamePhase(Enum):
    MENU = auto()
    INTRO_DIALOGUE = auto()
    CODE_BATTLE = auto()
    SUCCESS_DIALOGUE = auto()
    FINAL_CHOICE = auto()
    ENDING = auto()
    GAME_COMPLETE_MENU = auto()  # tüm hackerlar bitince ana menüye dönüş ekranı


class GameManager:
    def __init__(self, data_path: Optional[str] = None):
        if data_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_dir, "data", "hackers.json")

        self.hackers: list[Hacker] = self._load_hackers(data_path)
        self.current_index: int = 0
        self.dialogue = DialogueSystem()
        self.phase: GamePhase = GamePhase.MENU
        self.active_challenge: Optional[CodeChallenge] = None
        self.score: int = 0
        self.attempts_this_hacker: int = 0

    # ------------------------------------------------------------------
    @staticmethod
    def _load_hackers(path: str) -> list[Hacker]:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        hackers = [Hacker.from_dict(item) for item in raw]
        hackers.sort(key=lambda h: h.id)  # zorluk sirasina gore garanti sirala
        return hackers

    # ------------------------------------------------------------------
    @property
    def current_hacker(self) -> Hacker:
        return self.hackers[self.current_index]

    @property
    def total_hackers(self) -> int:
        return len(self.hackers)

    @property
    def is_last_hacker(self) -> bool:
        return self.current_index == self.total_hackers - 1

    # ------------------------------------------------------------------
    # OYUN AKIŞI
    # ------------------------------------------------------------------
    def start_game(self) -> None:
        self.current_index = 0
        self.score = 0
        self._begin_current_hacker_encounter()

    def _begin_current_hacker_encounter(self) -> None:
        """Yeni hacker ile karşılaşmayı başlatır: intro diyaloğunu gösterir."""
        hacker = self.current_hacker
        self.attempts_this_hacker = 0
        self.dialogue.show_intro(hacker)
        self.phase = GamePhase.INTRO_DIALOGUE

    def player_confirms_intro(self) -> None:
        """Oyuncu intro diyaloğunda 'Devam Et / Savaş' dediğinde çağrılır."""
        self.dialogue.start_challenge()
        self.active_challenge = CodeChallenge(self.current_hacker)
        self.phase = GamePhase.CODE_BATTLE

    # ------------------------------------------------------------------
    # KOD SAVAŞI
    # ------------------------------------------------------------------
    def submit_fix(self, selected_start: int, selected_end: int, proposed_fix: str) -> ChallengeResult:
        """
        Oyuncu 'Duzelt' butonuna bastığında main.py bunu çağırır.
        Sonuca göre otomatik olarak success diyaloğuna veya final akışına geçer.
        """
        assert self.active_challenge is not None, "Aktif bir kod savasi yok!"
        self.attempts_this_hacker += 1

        result = self.active_challenge.check_answer(selected_start, selected_end, proposed_fix)

        if result.success:
            self.score += max(100 - (self.attempts_this_hacker - 1) * 10, 10)
            self.current_hacker.mark_defeated()
            self.dialogue.show_success(self.current_hacker, result.explanation)
            self.phase = GamePhase.SUCCESS_DIALOGUE

        return result

    # ------------------------------------------------------------------
    # SUCCESS SONRASI: Sıradaki hacker'a geç ya da final'i tetikle
    # ------------------------------------------------------------------
    def player_confirms_success(self) -> None:
        hacker = self.current_hacker

        if hacker.is_final:
            # Son hacker yenildi -> "Iyi Son / Kotu Son" seçim ekranını göster
            self.dialogue.show_ending_choice(hacker)
            self.phase = GamePhase.FINAL_CHOICE
            return

        if self.is_last_hacker:
            # Guvenlik agi: is_final isaretlenmemis ama son elemansa yine bitir
            self.phase = GamePhase.GAME_COMPLETE_MENU
            return

        # Normal durum: sonraki hacker'a geç
        self.current_index += 1
        self._begin_current_hacker_encounter()

    # ------------------------------------------------------------------
    # ÇOKLU SON (MULTIPLE ENDINGS)
    # ------------------------------------------------------------------
    def player_chooses_ending(self, join_dark_side: bool) -> None:
        """
        join_dark_side=True  -> "Karanlık Tarafa Katıl" (Kötü Son)
        join_dark_side=False -> "Reddet, Dünyayı Kurtar" (İyi Son)
        """
        self.dialogue.resolve_ending(self.current_hacker, join_dark_side)
        self.phase = GamePhase.ENDING

    def finish_game(self) -> None:
        self.phase = GamePhase.GAME_COMPLETE_MENU

    # ------------------------------------------------------------------
    def progress_text(self) -> str:
        return f"{self.current_hacker.chapter} | Hacker {self.current_index + 1}/{self.total_hackers} | Skor: {self.score}"
