def recalcular_totales(orden):

    subtotal = 0
    costo_total = 0

    for p in orden["productos"]:
        subtotal += p["cantidad"] * p["precio"]
        costo_total += p["cantidad"] * p["costo"]

    total = subtotal - orden.get("descuento_global", 0) + orden.get("gasto_extra", 0)
    ganancia = total - costo_total

    orden["subtotal"] = subtotal
    orden["total"] = total
    orden["ganancia"] = ganancia

    return orden