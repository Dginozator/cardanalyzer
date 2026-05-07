#кат1

# Спецификация описания карточки товара v1.4 (draft)

Цель: единый машинно-читаемый формат для (а) кластеризации макетов, (б) генерации новых карточек по шаблону, (в) поиска похожих.

Изменения относительно v1.3:
- `safe_areas` переведено в производное поле, вычисляется из `marketplace_overlay.elements`. Ручная правка запрещена.
- Добавлен раздел «safe_areas: механика и расчёт».
- Добавлены пункты валидации: соответствие `safe_areas` правилам расчёта; диапазоны и суммы сторон.
- Версия схемы повышена до `1.4`.

---

## Принципы

1. Разделение слоёв: `design` (дизайн от селлера) и `marketplace_overlay` (UI площадки) хранятся отдельно.
2. Разделение признаков: `structural` (геометрия/композиция), `visual` (стиль/цвет), `semantic` (смысл/роль) — три независимых вектора для кластеризации.
3. Для всех категориальных полей используются контролируемые словари (enum). Поля, допускающие свободный текст, помечены тегом **[free-text]**.
4. Координаты нормализованы: значения в долях [0..1], origin = top-left.
5. Поля без явной пометки считаются `optional`.
6. Конвенция именования полей: `{category}_{subtype}`.
7. Спецификация самодостаточна: все словари заданы внутри документа, внешних справочников нет.

---

## Описание корневых разделов

- **`canvas`** — физические параметры холста.
- **`structural`** — геометрия и композиция: архетип, плотность, элементы с координатами.
- **`visual`** — визуальный стиль: фон, палитра.
- **`semantic`** — смысловая шапка: категория товара, агрегированный текст, смысл изображения.
- **`marketplace_overlay`** — элементы UI площадки поверх карточки.
- **`clustering_keys`** — детерминированно вычисляемые строковые ключи.
- **`generation`** — ограничения и подсказки для генератора.

Замечание: `structural.elements` — единственное место хранения элементов дизайна. `visual` и `semantic` содержат агрегаты.

---

## Корневая схема

```yaml
schema_version: "1.4"               # версия схемы
card_id: string                     # required, [free-text] — уникальный ID (UUID/хеш)

source:                             # происхождение карточки
  url: string                       # [free-text] — URL источника
  marketplace: enum                 # площадка (см. enum marketplace)
  captured_at: ISO8601              # дата захвата

canvas:                             # required — физические параметры холста
  aspect_ratio: enum                # соотношение сторон (см. enum aspect_ratio)
  resolution_px: [W, H]             # исходное разрешение в пикселях
  safe_areas:                       # required — вычисляется детерминированно из marketplace_overlay.elements; ручная правка запрещена
    top: float                      # доля перекрытия сверху [0..1]
    right: float                    # доля перекрытия справа [0..1]
    bottom: float                   # доля перекрытия снизу [0..1]
    left: float                     # доля перекрытия слева [0..1]

structural:                         # required — геометрия и композиция
  composition:
    archetype: enum                 # архетип компоновки (см. enum composition_archetype)
    density: enum                   # плотность заполнения (см. enum density)
  elements: [Element, ...]          # все элементы дизайна

visual:                             # required — визуальный стиль
  background:
    type: enum                      # тип фона (см. enum background_type)
    colors: [hex, ...]              # цвета фона; для градиента — крайние точки
    notes: string                   # [free-text], не для ML
  palette:
    dominant: [hex, hex, hex]       # 3 доминирующих цвета
    accents: [hex, ...]             # акцентные цвета
    tone: enum                      # светлота палитры (см. enum tone)
    saturation: enum                # насыщенность (см. enum saturation)
    temperature: enum               # цветовая температура (см. enum temperature)

semantic:                           # required — смысловая шапка
  product_category: enum            # категория товара (см. enum product_category)
  text_content:                     # агрегированный текст с карточки
    full_text: string               # [free-text] — весь видимый текст, конкатенация по z_order через \n
    keywords: [string, ...]         # [free-text] — значимые термины; алгоритм извлечения — отдельный документ
  image_meaning:
    scene_description: string       # [free-text, ≤ 500 символов] — краткое описание визуальной сцены

marketplace_overlay:                # optional — UI маркетплейса поверх карточки; источник правды для safe_areas
  elements: [Element, ...]          # элементы UI; роли только из overlay_role

clustering_keys:                    # required — вычисляется детерминированно; ручная правка запрещена
  structural_key: string            # ключ по геометрии и ролям
  visual_key: string                # ключ по фону, палитре, плотности
  semantic_key: string              # ключ по категории
  full_key: string                  # объединённый ключ

generation:                         # параметры для генератора
  hints:
    must_keep: [selector, ...]      # селекторы полей/элементов, которые генератор не меняет
    free_to_change: [selector, ...] # селекторы полей/элементов, которые генератор может менять свободно
  constraints:
    min_text_contrast_ratio: float  # минимальный WCAG-контраст текста к фону
    max_density_pct: float          # верхний порог плотности (в процентах от площади холста)
    min_safe_area_clearance_pct: float  # минимальный зазор между bbox критичных элементов и safe_areas (в процентах от меньшей стороны холста)
    forbid_overlap_with_safe_area: bool # запрет пересечения bbox критичных элементов с safe_areas
    max_palette_colors: int         # лимит цветов в палитре
```

