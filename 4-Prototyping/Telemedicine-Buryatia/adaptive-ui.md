## Уникальное решение: Градиентный интерфейс
- **Режим 1:** Полная версия (городские районы)
- **Режим 2:** Облегченная версия (сельские районы) 
- **Режим 3:** Текстовая версия (спутниковая связь)

@startuml
# В 3-Modelling-And-Design/Telemedicine-Buryatia/buryat-chatbot.puml

actor "Patient" as P
actor "Doctor" as D
component "Buryat NLP Engine" as NLP
database "Traditional Medicine KB" as TM

P -> NLP: Говорит на бурятском
NLP -> TM: Ищет традиционные аналоги
TM -> D: Предлагает интегрированное лечение
D -> P: Рекомендация на двух языках
@enduml
