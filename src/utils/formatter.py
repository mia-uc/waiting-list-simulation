import locale


def formatear_moneda(valor):
    """
    Formatea un valor numérico como una cadena de texto con formato monetario.

    :param valor: El valor numérico a formatear.
    :param locale_str: La configuración regional a usar para el formateo.
    :return: Una cadena de texto con el valor formateado como moneda.
    """
    locale.setlocale(locale.LC_ALL, '')
    return locale.currency(valor, grouping=True)