**Критичные элементы** для `min_safe_area_clearance_pct` и `forbid_overlap_with_safe_area` — элементы с ролями из фиксированного списка: `product_main`, `text_headline`, `price_tag`, `trust_mark`.

Формат `selector` описан в разделе «Селекторы элементов (DSL)».

---

## Схема Element

```yaml
Element:
  element_id: string                # required, [free-text] — локальный ID в пределах карточки
  role: enum                        # required — значение из element_role или overlay_role
  group_id: string | null           # ID родительского элемента с role=group
  bbox: [x, y, w, h]                # required — x,y — top-left угол, w,h — ширина/высота; в долях [0..1]
  anchor: enum                      # required — зона холста для центра bbox (см. enum anchor и раздел "anchor: механика")
  z_order: int                      # required — порядок наложения; больше = выше
  shape: enum                       # геометрия видимой границы (см. enum shape)
  arrangement: enum | null          # внутренняя раскладка; required для group, brand_pattern, kit_showcase; иначе null
  product_view: enum | null         # required только для role=product_main; иначе null

  content:
    text: string | null             # [free-text] — отображаемый текст

  visual:
    fill_color: hex | null          # цвет заливки
    stroke_color: hex | null        # цвет обводки
    text_color: hex | null          # цвет текста
    has_icon: bool                  # есть ли пиктограмма у элемента
    icon_concept: string | null     # [free-text, ≤ 30 символов] — краткое описание пиктограммы
    has_shadow: bool                # есть ли тень
    contrast_level: enum            # контраст к фону (см. enum contrast_level)

  relations:
    parent: element_id | null       # логический родитель (не group)
    aligned_with: [element_id, ...] # выровнен с этими элементами по краю/оси
    overlaps: [element_id, ...]     # bbox пересекается с этими элементами

  notes: string                     # [free-text], не для ML
```

---

## Селекторы элементов (DSL)

Используются в `generation.hints.must_keep` и `generation.hints.free_to_change`.

**Область действия:** только `structural.*` и `visual.*`.

### Грамматика

```
selector   := path
path       := segment ("." segment)*
segment    := field_name
            | "elements[" predicate "]"
predicate  := condition ("," condition)*        # AND
condition  := key "=" value
            | key " in " "[" value ("," value)* "]"
key        := identifier
value      := string | enum_literal
```

**Правила:**
- Предикат применяется только к массиву `elements`.
- Несколько условий в предикате объединяются через `,` по правилу AND.
- Оператор `=` — точное равенство.
- Оператор `in` — вхождение в список.

### Примеры

Поля целиком:
```
visual.background
visual.palette.dominant
visual.palette.accents
structural.composition
```

Элементы по роли:
```
structural.elements[role=product_main]
structural.elements[role=text_feature]
structural.elements[role=brand_logo].bbox
```

