from __future__ import annotations

import re
from dataclasses import dataclass, field

from parser.models import VacancyData


@dataclass
class RelevanceResult:
    score: int
    is_relevant: bool
    reason: str = ""
    details: list[str] = field(default_factory=list)


class VacancyRelevanceScorer:
    POSITIVE_TITLE_KEYWORDS: list[tuple[int, list[str]]] = [
        (80, ["ведущий системный администратор", "главный системный администратор"]),
        (100, ["системный администратор", "system administrator", "sysadmin"]),
        (70, ["инженер технической поддержки", "support engineer", "technical support"]),
        (60, ["it специалист", "it инженер", "системный инженер", "ит специалист", "ит инженер"]),
        (50, ["сетевой инженер", "network engineer"]),
    ]
    NEGATIVE_TITLE_KEYWORDS = [
        "продавец",
        "кассир",
        "мерчендайзер",
        "официант",
        "бариста",
        "администратор кофейни",
        "администратор клиники",
        "администратор салона",
        "управляющий салоном",
        "офис менеджер",
        "офис-менеджер",
        "секретарь",
        "бизнес ассистент",
        "бизнес-ассистент",
    ]
    TECH_SKILLS = [
        "Linux",
        "Windows Server",
        "Active Directory",
        "TCP/IP",
        "DNS",
        "DHCP",
        "Mikrotik",
        "Cisco",
        "VMware",
        "Hyper-V",
        "Docker",
        "Git",
        "PowerShell",
        "Bash",
        "Zabbix",
        "Grafana",
    ]
    TEXT_KEYWORDS = [
        "обслуживание серверов",
        "администрирование серверов",
        "техническая поддержка",
        "сетевое оборудование",
        "Active Directory",
        "групповые политики",
        "виртуализация",
        "резервное копирование",
    ]

    def score(self, vacancy: VacancyData, minimum_score: int = 50) -> RelevanceResult:
        title = self._normalize(vacancy.title)
        text = "\n".join(
            [
                vacancy.title,
                vacancy.full_text,
                " ".join(vacancy.key_skills),
                " ".join(vacancy.responsibilities),
                " ".join(vacancy.requirements),
            ]
        )
        score = 0
        details: list[str] = []

        negative = self._first_match(title, self.NEGATIVE_TITLE_KEYWORDS)
        if negative:
            return RelevanceResult(
                score=-100,
                is_relevant=False,
                reason="отрицательное ключевое слово",
                details=[f"Название содержит: {negative}"],
            )

        title_points = 0
        title_match = ""
        for points, keywords in self.POSITIVE_TITLE_KEYWORDS:
            matched = self._first_match(title, keywords)
            if matched:
                title_points = points
                title_match = matched
                break
        if title_points:
            score += title_points
            details.append(f"Название: {title_match} +{title_points}")

        skill_hits = self._matched_keywords(text, self.TECH_SKILLS)
        if skill_hits:
            points = len(skill_hits) * 10
            score += points
            details.append(f"Технические навыки: {', '.join(skill_hits)} +{points}")

        text_hits = self._matched_keywords(text, self.TEXT_KEYWORDS)
        if text_hits:
            points = len(text_hits) * 15
            score += points
            details.append(f"Текст вакансии: {', '.join(text_hits)} +{points}")

        reason = ""
        if not skill_hits and not text_hits and title_points < minimum_score:
            reason = "отсутствуют технические навыки"
        elif score < minimum_score:
            reason = f"релевантность ниже порога {minimum_score}"

        return RelevanceResult(score=score, is_relevant=score >= minimum_score and not reason, reason=reason, details=details)

    def apply(self, vacancy: VacancyData, minimum_score: int = 50) -> VacancyData:
        result = self.score(vacancy, minimum_score)
        vacancy.relevance_score = result.score
        vacancy.is_relevant = result.is_relevant
        vacancy.exclusion_reason = result.reason
        vacancy.relevance_details = result.details
        return vacancy

    def _first_match(self, text: str, keywords: list[str]) -> str:
        for keyword in keywords:
            if re.search(self._keyword_pattern(keyword), text, flags=re.I):
                return keyword
        return ""

    def _matched_keywords(self, text: str, keywords: list[str]) -> list[str]:
        found = []
        for keyword in keywords:
            if re.search(self._keyword_pattern(keyword), text, flags=re.I):
                found.append(keyword)
        return found

    def _keyword_pattern(self, keyword: str) -> str:
        escaped = re.escape(keyword)
        return rf"(?<![A-Za-zА-Яа-я0-9]){escaped}(?![A-Za-zА-Яа-я0-9])"

    def _normalize(self, value: str) -> str:
        return re.sub(r"\s+", " ", value or "").strip().lower()
