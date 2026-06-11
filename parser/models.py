from dataclasses import dataclass, field


@dataclass
class VacancyData:
    url: str
    vacancy_id: str = ""
    title: str = ""
    company: str = ""
    city: str = ""

    # Структурированная зарплата (из API)
    salary_from: int | None = None
    salary_to: int | None = None
    salary_currency: str = ""
    salary_gross: bool = False

    # Форматированная строка для отображения
    salary: str = ""

    # ID для дедупликации и группировки
    employer_id: str = ""
    area_id: str = ""

    full_text: str = ""
    key_skills: list[str] = field(default_factory=list)
    responsibilities: list[str] = field(default_factory=list)
    requirements: list[str] = field(default_factory=list)
    skills: list[dict[str, str]] = field(default_factory=list)

    @property
    def display_name(self) -> str:
        return self.title or self.url