Список ролей:
```
structural.elements[role in [text_headline, text_feature, text_info]]
```

### Семантика в контексте `generation.hints`

- `must_keep` — при генерации значения по селектору остаются неизменными. Если селектор указывает на элемент целиком, сохраняются все его поля.
- `free_to_change` — значения по селектору разрешено менять.
- Селектор, не нашедший совпадений, молча игнорируется.
- Пересечение множеств `must_keep` и `free_to_change` запрещено.

### Пример блока hints

```yaml
generation:
  hints:
    must_keep:
      - "visual.background"
      - "structural.elements[role=product_main]"
      - "structural.elements[role=brand_logo].bbox"
      - "visual.palette.dominant"
    free_to_change:
      - "structural.elements[role=text_feature]"
      - "structural.elements[role=promo_offer]"
      - "visual.palette.accents"
```

### Ограничения v1.4

- Поддерживаются только операторы `,` в качестве AND, `=` и `in`.
- Предикаты возможны только у массива `elements`.
- Адресация возможна только для `structural.*` и `visual.*`.

---

## Контролируемые словари (enum)

```yaml
aspect_ratio:
  - "9:16"   # вертикальный, наиболее частый формат карточки
  - "3:4"    # вертикальный, классический
  - "1:1"    # квадрат
  - "4:3"    # горизонтальный
  - "16:9"   # широкий горизонтальный

background_type:
  - solid        # однотонная заливка
  - gradient     # градиент между двумя+ цветами
  - scene        # фотофон/интерьер/lifestyle-сцена
  - texture      # повторяющаяся текстура/паттерн
  - transparent  # фона нет

composition_archetype:
  - single_focus   # один доминирующий объект (товар или demo) в центре внимания, остальное вокруг
  - split          # холст разделён на зону товара и зону инфо; направление выводится из anchor элементов
  - demo_focus     # композиционный центр — артефакт/результат (product_demo); сам товар может отсутствовать
  - no_focus       # равномерная композиция без явного центра (паттерн, лента, заливка)

density:
  - low      # покрытие холста элементами < 35%
  - medium   # 35–65%
  - high     # > 65%

shape:
  - rectangle     # прямой прямоугольник
  - rounded_rect  # со скруглёнными углами
  - circle        # круг
  - ellipse       # эллипс
  - polygon       # многоугольник
  - cutout        # вырезанный по контуру объект (фото без фона)
  - freeform      # произвольная форма

anchor:
  - top_left      # верхний левый
  - top_center    # верхний центр
  - top_right     # верхний правый
  - center_left   # средний левый
  - center        # центр
  - center_right  # средний правый
  - bottom_left   # нижний левый
  - bottom_center # нижний центр
  - bottom_right  # нижний правый

contrast_level:
  - low      # WCAG ratio < 3
  - medium   # 3–7
  - high     # > 7

tone:
  - light    # средняя L в HSL доминирующих цветов > 0.66
  - medium   # 0.33–0.66
  - dark     # < 0.33

saturation:
  - muted     # средняя S в HSL доминирующих цветов < 0.25
  - moderate  # 0.25–0.65
  - vivid     # > 0.65

temperature:
  - warm      # преобладает hue в секторе 0°–60° и 300°–360° (красный, оранжевый, жёлтый, пурпурный)
  - neutral   # палитра близка к ахроматической (средняя S < 0.15) или hue смешан
  - cool      # преобладает hue в секторе 60°–300° (зелёный, голубой, синий)

marketplace:
  - ozon
  - wildberries
  - yandex_market
  - avito
  - other

product_category:
  - food           # продукты питания
  - home           # товары для дома и мебель
  - apparel        # одежда и обувь
  - electronics    # электроника и бытовая техника
  - auto           # автозапчасти и автоаксессуары
  - digital        # цифровые товары
  - tools          # инструменты
  - beauty_health  # товары для красоты и здоровья
  - kids           # товары для детей
  - sports         # спорттовары
  - other          # прочее

product_view:
  - catalog     # студийное фото на однотонном фоне (cutout/силуэт)
  - close_up    # крупный план, акцент на детали
  - in_use      # товар в действии или используется человеком
  - lifestyle   # товар в окружении/интерьере
  - group_shot  # несколько единиц товара в единой композиции (визуально неотделимы)

arrangement:
  - linear_x    # горизонтальный ряд
  - linear_y    # вертикальный столбец
  - grid        # двумерная сетка
  - radial      # веер/радиально
  - repeat_x    # повтор по X
  - repeat_y    # повтор по Y
  - repeat_xy   # заливка повторением (паттерн на всю площадь)
  - scattered   # рассеянно/хаотично

element_role:
  # product_*
  - product_main       # главный товар; обязателен product_view
  - product_secondary  # дополнительный ракурс/экземпляр с самостоятельной и повторяемой геометрией
  - product_demo       # артефакт/результат работы (проекция, пятно света, схема, до/после)

  # text_*
  - text_headline      # крупный заголовок-УТП или название категории
  - text_feature       # свойство/преимущество текстом
  - text_info          # информационный баннер от селлера
  - text_spec          # числовой технический параметр в плашке

  # kit_*
  - kit_quantity       # количество в одном лоте/упаковке
  - kit_showcase       # визуальный показ состава набора; обязателен arrangement

  # brand_*
  - brand_logo         # графический логотип бренда/селлера
  - brand_name         # название бренда текстом
  - brand_pattern      # повторяющийся брендовый паттерн; обязателен arrangement

  # прочие самостоятельные
  - trust_mark         # бейдж доверия (гарантия, сертификат, оригинал)
  - promo_offer        # маркетинговая плашка от селлера (хит, новинка, акция)
  - price_tag          # ценник, нанесённый на дизайн карточки

  # служебные
  - group              # универсальный контейнер; обязателен arrangement

overlay_role:
  - overlay_wishlist     # иконка избранного
  - overlay_rating       # рейтинг (звёзды/число)
  - overlay_logo         # логотип маркетплейса
  - overlay_promo        # промо-плашка площадки
  - overlay_discount     # стикер скидки от площадки
  - overlay_loyalty      # баллы/кэшбэк
  - overlay_delivery     # сроки доставки
  - overlay_variant      # подсказка о вариантах товара
  - overlay_installment  # рассрочка
  - overlay_stock        # остатки
```

