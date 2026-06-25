def calculate(fields: dict) -> list:
    """
    計算結果を返す

    Parameters
    ----------
    fields : dict
        {
            "total_cny": 5000,
            "exchange_rate": 20.5
        }
    """

    results = []

    total_cny = fields.get("total_cny")
    exchange_rate = fields.get("exchange_rate")

    if (
        total_cny is not None
        and exchange_rate is not None
    ):
        total_jpy = total_cny * exchange_rate

        results.append(
            {
                "key": "total_jpy",
                "value": total_jpy,
                "source": "calculated",
                "formula": "total_cny * exchange_rate",
            }
        )

    return results