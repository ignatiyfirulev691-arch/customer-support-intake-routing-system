# Customer Support Intake & Routing System

Портфолио-прототип автоматизации обработки обращений клиентов в e-commerce.

## 1. Что я построил

Я спроектировал и реализовал workflow для маршрутизации post-purchase обращений на основе:

- контекста обращения клиента;
- данных о заказе из CRM;
- данных о доставке из системы перевозчика.

Основной сценарий проекта:

> Заказ отмечен как доставленный, но клиент сообщает, что его не получил.

Прототип получает входные данные, обращается к двум источникам, объединяет полученную информацию, применяет явные правила маршрутизации и направляет кейс либо в автоматическую обработку, либо на передачу человеку.

В проект входят:

- рабочий n8n workflow;
- Mock CRM API на Python;
- Mock Carrier API на Python;
- тестовые сценарии;
- результаты выполнения;
- evidence по ключевым веткам;
- документация по архитектуре, решениям, debugging и ограничениям.

---

## 2. Бизнес-проблема

При обработке post-purchase обращения оператору может быть недостаточно только сообщения клиента.

Для принятия решения по кейсу необходимо:

1. учесть контекст обращения;
2. получить данные о заказе;
3. получить статус доставки;
4. сопоставить информацию из разных источников;
5. определить, допустима ли автоматическая обработка;
6. передать кейс человеку, если требуется дополнительная проверка.

В данном прототипе этот процесс реализован для сценария с доставкой: заказ имеет статус `delivered`, но клиент сообщает, что фактически его не получил.

### Цель прототипа

Показать полный путь от входящего обращения до маршрутизации кейса с:

- понятной архитектурой;
- явными правилами;
- проверяемыми результатами;
- отдельными ветками для автоматической обработки и human handoff;
- зафиксированными ограничениями MVP.

---

## 3. Архитектура

### Общая схема

```text
Запрос клиента
      |
      v
    n8n
      |
      +----------------------+
      |                      |
      v                      v
  Mock CRM API        Mock Carrier API
      |                      |
      +----------+-----------+
                 |
                 v
               Merge
                 |
                 v
      Determine Routing Decision
                 |
                 v
          Route by Decision
             /         \
            v           v
Automatic Processing  Human Handoff
```

### Роли компонентов

| Компонент | Роль в системе |
|---|---|
| `n8n` | оркестрация workflow и передача данных между шагами |
| `Mock CRM API` | получение данных заказа и CRM-статуса |
| `Mock Carrier API` | получение статуса доставки |
| `Merge` | объединение данных из двух источников |
| `Determine Routing Decision` | применение логики маршрутизации |
| `Route by Decision` | выбор дальнейшей ветки |
| `Automatic Processing` | результат автоматической обработки |
| `Human Handoff` | передача кейса человеку |

### Разделение ответственности

В прототипе компоненты разделены по ролям:

- `n8n` отвечает за orchestration;
- Python Mock API имитируют внешние системы и предоставляют данные для workflow;
- `Determine Routing Decision` содержит логику маршрутизации;
- финальные ветки отражают результат принятого решения.

Такое разделение позволяет отдельно изменять интеграции, workflow и правила маршрутизации.

---

## 4. Как работает workflow

### Шаг 1. Test Input

Workflow получает тестовые входные данные:

```text
order_id
customer_id
request_type
customer_message
```

В текущем MVP `request_type` используется как структурированный контекст обращения. `customer_message` переносится через workflow и сохраняется в итоговом результате.

### Шаг 2. Получение данных из CRM

`CRM - Get Order` делает HTTP-запрос:

```text
GET http://127.0.0.1:5000/crm/order
```

Передаются:

```text
order_id
customer_id
```

Mock CRM возвращает статус заказа либо ошибку `404`.

### Шаг 3. Получение данных перевозчика

`Carrier - Get Tracking` делает HTTP-запрос:

```text
GET http://127.0.0.1:5001/carrier/tracking
```

Передаются:

```text
order_id
customer_id
```

Mock Carrier возвращает tracking status либо ошибку `404`.

### Шаг 4. Нормализация данных

Отдельные узлы:

```text
Prepare CRM Status
Prepare Carrier Status
```

приводят ответы источников к полям, которые используются дальше в workflow:

```text
crm_status
carrier_status
```

При этом контекст обращения переносится дальше в единый набор данных.

### Шаг 5. Merge