---

## anchor: механика

`anchor` — зона холста, в которую попадает геометрический центр bbox элемента. 9 зон образуются делением холста сеткой 3×3 равными третями.

**Назначение:**
- Огрублённое описание расположения, устойчивое к мелким сдвигам.
- Используется в `clustering_keys.structural_key` для «скелета» компоновки.
- Используется для вывода направления в `composition.archetype = split`.

**Правила вычисления:**
- Точка для определения `anchor` — **центр bbox**: `(x + w/2, y + h/2)`.
- Границы зон: вертикальные на `1/3` и `2/3` ширины, горизонтальные на `1/3` и `2/3` высоты холста.
- На границе — округление вниз/влево.

**Инварианты:**
- `anchor` — привязка к **холсту**.
- У каждого элемента ровно один `anchor`.
- Для крупных элементов `anchor` определяется по центру bbox.

Иерархическая привязка задаётся через `group_id` и `relations.parent`.

---

## safe_areas: механика и расчёт

`safe_areas` — четыре числа в `canvas`, описывающие зоны по краям холста, перекрытые UI маркетплейса. Поле производное и вычисляется из `marketplace_overlay.elements`. Ручная правка запрещена.

**Назначение:**
- Учитывать «слепые» зоны при генерации новых карточек, чтобы критичные элементы дизайна оставались за пределами UI площадки.
- Использовать в `generation.constraints.min_safe_area_clearance_pct` и `forbid_overlap_with_safe_area`.

**Источник правды.** `marketplace_overlay.elements`. Если раздел отсутствует или пуст — все четыре поля = 0.

**Алгоритм расчёта.**

Для каждой стороны холста смотрим, какие overlay-элементы прижаты к этому краю, и берём максимальный «вылет» от края. Один элемент может вносить вклад в несколько сторон одновременно (угловой → top + right).

