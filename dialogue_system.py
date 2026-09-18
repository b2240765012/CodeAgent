# -*- coding: utf-8 -*-
"""
dialogue_system.py
-------------------
DialogueSystem: Ekranda gösterilecek diyalog kutucuklarını sırayla yöneten
basit bir durum makinesi (state machine).

Üç temel diyalog akışı vardır:
    1) intro    -> Hacker ile karşılaşma (tehdit/alay)
    2) success  -> Hata başarıyla düzeltildiğinde (yenilgi repliği + açıklama)
    3) ending   -> Sadece son hacker'da: "Karanlık Tarafa Katıl / Reddet" seçimi

Bu sınıf pygame'e bağımlı DEĞİLDİR; sadece durumu tutar. Çizim işini main.py
üstlenir. Böylece diyalog mantığını konsolda da, farklı bir arayüzde de
(örn. web) tekrar kullanabiliriz.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Callable
from systems.hacker import Hacker


class DialogueState(Enum):
    IDLE = auto()
    INTRO = auto()
    CHALLENGE = auto()   # Kod savaşı ekranı aktif, diyalog kapalı
    SUCCESS = auto()
    ENDING_CHOICE = auto()
    ENDING_RESULT = auto()


@dataclass
class DialogueBox:
    speaker: str
    text: str


class DialogueSystem:
    def __init__(self):
        self.state: DialogueState = DialogueState.IDLE
        self.current_box: Optional[DialogueBox] = None
        # Oyuncunun final'de verdiği kararı burada saklarız
        self.player_joined_dark_side: Optional[bool] = None

    # ------------------------------------------------------------------
    def show_intro(self, hacker: Hacker) -> DialogueBox:
        self.state = DialogueState.INTRO
        self.current_box = DialogueBox(speaker=hacker.name, text=hacker.intro_dialogue)
        return self.current_box

    def start_challenge(self) -> None:
        """Oyuncu 'Devam' dediğinde diyalog kutusunu kapatıp kod ekranına geçer."""
        self.state = DialogueState.CHALLENGE
        self.current_box = None

    def show_success(self, hacker: Hacker, explanation: str) -> DialogueBox:
        self.state = DialogueState.SUCCESS
        text = f"{hacker.success_dialogue}\n\n[Ogretici Not] {explanation}"
        self.current_box = DialogueBox(speaker=hacker.name, text=text)
        return self.current_box

    # ------------------------------------------------------------------
    # FİNAL: Çoklu son seçimi
    # ------------------------------------------------------------------
    def show_ending_choice(self, hacker: Hacker) -> DialogueBox:
        assert hacker.is_final, "Bu metod sadece final hacker icin cagrilmali!"
        self.state = DialogueState.ENDING_CHOICE
        self.current_box = DialogueBox(speaker=hacker.name, text=hacker.choice_prompt)
        return self.current_box

    def resolve_ending(self, hacker: Hacker, joined_dark_side: bool) -> DialogueBox:
        """
        Oyuncunun final seçimini işler ve ilgili bitiş diyaloğunu döner.
        joined_dark_side=True  -> Kötü Son
        joined_dark_side=False -> İyi Son ("Sistem Kurtarıldı")
        """
        self.player_joined_dark_side = joined_dark_side
        self.state = DialogueState.ENDING_RESULT
        text = hacker.bad_ending_dialogue if joined_dark_side else hacker.good_ending_dialogue
        speaker = "KARANLIK SON" if joined_dark_side else "SISTEM KURTARILDI"
        self.current_box = DialogueBox(speaker=speaker, text=text)
        return self.current_box

    # ------------------------------------------------------------------
    def clear(self) -> None:
        self.state = DialogueState.IDLE
        self.current_box = None
