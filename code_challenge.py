# -*- coding: utf-8 -*-
"""
code_challenge.py
------------------
CodeChallenge: Bir Hacker'ın barındırdığı hatalı kodu "savaş alanına" çeviren
sınıf. Oyuncudan iki şey ister:
    1) Hangi satır(lar)da hata olduğunu seçmesi (bug_start_line / bug_end_line)
    2) O satır(lar) için önerdiği düzeltmeyi yazması (fixed_code ile eşleşmeli)

check_answer() metodu, bu ikisini normalize ederek (boşluk/girinti farklarına
toleranslı şekilde) karşılaştırır ve sonucu bir ChallengeResult olarak döner.

Neden ayrı bir sınıf? Çünkü "doğrulama mantığı" ileride değişebilir
(örn. gerçek bir Python/JS parser'a bağlanmak, unit test çalıştırmak vb.)
Bu sınıfı değiştirmek, Hacker veya oyunun geri kalanını etkilemez.
"""

from __future__ import annotations
from dataclasses import dataclass
from systems.hacker import Hacker


@dataclass
class ChallengeResult:
    success: bool
    message: str
    explanation: str = ""


class CodeChallenge:
    def __init__(self, hacker: Hacker):
        self.hacker = hacker
        self.lines = hacker.get_code_lines()

    # ------------------------------------------------------------------
    # Yardımcı: metni karşılaştırmaya uygun hale getirir (normalize eder)
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize(text: str) -> str:
        """
        Karşılaştırmayı, öğrenciyi gereksiz yere boşluk/girinti hatasından
        dolayı cezalandırmayacak şekilde toleranslı yapar:
        - Baştaki/sondaki boşlukları siler
        - Ardışık boşlukları teke indirir
        - Tamamen boşsa "" döner (silme durumunu kontrol etmek için)
        """
        return " ".join(text.split())

    # ------------------------------------------------------------------
    # 1) Oyuncu hangi satırları seçti? Doğru mu?
    # ------------------------------------------------------------------
    def is_correct_line_selection(self, selected_start: int, selected_end: int) -> bool:
        return (
            selected_start == self.hacker.bug_start_line
            and selected_end == self.hacker.bug_end_line
        )

    # ------------------------------------------------------------------
    # 2) Oyuncunun önerdiği düzeltme, beklenen düzeltmeyle eşleşiyor mu?
    # ------------------------------------------------------------------
    def is_correct_fix(self, proposed_fix: str) -> bool:
        if self.hacker.fix_type == "delete":
            # Silme durumunda oyuncunun önerisi boş olmalı (satırı sildi demektir)
            return self._normalize(proposed_fix) == ""
        return self._normalize(proposed_fix) == self._normalize(self.hacker.fixed_code)

    # ------------------------------------------------------------------
    # Ana giriş noktası: GameManager bunu çağırır
    # ------------------------------------------------------------------
    def check_answer(self, selected_start: int, selected_end: int, proposed_fix: str) -> ChallengeResult:
        if not self.is_correct_line_selection(selected_start, selected_end):
            return ChallengeResult(
                success=False,
                message=(
                    f"Yanlis satir! {self.hacker.name} sana gulumsuyor: "
                    f"'Hata orada degil, tekrar bak.'"
                ),
            )

        if not self.is_correct_fix(proposed_fix):
            return ChallengeResult(
                success=False,
                message="Satiri dogru buldun ama duzeltme yanlis. Tekrar dene!",
            )

        return ChallengeResult(
            success=True,
            message=f"{self.hacker.name} sistemden atildi!",
            explanation=self.hacker.explanation,
        )

    # ------------------------------------------------------------------
    # Oyuncuya kolaylık için: düzeltilmiş tam kodu üretir (ekranda gösterim için)
    # ------------------------------------------------------------------
    def build_fixed_full_code(self) -> str:
        lines = list(self.lines)
        start_idx = self.hacker.bug_start_line - 1  # 0-indeksli
        end_idx = self.hacker.bug_end_line - 1

        if self.hacker.fix_type == "replace":
            new_lines = self.hacker.fixed_code.split("\n")
            lines[start_idx:end_idx + 1] = new_lines
        elif self.hacker.fix_type == "insert_after":
            new_lines = self.hacker.fixed_code.split("\n")
            lines[end_idx + 1:end_idx + 1] = new_lines
        elif self.hacker.fix_type == "delete":
            del lines[start_idx:end_idx + 1]

        return "\n".join(lines)
