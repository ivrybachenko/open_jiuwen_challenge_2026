# Источники обзора 0005

Все ссылки открываются без подписки: arXiv. Полные тексты в репозиторий не
копировались.

## Включённые (64)

| ID | Источник | Год | Подход | Данные и домен | Метрика | Результат | Ограничение |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | Erol et al. [Cost-of-Pass](https://arxiv.org/abs/2504.13359) | 2025 | экономическая метрика стоимости правильного ответа | 3 класса задач, набор моделей | ожидаемая денежная стоимость правильного ответа | лёгкие модели выгодны для базовых задач, крупные — для знаний, reasoning — для сложных; majority voting и self-refinement редко оправдывают цену; TALE-EP перспективен | доллары, а не веса токенов; нет кодовых агентов |
| S02 | Wang et al. [Efficient Agents](https://arxiv.org/abs/2508.02694) | 2025 | упрощение агентской архитектуры под cost-of-pass | GAIA | cost-of-pass, успех | 96,7 % качества OWL при цене $0,228 вместо $0,398; cost-of-pass лучше на 28,4 % | один бенчмарк; цены провайдера |
| S03 | Bai et al. [How Do AI Agents Spend Your Money?](https://arxiv.org/abs/2604.22750) | 2026 | измерение расхода траекторий | SWE-bench Verified, 8 моделей | входные, выходные токены, успех | агентские задачи тратят в 1000 раз больше токенов, чем code chat; разброс до 30× на одной задаче; точность растёт до среднего расхода и выходит на плато; трудность людьми слабо предсказывает расход | сырые токены; приёмы не проверялись |
| S04 | Salim et al. [Tokenomics](https://arxiv.org/abs/2601.14470) | 2026 | разложение расхода по фазам SDLC | ChatDev, 30 задач, GPT-5 | доля токенов по фазам | code review — 59,4 % токенов; входные — 53,9 %; основной расход не в первичной генерации, а в доработке и проверке | один фреймворк, 30 задач |
| S05 | Weinberger, Hozez. [Token Reduction Is Not Cost Reduction](https://arxiv.org/abs/2607.12161) | 2026 | три сжатия вывода инструментов против Claude Code | контрольные кодовые задачи, SWE-bench Go | оплаченная стоимость, успех, кеш, траектория | −38,4 % токенов вывода дали +6,8 % стоимости; корреляция экономии токенов и стоимости r = 0,15; сжатие меняет траекторию и может снизить успех | один провайдер; кеш доминирует в цене |
| S06 | Du et al. [OckBench](https://arxiv.org/abs/2511.05722) | 2025 | бенчмарк точности и токенной эффективности | рассуждение и код | точность, длина в токенах | модели с близкой точностью различаются по длине до 5× | только измерение, без приёмов |
| S07 | Ali et al. [The Harness Effect](https://arxiv.org/abs/2607.06906) | 2026 | смена оркестрации при фиксированных моделях | 22 задачи, 6 моделей | стоимость, токены на задачу, качество | −38 % токенов на задачу, −41 % стоимости, качество на уровне; эффект переносится на все модели | вендорский harness, малая выборка |
| S08 | Agyemang et al. [Local-Splitter](https://arxiv.org/abs/2604.12301) | 2026 | семь тактик с локальным триажем | 4 класса кодовых нагрузок | облачные токены, стоимость, успех | локальная маршрутизация + сжатие промпта дают 45–79 % экономии на edit/explanation; RAG + draft-review — 51 % | локальная модель как триаж; сырые токены |
| S09 | Li et al. [TokenEconomizer](https://arxiv.org/abs/2610.22732) | 2026 | внешний контроллер микро-навыков, pruning инструментов, вмешательство в циклы | последовательности кодовых задач, Claude Code/Codex/Copilot | стоимость токенов, успех | −18,4–30,9 % стоимости при сопоставимом успехе; эффект в каждом репозитории | чёрный ящик, проприетарные агенты |
| S10 | Han et al. [TALE](https://arxiv.org/abs/2412.18547) | 2024 | бюджет токенов в промпте + оценка сложности | математика и QA | длина CoT, точность | заметное сокращение CoT при небольшом падении точности; выбор бюджета критичен | бюджет подбирается; нет агентов |
| S11 | Lee et al. [Token Complexity](https://arxiv.org/abs/2503.01141) | 2025 | связь длины и точности, минимальная токенная сложность | наборы рассуждения | длина, точность, информационный предел | универсальный trade-off; у каждой задачи есть порог токенов; промптовое сжатие далеко от теоретического предела; нужна адаптация по трудности | нет агентского цикла |
| S12 | He et al. [CARE](https://arxiv.org/abs/2609.29664) | 2026 | contrastive accuracy reward для длины | математика, код | Pass@1, длина | +4 % Pass@1 при −37 % длины; эффект сосредоточен на частично решаемых задачах | обучение; нет агентов |
| S13 | Yang et al. [Dynamic Early Exit](https://arxiv.org/abs/2504.15895) | 2025 | ранний выход по уверенности в пробном ответе | 10 бенчмарков, 11 моделей | длина CoT, точность | −19,1–80,1 % длины при +0,3–5,0 % точности | нужны пробные ответы; reasoning-модели |
| S14 | Wang et al. [ESTAR](https://arxiv.org/abs/2602.10004) | 2026 | классификатор остановки + SFT/RL | 4 набора рассуждения | длина, точность | 3,7× короче (4 799 → 1 290) при 74,9 % против 74,2 % | обучение; нет агентов |
| S15 | Xiang et al. [DTSR](https://arxiv.org/abs/2604.06787) | 2026 | мониторинг reflection-сигналов и проверка достаточности | Qwen3 | длина, точность | −28,9–34,9 % длины при минимальной потере | самооценка моделей переоценена |
| S16 | Li et al. [Budget Guidance](https://arxiv.org/abs/2506.13752) | 2025 | предиктор остатка длины без дообучения | MATH-500 и др. | длина, точность | 63 % токенов полного рассуждения при конкурентной точности; +26 % точности при жёстком бюджете | математика; нет агентов |
| S17 | Aggarwal, Welleck. [L1](https://arxiv.org/abs/2503.04697) | 2025 | RL с ограничением длины | наборы рассуждения | длина, точность | плавный trade-off длины и точности; короткие reasoning-модели | обучение; небольшие модели |
| S18 | Muennighoff et al. [s1](https://arxiv.org/abs/2501.19393) | 2025 | budget forcing | MATH, AIME | точность, бюджет | +27 % над o1-preview; 50 % → 57 % на AIME24 при продолжении | математика; SFT |
| S19 | Lee et al. [DART](https://arxiv.org/abs/2606.23181) | 2026 | два дешёвых no-think черновика, согласие или бюджет по энтропии | математика, код, hybrid-модели | thinking-токены, точность | −32–73 % thinking-токенов; +9,0 п.п. на олимпиадной математике и +22,5 п.п. на коде | нужны два черновика; hybrid-модели |
| S20 | Yang et al. [Ares](https://arxiv.org/abs/2603.07915) | 2026 | роутер уровня рассуждения на шаг | TAU-Bench, BrowseComp-Plus, WebArena | reasoning-токены, успех | −52,7 % reasoning-токенов при минимальной потере успеха | обученный роутер; агентские задачи |
| S21 | Hosseini et al. [Confidence Training](https://arxiv.org/abs/2609.31619) | 2026 | self-supervised confidence как цель обучения | математика, наука, код; 4 семейства моделей | токены, точность | −25 % токенов при той же точности; 600 задач | обучение; нет агентов |
| S22 | Cuadron et al. [Danger of Overthinking](https://arxiv.org/abs/2502.08235) | 2025 | анализ overthinking в агентах | SWE-bench Verified, 4 018 траекторий | overthinking score, успех, стоимость | выбор решения с меньшим overthinking даёт почти +30 % успеха и −43 % стоимости | анализ; выбор требует нескольких прогонов |
| S23 | Caldarella et al. [Harmful Overthinking](https://arxiv.org/abs/2606.02835) | 2026 | оценка траекторий после первого правильного ответа | мультимодальные и текстовые рассуждения | точность, длина | остановка на первом правильном префиксе даёт до +21 % точности; early stopping убирает до 50 % «болтливого», но не вредного overthinking | не агенты; мультимодальность |
| S24 | Zhou et al. [When More Thinking Hurts](https://arxiv.org/abs/2604.10739) | 2026 | маргинальная полезность токенов | наборы рассуждения | точность, бюджет | отдача падает; модель может отказаться от уже правильного ответа; оптимальная длина зависит от трудности | нет агентов |
| S25 | Xue et al. [Reasoning Steps in Thinking Code LLMs](https://arxiv.org/abs/2511.05874) | 2025 | управление числом шагов | BigCodeBench, 100 задач, 6 моделей | число шагов, успех | умеренное сокращение сохраняет успех на стандартных задачах, редко — на трудных; completeness — главный провал | 100 задач; 21 эксперт |
| S26 | Li et al. [HERO](https://arxiv.org/abs/2609.38885) | 2026 | иерархический RL для token-efficient coding agent | SWE-bench Verified/Multilingual | resolve rate, токены | лучший trade-off разрешения и токенов, чем у SOTA-агентов | обучение; нет публичного кода в аннотации |
| S27 | Chen et al. [FrugalGPT](https://arxiv.org/abs/2305.05176) | 2023 | каскад моделей | массовые запросы | стоимость, качество | качество GPT-4 при −98 % стоимости или +4 % качества при той же цене | одиночные запросы, не агенты |
| S28 | Zellinger et al. [Early Abstention](https://arxiv.org/abs/2502.09054) | 2025 | каскад с отказом на ранних моделях | 6 бенчмарков | стоимость, ошибка, доля отказов | −13 % стоимости и −5 % ошибок ценой +4,1 % отказов; test loss −2,2 % | QA, не код |
| S29 | Yue et al. [Mixture of Thoughts Cascade](https://arxiv.org/abs/2310.03094) | 2023 | каскад по согласию ответов | 6 наборов рассуждения | стоимость, качество | качество GPT-4 за 40 % его стоимости | старые модели; QA |
| S30 | Lee et al. [STEER](https://arxiv.org/abs/2511.06190) | 2025 | пошаговая маршрутизация по уверенности | математика, multi-hop QA, планирование | FLOPs, точность | +20 % точности при −48 % FLOPs против большой модели на AIME | FLOPs, а не токены; нет кода |
| S31 | Chen et al. [Model Cascading for Code](https://arxiv.org/abs/2405.15842) | 2024 | каскад + self-testing для кода | генерация кода | стоимость, точность | −26 % стоимости в среднем, до −70 %; точность не хуже | code completion; стоимость тестов |
| S32 | Zhang et al. [Budget-Aware Agentic Routing](https://arxiv.org/abs/2602.21227) | 2026 | выбор дешёвой/дорогой модели на каждом шаге | агентские задачи | cost-success frontier | лучше frontier при существенно меньшей стоимости; работает при жёстком бюджете | обучение; нет кода |
| S33 | Snell et al. [Compute-Optimal Scaling](https://arxiv.org/abs/2408.03314) | 2024 | аллокация test-time compute по трудности | математика | FLOPs, точность | в 4× эффективнее best-of-N; малая модель с compute обходит 14× большую при ненулевом успехе | FLOPs; математика |
| S34 | Ehrlich et al. [CodeMonkeys](https://arxiv.org/abs/2501.14723) | 2025 | много траекторий + голосование по тестам + селектор | SWE-bench Verified | resolve rate, доллары | 57,4 % при бюджете около $2 300; селектор по ансамблю даёт 66,2 % | очень дорого; не про экономию на решённую задачу |
| S35 | Dong, Shigida. [Independent Sampling](https://arxiv.org/abs/2605.08478) | 2026 | k-shot против агентского рассуждения | 216 задач Codeforces | точность/стоимость, точность/вызов | k-shot лучше по обеим осям; оптимальный решатель минимизирует log failure на доллар | только самодостаточные алгоритмические задачи |
| S36 | Aggarwal et al. [Adaptive-Consistency](https://arxiv.org/abs/2305.11860) | 2023 | остановка голосования по согласию | 17 наборов, 3 модели | число сэмплов, точность | бюджет сэмплов −7,9× при падении точности <0,1 % | только сэмплирование |
| S37 | Jiang et al. [LLMLingua](https://arxiv.org/abs/2310.05736) | 2023 | сжатие промпта | GSM8K, BBH, ShareGPT, arXiv | коэффициент сжатия, качество | до 20× сжатия при небольшой потере | только входные токены; нужна модель-компрессор |
| S38 | Dixit et al. [FOCUS](https://arxiv.org/abs/2609.37590) | 2026 | причинно-сохраняющее сжатие истории без обучения | API/tool-calling, QA, web, диалог | пиковый контекст, успех | −48 % пикового контекста, −73 % зависимостей, +8,9 п.п. успеха | причинный прокси; не код |
| S39 | Liu et al. [Latent Tool Compression](https://arxiv.org/abs/2611.06500) | 2026 | сжатие вывода инструментов в латентные токены | web-search QA, 2 семейства моделей | токены, runtime, качество | −70,01–89,24 % токенов, −24,45–55,97 % runtime, качество растёт | обученный компрессор; web QA |
| S40 | Chaturvedi et al. [DTOC](https://arxiv.org/abs/2609.26121) | 2026 | обратимое сжатие вывода инструментов | DeepSWE | входные токены, шаги, cost per solved task | для отзывчивых моделей: −10,3–12,7 % входа, −2,4–32,3 % шагов, solve rate 1,5–2,5×, cost per solved 3–3,5× ниже; для других смешанно | сильная зависимость от модели |
| S41 | Li et al. [ACM](https://arxiv.org/abs/2607.23809) | 2026 | инструменты управления контекстом + внешняя память | агентский поиск и код | пиковое давление токенов, успех | снижает пиковый контекст, позволяет длиннее исследовать, стабильнее между прогонами | нужны демонстрации/дообучение |
| S42 | Liu et al. [CAT](https://arxiv.org/abs/2512.22087) | 2025 | контекст как вызываемый инструмент | SWE-bench Verified | resolve rate, контекстный бюджет | SWE-Compressor: 57,6 % solved при ограниченном контексте, лучше ReAct и статического сжатия | обучение |
| S43 | Sun et al. [Context Folding](https://arxiv.org/abs/2510.11967) | 2025 | свёртка подтраекторий | deep research, SWE | активный контекст, успех | в 10× меньший активный контекст при уровне ReAct или лучше | RL-обучение |
| S44 | Wang et al. [ICLR](https://arxiv.org/abs/2609.29875) | 2026 | забывание исторических рассуждений без обучения | 260 задач WorkBuddyBench | вход/выход/кеш, reward | −25,5 % входа, −14,4 % выхода, −33,3 % чтения кеша, reward 0,699 → 0,718 | не код; нужен прокси-сигнал |
| S45 | Gao et al. [SWE-MeM](https://arxiv.org/abs/2606.28434) | 2026 | память как инструмент + Memory-aware GRPO | SWE-bench Verified | resolve rate, эффективность | 43,4 % и 60,2 % для 4B и 30B; лучше baseline по качеству и расходу | обучение |
| S46 | Ren et al. [TACO](https://arxiv.org/abs/2604.19572) | 2026 | самоэволюционирующее сжатие наблюдений терминала | TerminalBench, SWE-bench Lite, CompileBench и др. | точность, токены | +1–4 % точности; +2–3 % при том же бюджете токенов; ниже суммарный расход | терминальные домены; правила |
| S47 | Xiao et al. [TraceLite](https://arxiv.org/abs/2610.28612) | 2026 | изображения истории + удаление дублей | SWE-bench Verified, DeepSWE | resolve rate, входные токены, стоимость | 78,25 % resolve, −33,05 % входа, −21,30 % стоимости API | рендер в изображения; модели |
| S48 | Chen et al. [Measure Before You Manage](https://arxiv.org/abs/2608.31057) | 2026 | анализ рабочей памяти кодовых агентов | 55 архивных траекторий | удержание, сжатие, стоимость управления | разные типы объектов сжимаются по-разному; равный бюджет токенов не значит равный контекст; выигрыш калибровки не переносится | только 55 траекторий |
| S49 | Fan et al. [Harness Design](https://arxiv.org/abs/2609.20804) | 2026 | покомпонентное сравнение harness | SWE-bench Verified, Terminal-Bench 2.1, 176 настроек | успех, стоимость | управление контекстом важно при узком окне; rule-based elision до суммаризации — лучший режим; планирование экономит сильным моделям; bash-only дешевле | конкретный harness и модели |
| S50 | Lulla et al. [AGENTS.md](https://arxiv.org/abs/2601.20404) | 2026 | файл инструкций репозитория | 10 репозиториев, 124 PR | runtime, выходные токены, завершение | −28,64 % медианного runtime, −16,58 % выходных токенов при сопоставимом завершении | наблюдательное, 10 репозиториев |
| S51 | Zhang et al. [FastContext](https://arxiv.org/abs/2606.14066) | 2026 | отдельный исследователь репозитория | SWE-bench Multilingual/Pro, SWE-QA | resolve rate, токены | +5,5 % resolve при −60 % токенов кодового агента | обученный исследователь 4B–30B |
| S52 | Xia et al. [Agentless](https://arxiv.org/abs/2407.01489) | 2024 | локализация → ремонт → валидация без агентского цикла | SWE-bench Lite | resolve rate, доллары | 32,00 % (96 исправлений) при $0,70; лучше открытых агентов того времени | модели 2024; нет многошаговости |
| S53 | Xu et al. [Tool Architecture](https://arxiv.org/abs/2608.11386) | 2026 | сравнение шести архитектур инструментов | 11 700 траекторий, 3 актора | шаги, токены, консистентность | CodeAct-подобный интерфейс: −41,6 % шагов и −56,3 % токенов при том же качестве | конкретные акторы и задачи |
| S54 | Gandhi et al. [Steer, Don't Solve](https://arxiv.org/abs/2606.21811) | 2026 | дешёвый критик высокоуровневого плана | SWE-bench Verified, 6 агентов | resolve rate, стоимость | +16,0 % и +14,4 % resolved для двух агентов; стоимость примера $0,07 → $0,03 | обучение критика; не все агенты дешевеют |
| S55 | Xu et al. [ContextPipe](https://arxiv.org/abs/2609.00749) | 2026 | детерминированная сборка контекста с бюджетом | SWE-bench Pro, Qutebrowser | объём токенов, вызовы, время | −31 % токенов, −23 % вызовов LLM, −9 % времени | один срез; ниже hit rate KV-кеша |
| S56 | Zhang et al. [Agentic Plan Caching](https://arxiv.org/abs/2506.14852) | 2025 | кеш шаблонов планов между похожими задачами | несколько агентских приложений | стоимость, latency, качество | −50,31 % стоимости, −27,28 % latency при сохранении качества | нужны похожие задачи; не разовые |
| S57 | Li et al. [BAVT](https://arxiv.org/abs/2603.12634) | 2026 | budget-aware value tree search | 4 набора multi-hop QA | успех, бюджет | при жёстком бюджете обходит baseline с 4× ресурсом | QA; нужен value-предиктор |
| S58 | He et al. [Consequence-Aware Allocation](https://arxiv.org/abs/2606.04402) | 2026 | приоритет по последствиям ошибки | SWE-bench Lite | успех на высокоценных задачах, общая точность | лучший успех на высокоценных задачах при фиксированном compute; общая точность конкурентна | нужен предиктор последствий |
| S59 | Luo et al. [HERA](https://arxiv.org/abs/2610.06563) | 2026 | коэволюция harness и среды для отказа | пары выполнимых/невыполнимых задач | abstention accuracy, completion, стоимость | abstention 61,7 % → 83,3 %, feasible 68,3 % → 76,7 %; перенос +15,3 п.п.; малые модели при −85 % стоимости | синтетические невыполнимые задачи |
| S60 | Zhao et al. [ROI-Reasoning](https://arxiv.org/abs/2601.03822) | 2026 | мета-когнитивный прогноз стоимости + RL при глобальном бюджете | математика, MCQ, код | score, regret | до +417 % относительного score при жёстком бюджете | обучение |
| S61 | Li et al. [ContextCurator](https://arxiv.org/abs/2604.11462) | 2026 | отдельная лёгкая политика управления контекстом | WebArena, DeepSearch | успех, токены | WebArena 36,4 % → 41,2 % при −8,8 % токенов; DeepSearch 53,9 % → 57,1 % при 8× меньше токенов | web/search, не код |
| S62 | Ning et al. [HRBench](https://arxiv.org/abs/2605.28398) | 2026 | бенчмарк переключения thinking-режима | 6 hybrid-моделей, 5 бенчмарков | точность, токены | prompt-based выбор даёт хороший trade-off, routing — стабильную экономию, speculative — дороже | бенчмарк, не продакшен |
| S63 | Alomrani et al. [Reasoning on a Budget](https://arxiv.org/abs/2507.02076) | 2025 | обзор L1-контроля и L2-адаптивности | reasoning-модели | токены, точность | систематизирует управление test-time compute; фиксированный compute неоптимален | обзор |
| S64 | Sui et al. [Stop Overthinking](https://arxiv.org/abs/2503.16419) | 2025 | обзор эффективного рассуждения | reasoning-модели | длина, качество | таксономия: модель, выход, промпт; overthinking — системная проблема | обзор |

## Исключённые (49)

Причины: `дубль` — перекрывает включённую работу и не добавляет нового
замера; `не тот объект` — ускорение, кеш, обучение или домен, который не
переносится; `нет замера` — нет количественного результата рядом с
качеством; `бенчмарк` — описывает измерение, а не приём.

| ID | Источник | Причина |
| --- | --- | --- |
| X01 | Renze, Guven. [Concise CoT](https://arxiv.org/abs/2401.05618) | дубль: тот же вывод, что S10–S11; нет агентов |
| X02 | Pan et al. [LLMLingua-2](https://arxiv.org/abs/2403.12968) | дубль S37; только входные токены |
| X03 | Nagle et al. [Fundamental Limits of Prompt Compression](https://arxiv.org/abs/2407.15504) | нет замера на агенте; теория сжатия |
| X04 | Li et al. [Prompt Compression Survey](https://arxiv.org/abs/2410.12388) | дубль S37; обзор без нового замера |
| X05 | Estermann, Wattenhofer. [Reasoning Effort and Complexity](https://arxiv.org/abs/2503.15113) | не тот объект: головоломка Tents, нет приёма экономии |
| X06 | Liu et al. [Efficient Inference for LRMs](https://arxiv.org/abs/2503.23077) | дубль S63–S64 |
| X07 | Petrov et al. [Gisting](https://arxiv.org/abs/2504.08934) | нет агента; метод проигрывает average pooling |
| X08 | Feng et al. [Efficient Reasoning Models](https://arxiv.org/abs/2504.10903) | дубль S63–S64 |
| X09 | Sun et al. [Strict Output Length Constraint](https://arxiv.org/abs/2504.14350) | нет агента; только оценка 30 моделей |
| X10 | Qiao et al. [ConCISE](https://arxiv.org/abs/2505.04881) | дубль S13–S14; обучение |
| X11 | Ghosal et al. [Mirage of Test-Time Scaling](https://arxiv.org/abs/2506.04210) | дубль S24; нет агента |
| X12 | Betancor et al. [Fractional Kolmogorov Operators](https://arxiv.org/abs/2506.14631) | не тот объект: математический анализ, ложное попадание |
| X13 | Tang et al. [ConciseHint](https://arxiv.org/abs/2506.18810) | дубль S13–S16; нет агента |
| X14 | Zhu, Li. [Concise and Adaptive Thinking Survey](https://arxiv.org/abs/2507.09662) | дубль S63–S64 |
| X15 | Guo et al. [ACC-RAG](https://arxiv.org/abs/2507.22931) | только RAG-контекст, входные токены; дубль S37 |
| X16 | Liu et al. [SMITH](https://arxiv.org/abs/2512.11303) | нет замера токенов; GAIA |
| X17 | Iacobacci et al. [Thinking Budget](https://arxiv.org/abs/2512.19585) | дубль S24; нет агента |
| X18 | Lumer et al. [Prompt Caching](https://arxiv.org/abs/2601.06007) | не тот объект: кеш провайдера не учитывается регламентом |
| X19 | Singh. [Semantic Caching for NL2Code](https://arxiv.org/abs/2601.11687) | нет контролируемого замера; продакшен-отчёт |
| X20 | Wang et al. [Optimal Budgeted Adaptation](https://arxiv.org/abs/2602.00952) | не тот объект: дообучение, не инференс |
| X21 | Mi et al. [Skill-Pro](https://arxiv.org/abs/2602.01869) | нет замера токенов на задачу |
| X22 | Li et al. [ContextBench](https://arxiv.org/abs/2602.05892) | бенчмарк retrieval, не приём |
| X23 | Zeng et al. [LOCA-bench](https://arxiv.org/abs/2602.07962) | бенчмарк контекста, не приём |
| X24 | Pollertlam, Kornsuwannawit. [Memory vs Long Context](https://arxiv.org/abs/2603.04814) | не тот объект: чат-бот, не код |
| X25 | Zhao et al. [PoC](https://arxiv.org/abs/2603.19733) | нет агента; сжатие без cost per solved task |
| X26 | Chen et al. [Token Economics Survey](https://arxiv.org/abs/2605.09104) | дубль S63; обзор без нового замера |
| X27 | Jin et al. [EXG](https://arxiv.org/abs/2605.17721) | нет замера токенов |
| X28 | Kotte. [UCCI](https://arxiv.org/abs/2605.18796) | NER, не код; дубль S30 |
| X29 | Hamri, Talgam-Cohen. [ZEBRA](https://arxiv.org/abs/2605.20485) | multi-phase split, не одиночный агент; дубль S57 |
| X30 | Merchant et al. [Temporal Semantic Caching](https://arxiv.org/abs/2605.20630) | latency, не токены |
| X31 | Yang, Zhu. [Water-filling](https://arxiv.org/abs/2605.23929) | теория workflow, нет кодового замера |
| X32 | Florian et al. [Beyond pass@k](https://arxiv.org/abs/2605.28022) | качество сэмплирования, не стоимость на решённую |
| X33 | Lin et al. [AbstainGNN](https://arxiv.org/abs/2605.30786) | не тот объект: графовые сети |
| X34 | Xu et al. [TokenPilot](https://arxiv.org/abs/2606.17016) | кеш-центрично; кеш не учитывается |
| X35 | Peng et al. [Inference Economics](https://arxiv.org/abs/2607.13080) | доллары/TCO, не токены на решённую |
| X36 | El-Ramly. [ACEM](https://arxiv.org/abs/2608.02582) | модель стоимости без эмпирических результатов |
| X37 | Xue et al. [Cost-Aware Bandits](https://arxiv.org/abs/2608.04333) | оценка конфигураций, не задачи агента |
| X38 | Moon. [Price of Thinking](https://arxiv.org/abs/2608.16956) | одна модель и математика; дубль S01 |
| X39 | Qiu et al. [LifeMem](https://arxiv.org/abs/2609.12655) | память без замера токенов |
| X40 | Kwartler et al. [Harness Tokenomics](https://arxiv.org/abs/2609.28919) | enterprise-роутер, дубль S07/S27 |
| X41 | Li et al. [Implicit Budgeting](https://arxiv.org/abs/2610.27190) | композиция задач, не агент |
| X42 | Chu et al. [Context Compression for Repo-Level Tasks](https://arxiv.org/abs/2604.13725) | нет агентского цикла; дубль S37/S38 |
| X43 | Enomoto et al. [Read More, Think More](https://arxiv.org/abs/2604.01535) | web-агенты; дубль S48/S49 |
| X44 | Zhang et al. [Masking Stale Observations](https://arxiv.org/abs/2606.00408) | поисковые агенты; дубль S48/S49 |
| X45 | Yang et al. [DocString Compression](https://arxiv.org/abs/2410.22793) | узкое сжатие DocString; дубль S37 |
| X46 | Ma et al. [GraphACM](https://arxiv.org/abs/2610.22031) | требует несколько прогонов; дубль S58 |
| X47 | Suzgun et al. [Dynamic Cheatsheet](https://arxiv.org/abs/2504.07952) | память между задачами; дубль S56 |
| X48 | Yang et al. [AdaCtrl](https://arxiv.org/abs/2505.18822) | обучение; дубль S12/S17 |
| X49 | Nayab et al. [Concise Thoughts](https://arxiv.org/abs/2407.19825) | QA, не агенты; дубль S11 |
