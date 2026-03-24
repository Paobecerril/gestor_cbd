def calcular_finanzas(ventas, gastos):

    ingresos = sum(v["total"] for v in ventas)

    gastos_total = sum(g["monto"] for g in gastos)

    ganancia = ingresos - gastos_total

    return ingresos, gastos_total, ganancia