Параметр `THRESHOLD = 0.05` — порог «прижатости» к краю в долях стороны холста.

```
top    = max(y + h)    среди overlay-элементов, у которых y < THRESHOLD
                        иначе 0

bottom = 1 - min(y)    среди overlay-элементов, у которых (y + h) > 1 - THRESHOLD
                        иначе 0

left   = max(x + w)    среди overlay-элементов, у которых x < THRESHOLD
                        иначе 0

right  = 1 - min(x)    среди overlay-элементов, у которых (x + w) > 1 - THRESHOLD
                        иначе 0
```

**Пример.** Иконка избранного в правом верхнем углу: `bbox = [0.92, 0.02, 0.06, 0.06]`.
- `y = 0.02 < 0.05` → вносит вклад в `top`: `top = max(top, 0.02 + 0.06) = 0.08`.
- `x + w = 0.98 > 0.95` → вносит вклад в `right`: `right = max(right, 1 − 0.92) = 0.08`.
- В `bottom` и `left` не идёт.

**Инварианты:**
- Все значения в [0..1].
- `top + bottom < 1.0`; `left + right < 1.0`.
- При смене UI площадки (рестайлинг маркетплейса) `marketplace_overlay` устаревает, `safe_areas` пересчитывается, фактически создаётся новая запись карточки.

---

## Правила вычисления tone / saturation / temperature

Все три поля вычисляются детерминированно из `visual.palette.dominant` (3 hex-цвета).

1. Каждый hex переводится в HSL (H в градусах 0–360, S и L в долях 0–1).
2. `tone` — по среднему значению L по трём цветам:
   - `light` если mean(L) > 0.66;
   - `dark` если mean(L) < 0.33;
   - `medium` иначе.
3. `saturation` — по среднему значению S по трём цветам:
   - `muted` если mean(S) < 0.25;
   - `vivid` если mean(S) > 0.65;
   - `moderate` иначе.
4. `temperature`:
   - `neutral` если mean(S) < 0.15 (палитра близка к ахроматической);
   - иначе считается доля цветов с S ≥ 0.15, попадающих в тёплый сектор hue (0°–60° или 300°–360°);
   - `warm` если тёплых ≥ 2 из 3;
   - `cool` если тёплых ≤ 1 из 3 и при этом есть хотя бы один цвет в секторе 60°–300°;
   - `neutral` в остальных случаях.

---

## clustering_keys: назначение и логика

Ключи — производные строки от других полей, нужные для быстрой группировки и поиска без перебора полной структуры карточки.
- O(1) сравнение карточек по выбранному вектору признаков.
- Индексы и хеш-таблицы для дедупликации и поиска похожих.
- Стабильность кластеров: ключ зависит только от перечисленных полей.

**Три независимых вектора + объединённый:**
- `structural_key` — геометрия и расположение ключевых ролей.
- `visual_key` — фон, палитра, плотность.
- `semantic_key` — категория товара.
- `full_key` — конкатенация трёх. Одинаковый ключ = почти-дубликат.

**Формулы:**

```
structural_key =
  {composition.archetype}__
  {product_main.anchor or "none"}__
  {product_main.product_view or "none"}__
  {group_main.anchor or "none"}__         # самая крупная по площади группа
  {brand_logo.anchor or "none"}__
  {trust_mark.anchor or "none"}__
  {promo_offer.anchor or "none"}

visual_key =
  bg:{background.type}__
  tone:{palette.tone}__sat:{palette.saturation}__temp:{palette.temperature}__
  density:{composition.density}

semantic_key =
  cat:{product_category}

full_key = structural_key + " | " + visual_key + " | " + semantic_key
```

**Правила вычисления:**
- Ключи пересчитываются автоматически при любом изменении исходных полей.

---

## Правила определения «главного» при коллизиях

**Главный товар (`product_main`).** В карточке допустим максимум один `product_main`. Если несколько товарных объектов одинаково претендуют на главного:

