# -*- coding: utf-8 -*-
"""
hacker.py
---------
Hacker sınıfı: Oyundaki her bir düşmanı (hacker'ı) temsil eden veri modeli.
JSON'daki bir kayıttan (dict) bir Hacker nesnesi üretir.

Bu sınıf BİLİNÇLİ olarak "aptal" tutulmuştur: kendi mantık kontrolünü yapmaz,
sadece verisini taşır. Doğrulama işini CodeChallenge sınıfına devrederiz
(Single Responsibility Principle - Tek Sorumluluk İlkesi).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Hacker:
    # --- Kimlik / tema bilgisi ---
    id: int
    chapter: str            # Hangi bölümde (Script Kiddies, Code Breakers, ...)
    name: str
    company: str
    language: str
    error_type: str

    # --- Diyaloglar ---
    intro_dialogue: str
    success_dialogue: str

    # --- Kod meydan okuması (challenge) verisi ---
    buggy_code: str
    bug_start_line: int
    bug_end_line: int
    fix_type: str            # "replace" | "insert_after" | "delete"
    fixed_code: str
    explanation: str

    # --- Final hacker'a özel alanlar (diğerlerinde None/False kalır) ---
    is_final: bool = False
    choice_prompt: Optional[str] = None
    good_ending_dialogue: Optional[str] = None
    bad_ending_dialogue: Optional[str] = None

    # --- Çalışma zamanı (runtime) durumu; JSON'da tutulmaz ---
    is_defeated: bool = field(default=False, compare=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Hacker":
        """JSON'dan gelen bir dict'i Hacker nesnesine çevirir."""
        return cls(
            id=data["id"],
            chapter=data["chapter"],
            name=data["name"],
            company=data["company"],
            language=data["language"],
            error_type=data["error_type"],
            intro_dialogue=data["intro_dialogue"],
            success_dialogue=data["success_dialogue"],
            buggy_code=data["buggy_code"],
            bug_start_line=data["bug_start_line"],
            bug_end_line=data["bug_end_line"],
            fix_type=data["fix_type"],
            fixed_code=data["fixed_code"],
            explanation=data["explanation"],
            is_final=data.get("is_final", False),
            choice_prompt=data.get("choice_prompt"),
            good_ending_dialogue=data.get("good_ending_dialogue"),
            bad_ending_dialogue=data.get("bad_ending_dialogue"),
        )

    def get_code_lines(self) -> list[str]:
        """Hatalı kodu satır satır bir listeye böler (arayüzde numaralandırmak için)."""
        return self.buggy_code.split("\n")

    def mark_defeated(self) -> None:
        self.is_defeated = True

    def __repr__(self) -> str:
        return f"<Hacker #{self.id} '{self.name}' ({self.company}) - {self.language}>"
