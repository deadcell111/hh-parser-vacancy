from __future__ import annotations

import re
from collections import Counter

import pandas as pd

from analyzer.skill_catalog import CERTIFICATES, SKILL_CATALOG, SOFT_SKILLS
from parser.models import VacancyData


class VacancyAnalyzer:
    RESPONSIBILITY_HEADERS = [
        "Обязанности", "Что предстоит делать", "Ваши задачи", "Задачи", "Чем предстоит заниматься",
        "Что нужно делать", "Функции", "Основные задачи", "Ключевые задачи", "Вам предстоит",
    ]
    REQUIREMENT_HEADERS = [
        "Требования", "Мы ожидаем", "Наш кандидат", "Что мы ждём", "Что мы ждем", "Будет плюсом",
        "Требуется", "Необходимо", "Ожидания", "Квалификация", "Мы ждем от тебя",
    ]
    STOP_HEADERS = [
        "Условия", "Мы предлагаем", "Преимущества", "О компании", "График", "Навыки", "Ключевые навыки",
        "Заработная плата", "Почему мы", "Этапы отбора", "Контакты",
    ]
    BAD_ITEM_FRAGMENTS = [
        "мы ждем", "мы ждём", "наш кандидат", "будет преимуществом", "будет плюсом",
        "понимание принципов", "поддержкой и администри",
    ]
    RESPONSIBILITY_HINTS = [
        "администр", "поддерж", "настрой", "монитор", "резерв", "обслуж", "сопровожд", "управлен",
        "установ", "обнов", "диагност", "решен", "работа с", "контроль", "разверт",
    ]
    REQUIREMENT_HINTS = [
        "опыт", "знание", "навык", "умение", "понимание", "владение", "работы с", "администрирования",
        "настройки", "эксплуатации", "сертификат",
    ]
    NORMALIZATION_MAP = {
        "TCP": "TCP/IP", "IP": "TCP/IP", "IPv4": "TCP/IP", "IPv6": "TCP/IP",
        "Ubuntu": "Linux", "Debian": "Linux", "CentOS": "Linux", "RHEL": "Linux", "Red Hat": "Linux",
        "Rocky Linux": "Linux", "AlmaLinux": "Linux", "Fedora": "Linux",
        "ESXi": "VMware", "VMware ESXi": "VMware", "vSphere": "VMware", "VMware vSphere": "VMware",
        "vCenter": "VMware",
        "GitHub": "Git", "GitLab": "Git", "Bitbucket": "Git",
        "AD": "Active Directory", "GPO": "Active Directory", "Group Policy": "Active Directory",
        "групповые политики": "Active Directory",
        "K8s": "Kubernetes", "Kubectl": "Kubernetes",
        "PowerShell Core": "PowerShell",
        "Windows": "Windows Server",
        "MSSQL Server": "SQL Server", "MS SQL": "SQL Server",
    }

    def analyze(self, vacancy: VacancyData) -> VacancyData:
        vacancy.responsibilities = self.extract_section_items(vacancy.full_text, self.RESPONSIBILITY_HEADERS, "duty")
        vacancy.requirements = self.extract_section_items(vacancy.full_text, self.REQUIREMENT_HEADERS, "requirement")
        skill_text = "\n".join(
            [
                "\n".join(vacancy.key_skills),
                "\n".join(vacancy.requirements),
                "\n".join(vacancy.responsibilities),
            ]
        )
        vacancy.skills = self._merge_skills(vacancy.skills, self.extract_skills(skill_text))
        return vacancy

    def extract_section_items(self, text: str, headers: list[str], item_type: str = "generic") -> list[str]:
        lines = [line.strip(" -•\t") for line in re.split(r"[\n\r]+", text or "") if line.strip()]
        items: list[str] = []
        collecting = False

        for line in lines:
            normalized = self._normalize_text(line).rstrip(":")
            if self._contains_header(normalized, headers):
                collecting = True
                remainder = self._text_after_header(line, headers)
                if remainder:
                    items.extend(self._split_items(remainder))
                continue
            if collecting and self._looks_like_header(normalized):
                if self._is_noise_heading(normalized):
                    continue
                break
            if collecting:
                items.extend(self._split_items(line))

        cleaned = [self._clean_item(item) for item in items]
        return self._unique([item for item in cleaned if self._is_meaningful_item(item, item_type)])[:300]

    def extract_skills(self, text: str) -> list[dict[str, str]]:
        found: list[dict[str, str]] = []
        for category, skills in SKILL_CATALOG.items():
            found.extend(self._find_catalog(text, skills, "Технические навыки"))
        found.extend(self._find_catalog(text, self._tool_catalog(), "Инструменты"))
        found.extend(self._find_catalog(text, SOFT_SKILLS, "Soft Skills"))
        found.extend(self._find_catalog(text, CERTIFICATES, "Сертификаты"))
        return found

    def build_market_statistics(self, vacancies: list[VacancyData], limit: int = 100) -> dict[str, pd.DataFrame]:
        return {
            "skills": self._counter_frame(vacancies, "Навык", self._skills_per_vacancy(vacancies), limit),
            "duties": self._counter_frame(vacancies, "Обязанность", [v.responsibilities for v in vacancies], limit),
            "requirements": self._counter_frame(vacancies, "Требование", [v.requirements for v in vacancies], limit),
        }

    def build_skill_stats(self, vacancies: list[VacancyData]) -> pd.DataFrame:
        return self.build_market_statistics(vacancies)["skills"]

    def _skills_per_vacancy(self, vacancies: list[VacancyData]) -> list[list[str]]:
        return [[skill["name"] for skill in vacancy.skills] for vacancy in vacancies]

    def _counter_frame(self, vacancies: list[VacancyData], name_column: str, values_by_vacancy: list[list[str]], limit: int) -> pd.DataFrame:
        total = len(vacancies)
        counter: Counter[str] = Counter()
        for values in values_by_vacancy:
            counter.update(set(values))
        rows = [
            {
                name_column: item,
                "Количество упоминаний": count,
                "Процент встречаемости": f"{round(count / total * 100)}%" if total else "0%",
            }
            for item, count in counter.most_common(limit)
        ]
        return pd.DataFrame(rows)

    def _find_catalog(self, text: str, catalog: list[str], category: str) -> list[dict[str, str]]:
        result = []
        for item in catalog:
            if re.search(self._skill_pattern(item), text or "", flags=re.I):
                result.append({"name": self._canonical_skill(item), "category": category})
        return result

    def _canonical_skill(self, skill: str) -> str:
        value = skill.strip()
        value = re.sub(r"\s+administration$", "", value, flags=re.I)
        value = re.sub(r"\s+automation$", "", value, flags=re.I)
        value = re.sub(r"\s+deployment$", "", value, flags=re.I)
        value = re.sub(r"\s+monitoring$", "", value, flags=re.I)
        value = re.sub(r"\s+troubleshooting$", "", value, flags=re.I)
        value = re.sub(r"^администрирование\s+", "", value, flags=re.I)
        return self.NORMALIZATION_MAP.get(value, value)

    def _skill_pattern(self, skill: str) -> str:
        escaped = re.escape(skill)
        return rf"(?<![A-Za-zА-Яа-я0-9]){escaped}(?![A-Za-zА-Яа-я0-9])"

    def _merge_skills(self, existing: list[dict[str, str]], detected: list[dict[str, str]]) -> list[dict[str, str]]:
        merged: dict[str, dict[str, str]] = {}
        priority = {"Технические навыки": 4, "Инструменты": 3, "Сертификаты": 2, "Soft Skills": 1, "Ключевые навыки": 0}
        for skill in existing + detected:
            name = self._canonical_skill(skill.get("name", ""))
            if not name:
                continue
            category = skill.get("category", "Технические навыки")
            key = name.lower()
            if key not in merged or priority.get(category, 0) > priority.get(merged[key]["category"], 0):
                merged[key] = {"name": name, "category": category}
        return sorted(merged.values(), key=lambda row: (row["category"], row["name"].lower()))

    def _tool_catalog(self) -> list[str]:
        return [
            "Jira", "Confluence", "Postman", "DBeaver", "DataGrip", "pgAdmin", "phpMyAdmin", "Service Desk",
            "Helpdesk", "Windows Admin Center", "Portainer", "Harbor", "Nexus", "Artifactory", "Sentry",
        ]

    def _contains_header(self, normalized_line: str, headers: list[str]) -> bool:
        for header in headers:
            header = header.lower()
            if normalized_line == header or normalized_line.startswith(header + ":"):
                return True
        return False

    def _text_after_header(self, line: str, headers: list[str]) -> str:
        for header in headers:
            match = re.search(re.escape(header) + r"\s*:?\s*(.+)$", line, flags=re.I)
            if match:
                return match.group(1).strip()
        return ""

    def _split_items(self, text: str) -> list[str]:
        rough_items = re.split(r"(?:\s*[;•]\s*|\s+-\s+|\s*\d+[.)]\s+)", text)
        return [item.strip(" -•.;:") for item in rough_items if item.strip(" -•.;:")]

    def _looks_like_header(self, normalized_line: str) -> bool:
        return self._contains_header(normalized_line, self.RESPONSIBILITY_HEADERS + self.REQUIREMENT_HEADERS + self.STOP_HEADERS)

    def _is_noise_heading(self, normalized_line: str) -> bool:
        return any(fragment in normalized_line for fragment in self.BAD_ITEM_FRAGMENTS)

    def _clean_item(self, item: str) -> str:
        item = re.sub(r"\s+", " ", item or "").strip(" -•.;:")
        item = re.sub(r"^(мы ждем от тебя|мы ждём от тебя|мы ожидаем|наш кандидат|будет преимуществом|будет плюсом)\s*:?\s*", "", item, flags=re.I)
        return item.strip(" -•.;:")

    def _is_meaningful_item(self, item: str, item_type: str) -> bool:
        normalized = self._normalize_text(item)
        if not (12 <= len(item) <= 260) or len(item.split()) < 2:
            return False
        if any(fragment in normalized for fragment in self.BAD_ITEM_FRAGMENTS):
            return False
        if self._looks_like_header(normalized):
            return False
        if item_type == "duty":
            return any(hint in normalized for hint in self.RESPONSIBILITY_HINTS)
        if item_type == "requirement":
            return any(hint in normalized for hint in self.REQUIREMENT_HINTS)
        return True

    def _unique(self, values: list[str]) -> list[str]:
        seen = set()
        result = []
        for value in values:
            key = self._normalize_text(value)
            if key not in seen:
                seen.add(key)
                result.append(value)
        return result

    def _normalize_text(self, value: str) -> str:
        return re.sub(r"\s+", " ", value or "").strip().lower()
