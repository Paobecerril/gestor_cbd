from models.ventas import obtener_ventas


def sugerir_precio(cliente, producto):

    ventas = obtener_ventas()

    precios = []

    for venta in ventas:

        if venta["cliente"] == cliente:

            for p in venta["productos"]:

                if p["producto"] == producto:

                    precios.append(p["precio"])

    if len(precios) == 0:
        return None

    return round(sum(precios) / len(precios), 2)