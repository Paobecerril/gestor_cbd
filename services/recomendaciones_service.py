from models.ordenes import obtener_ordenes


def sugerir_precio(cliente, producto):

    ventas = [
        o for o in obtener_ordenes()
        if o.get("estado_general") == "confirmada" and o.get("activo", True)
    ]

    precios = []

    for venta in ventas:

        if venta["cliente"] == cliente:

            for p in venta["productos"]:

                if p["producto"] == producto:

                    precios.append(p["precio"])

    if len(precios) == 0:
        return None

    return round(sum(precios) / len(precios), 2)