`Merge` объединяет результаты CRM и Carrier по позиции.

На выходе routing logic получает единую структуру данных.

### Шаг 6. Determine Routing Decision

`Determine Routing Decision` применяет детерминированные правила и создаёт:

```text
routing_decision
```

В текущем MVP используются значения:

```text
automatic
human_handoff
```

### Шаг 7. Route by Decision

`Route by Decision` проверяет значение:

```text
routing_decision == "automatic"
```

Если условие выполняется, кейс идёт в:

```text
Automatic Processing
```

Иначе:

```text
Human Handoff
```

---

## 5. Правила маршрутизации

Следующие правила являются **демо-правилами прототипа**, а не подтверждённой production policy.

### Правило 1. Оба источника подтверждают доставку

Если:

```text
CRM     = delivered
Carrier = delivered
```

и запрос не имеет типа:

```text
delivery_not_received
```

то:

```text
routing_decision = automatic
action           = automatic_processing
```

### Правило 2. Клиент сообщает, что заказ не получен

Если:

```text
request_type = delivery_not_received
```

то:

```text
routing_decision = human_handoff
action           = human_handoff
```

Это позволяет не отправлять потенциально спорный кейс в автоматическую обработку только потому, что оба источника показывают `delivered`.

### Правило 3. Источники расходятся

Если CRM и Carrier не подтверждают одинаковый статус доставки, прототип направляет кейс человеку:

```text
routing_decision = human_handoff
action           = human_handoff
```

### Правило 4. Заказ не найден

Если внешний lookup не находит заказ, Mock API возвращает:

```text
404
mock order not found
```

Текущий MVP останавливается на этой ошибке и не делает вид, что может безопасно принять routing decision без необходимого контекста.

---

## 6. Mock API

### Mock CRM API

Файл:

```text
app.py
```

Endpoint:

```text
GET http://127.0.0.1:5000/crm/order
```

Параметры:

```text
order_id
customer_id
```

API:

- проверяет наличие обязательных параметров;
- проверяет, что параметры имеют корректный тип;
- проверяет соответствие заказа и клиента;
- возвращает статус заказа;
- возвращает `404`, если заказ не найден или не принадлежит указанному клиенту.

### Mock Carrier API

Файл:

```text
carrier_api.py
```

Endpoint:

```text
GET http://127.0.0.1:5001/carrier/tracking
```

Параметры:

```text
order_id
customer_id
```

API:

- проверяет наличие обязательных параметров;
- проверяет корректность типов;
- проверяет соответствие заказа и клиента;
- возвращает tracking status;
- возвращает `404` при отсутствии заказа.

### Demo data

В проекте используются детерминированные данные:

| Order | Customer | CRM | Carrier |
|---|---:|---|---|
| `84721` | `551` | `delivered` | `delivered` |
| `84722` | `552` | `pending` | `in_transit` |

Данные являются mock-данными для демонстрации.

---

## 7. Тестирование

В текущем MVP выполнены четыре проверки.

| Тест | Сценарий | Фактический результат |
|---|---|---|
| A | CRM `delivered` + Carrier `delivered` | `automatic_processing` |
| B | `delivery_not_received` | `human_handoff` |
| C | CRM и Carrier расходятся | `human_handoff` |
| D | неизвестный заказ | `404 / mock order not found` |

### Тест A — автоматическая обработка

Вход:

```text
order_id = 84721
customer_id = 551
request_type = ""
customer_message = "Тестовый запрос."
```

Результат:

```text
crm_status       = delivered
carrier_status   = delivered
routing_decision = automatic
action           = automatic_processing
```

### Тест B — основной сценарий проекта

Вход:

```text
order_id = 84721
customer_id = 551
request_type = delivery_not_received
customer_message = "Заказ отмечен доставленным, но я его не получил."
```

Результат:

```text
crm_status       = delivered
carrier_status   = delivered
routing_decision = human_handoff
action           = human_handoff
```

### Тест C — рассинхронизация источников

Вход:

```text
order_id = 84722
customer_id = 552
request_type = ""
customer_message = "Тест: статусы источников расходятся."
```

Результат:

```text
crm_status       = pending
carrier_status   = in_transit
routing_decision = human_handoff
action           = human_handoff
```

### Тест D — неизвестный заказ

Вход:

```text
order_id = 99999
customer_id = 999
request_type = ""
customer_message = "Тест: заказ не существует."
```

Результат:

```text
404
mock order not found
```

После ошибки lookup routing decision не создаётся.

---

## 8. Evidence

В папке:

```text
evidence/
```

предусмотрены четыре скриншота выполнения workflow:

```text
test-a-automatic-processing.png
test-b-delivery-not-received.png
test-c-source-mismatch.png
test-d-unknown-order.png
```

Они используются как визуальное подтверждение того, что ключевые ветки действительно были запущены и проверены.

---

## 9. Debugging: что пришлось исправить

Во время реализации workflow возникла проблема: routing logic получала `undefined`/неожиданные значения, хотя поля визуально выглядели корректно в интерфейсе n8n.

Причина оказалась в скрытых пробелах в названиях полей.

В частности, были проблемы с именами вида:

```text
crm_status
carrier_status
request_type
```

После проверки фактической структуры данных были обнаружены лишние пробелы, из-за которых выражения JavaScript обращались не к тем ключам.

Поля были приведены к точным именам:

```text
crm_status
carrier_status
request_type
```

После исправления workflow начал корректно передавать данные в routing logic.

Этот эпизод важен как часть инженерного процесса: проблема была обнаружена через фактический execution output, локализована на уровне data contract и исправлена без перестройки всей архитектуры.

---

## 10. Оценка результата

Текущие тесты демонстрируют, что MVP умеет:

- получать данные из CRM;
- получать tracking data;
- объединять результаты двух источников;
- сохранять контекст обращения;
- применять детерминированные routing rules;
- отправлять кейс в automatic processing;
- отправлять кейс в human handoff;
- останавливать workflow при неизвестном заказе.

Эти четыре теста являются **демонстрационным набором**, а не статистической оценкой качества системы.

По этим данным не делается вывод о production accuracy, ROI или финансовом эффекте.

Для полноценной оценки потребуются:

- более крупный размеченный тестовый набор;
- ожидаемый результат для каждого кейса;
- baseline текущего процесса;
- согласованный acceptance threshold;
- отдельный анализ ошибок.

---

## 11. Ограничения прототипа

Это portfolio MVP с mock-интеграциями.

В проекте пока нет:

- реального CRM;
- реальной интеграции с перевозчиком;
- production authentication;
- production deployment;
- persistent storage;
- production monitoring / observability;
- полного набора production error-handling сценариев;
- подтверждённой production policy для reconciliation конфликтующих источников;
- полного набора бизнес-правил автоматизации.

Отдельно важно: правила маршрутизации, использованные в MVP, являются правилами демонстрационного прототипа. Они не представлены как согласованная политика реального бизнеса.

---

## 12. Как запустить локально

### 1. CRM

Установить Flask:

```bash
pip install flask
```

Запустить:

```bash
python app.py
```

CRM будет доступен по адресу:

```text
http://127.0.0.1:5000
```

### 2. Carrier

Во втором терминале запустить:

```bash
python carrier_api.py
```

Carrier будет доступен по адресу:

```text
http://127.0.0.1:5001
```

### 3. n8n

Запустить локальный n8n и открыть workflow:

```text
Customer Support Intake & Routing System
```

В workflow используются локальные endpoints:

```text
CRM     → http://127.0.0.1:5000
Carrier → http://127.0.0.1:5001
```

---

## 13. Файлы проекта

```text
Customer_Support_Intake_Routing_Portfolio/
│
├── README.md
├── PROJECT_LOG.md
├── TEST_EVIDENCE.md
├── EVIDENCE_HANDOFF.md
├── customer_support_intake_routing_system.json
├── app.py
├── carrier_api.py
└── evidence/
    ├── test-a-automatic-processing.png
    ├── test-b-delivery-not-received.png
    ├── test-c-source-mismatch.png
    └── test-d-unknown-order.png
```

Файл:

```text
customer_support_intake_routing_system.json
```

содержит экспорт n8n workflow.

---

## 14. Что демонстрирует этот проект

Проект показывает полный путь:

```text
Бизнес-проблема
      ↓
Декомпозиция процесса
      ↓
Архитектура
      ↓
Интеграции
      ↓
Workflow orchestration
      ↓
Business rules
      ↓
Testing
      ↓
Debugging
      ↓
Evidence
      ↓
Документация
```

Основной акцент проекта — не на количестве инструментов, а на том, как бизнес-сценарий переводится в конкретный проверяемый workflow с явными правилами, результатами и ограничениями.