1. Главным назначается первый при обходе слева-направо, сверху-вниз (по верхнему-левому углу bbox).
2. При равенстве координат — больший по площади.
3. Остальные становятся `product_secondary`.

Если центром композиции является артефакт/результат, а товар отсутствует, используется `composition.archetype = demo_focus`, и `product_main` может отсутствовать.

**Критерий `group_shot` vs `product_secondary`:**
- Несколько экземпляров в единой композиции, визуально неотделимых — один `product_main` с `product_view = group_shot`.
- Экземпляры разнесены по холсту с самостоятельной и повторяемой геометрией — один `product_main` + N×`product_secondary`.

**Главная группа (`group_main`).** Используется в `structural_key`. Главной считается группа с наибольшей площадью bbox среди всех элементов с `role = group`. При равных площадях (с округлением до 0.05) — первая по обходу слева-направо, сверху-вниз.

---

## Правила нормализации

- Координаты округляются до 0.01.
- Все hex приводятся к нижнему регистру.
- Совмещённые семантики в одном визуальном бейдже разделяются на два соседних `Element` с общим `group_id`. Массивы значений в поле `role` запрещены.
- `semantic.text_content.full_text` формируется конкатенацией `content.text` всех элементов с непустым текстом, в порядке возрастания `z_order`, через разделитель `\n`.
- `semantic.image_meaning.scene_description` — свободный текст, не более 500 символов, без ограничения языка.
- `icon_concept` — свободный текст, не более 30 символов, на языке разметки. Используется описательная форма («щит», «лист», «капля воды»), без эмоциональной окраски и маркетинговых формулировок.
- `product_category = kids` имеет приоритет над остальными категориями, если товар позиционируется как детский: надпись «для детей/детская», детский размерный ряд, целевая аудитория заявлена в заголовке или визуально (персонажи, детские модели, детская стилистика упаковки). Детская одежда → `kids`, а не `apparel`. Детское питание → `kids`, а не `food`.
- `product_category = other` используется только если товар не подпадает ни под одну из 10 остальных категорий. Неуверенность между двумя конкретными категориями — повод выбрать более специфичную, а не `other`.

---

## Валидация

1. В `structural.elements` максимум один элемент с `role = product_main`. При нескольких претендентах главный определяется по правилам раздела «Правила определения "главного" при коллизиях».
2. При `composition.archetype = demo_focus` `product_main` может отсутствовать.
3. Если `product_main` присутствует, его `product_view` обязателен и не null.
4. `structural.elements` содержит только роли из `element_role`.
5. `marketplace_overlay.elements`, если присутствует, содержит только роли из `overlay_role`.
6. Все `relations.parent` ссылаются на существующие `element_id`.
7. Все `group_id` ссылаются на существующий элемент с `role = group`.
8. `arrangement` обязателен и не null для `role ∈ {group, brand_pattern, kit_showcase}`. Для остальных ролей `arrangement = null`.
9. Все селекторы в `generation.hints.*` синтаксически корректны и адресуют только разрешённые разделы (`structural.*`, `visual.*`).
10. Множества полей и элементов, покрываемых `must_keep` и `free_to_change`, не пересекаются.
11. `semantic.image_meaning.scene_description` не превышает 500 символов.
12. `Element.visual.icon_concept`, если не null, не превышает 30 символов.
13. `visual.palette.tone`, `saturation`, `temperature` соответствуют значениям, вычисляемым по правилам из раздела «Правила вычисления tone / saturation / temperature», на основе `visual.palette.dominant`.
14. `canvas.safe_areas` соответствует значениям, вычисляемым по правилам из раздела «safe_areas: механика и расчёт», на основе `marketplace_overlay.elements`. Все поля в [0..1]; `top + bottom < 1.0`; `left + right < 1.0`.

---

Бэклог:

1. Проверить спецификацию на реальных разметках (согласие между разметчиками, покрытие enum, неоднозначности ролей).
2. Проверить спецификацию на реальных генерациях (работоспособность `generation.hints`, адекватность результата).
3. Адаптировать под слабые VLM: определить метрику «повторяемого качества», целевой порог и тестовый набор.
[Промпт разметчика](../../undefined)