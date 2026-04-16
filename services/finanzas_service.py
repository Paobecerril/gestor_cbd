def calcular_finanzas(ventas, gastos):

    ingresos = sum(v["total"] for v in ventas)

    gastos_total = sum(g["monto"] for g in gastos)

    # Ganancia = (precio_venta - costo_base) × cantidad por producto,
    # menos el gasto extra de envío de cada orden
    ganancia = 0.0
    for v in ventas:
        for p in v.get("productos", []):
            precio   = float(p.get("precio",   0))
            costo    = float(p.get("costo",    0))
            cantidad = int(p.get("cantidad",   1))
            ganancia += (precio - costo) * cantidad
        ganancia -= float(v.get("gasto_extra", 0))

    return ingresos, gastos_total, ganancia