# Test Evidence — Current MVP

## Сводная таблица

| Тест | Сценарий | Фактический результат |
|---|---|---|
| A | CRM `delivered` + Carrier `delivered` | `automatic_processing` |
| B | `delivery_not_received` | `human_handoff` |
| C | CRM и Carrier расходятся | `human_handoff` |
| D | неизвестный заказ | `404 / mock order not found` |

## Test A — automatic path

```text
order_id = 84721
customer_id = 551
request_type = ""
customer_message = "Тестовый запрос."
```

```text
crm_status       = delivered
carrier_status   = delivered
routing_decision = automatic
action           = automatic_processing
```

## Test B — primary customer complaint

```text
order_id = 84721
customer_id = 551
request_type = delivery_not_received
customer_message = "Заказ отмечен доставленным, но я его не получил."
```

```text
crm_status       = delivered
carrier_status   = delivered
routing_decision = human_handoff
action           = human_handoff
```

## Test C — source mismatch

```text
order_id = 84722
customer_id = 552
request_type = ""
customer_message = "Тест: статусы источников расходятся."
```

```text
crm_status       = pending
carrier_status   = in_transit
routing_decision = human_handoff
action           = human_handoff
```

## Test D — unknown order

```text
order_id = 99999
customer_id = 999
request_type = ""
customer_message = "Тест: заказ не существует."
```

```text
404
mock order not found
```

Routing decision после failed lookup не создаётся.

## Интерпретация

Все четыре текущих проверки соответствуют настроенным demo rules.

Это демонстрационный набор тестов, а не production performance evaluation. По нему не следует делать вывод о production accuracy, ROI или финансовом эффекте.
