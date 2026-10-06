"""Alias legibles para las series más usadas del SIE.

Permite escribir ``descargar("inpc")`` en lugar de recordar ``"SP1"``. Todas las
claves de este catálogo fueron contrastadas con el catálogo público del SIE;
``tests/test_red.py`` repite esa verificación.

El campo ``agregacion`` indica cómo llevar la serie a una frecuencia menor:
``"ultimo"`` para precios y saldos (el promedio suaviza artificialmente la
volatilidad) y ``"promedio"`` para tasas de interés.
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass

import pandas as pd

from .errores import SerieNoEncontrada

_ID = re.compile(r"^S[A-Z]\d+$", re.IGNORECASE)


@dataclass(frozen=True)
class Serie:
    """Entrada del catálogo de alias."""

    id: str
    descripcion: str
    periodicidad: str
    unidad: str
    agregacion: str = "ultimo"


CATALOGO: dict[str, Serie] = {
    # ── Precios ──────────────────────────────────────────────────────────────
    "inpc": Serie("SP1", "INPC, índice general", "Mensual", "Índice"),
    "inpc_subyacente": Serie("SP74625", "INPC subyacente", "Mensual", "Índice"),
    "inpc_no_subyacente": Serie("SP74630", "INPC no subyacente", "Mensual", "Índice"),
    "inflacion_mensual": Serie("SP30577", "INPC, variación mensual", "Mensual", "%"),
    "inflacion_anual": Serie("SP30578", "INPC, variación anual", "Mensual", "%"),
    "inflacion_acumulada": Serie("SP30579", "INPC, variación acumulada en el año", "Mensual", "%"),
    "inflacion_subyacente_anual": Serie("SP74662", "Inflación subyacente anual", "Mensual", "%"),
    "inflacion_no_subyacente_anual": Serie(
        "SP74665", "Inflación no subyacente anual", "Mensual", "%"
    ),
    "inpc_quincenal": Serie("SP8664", "INPC quincenal, índice general", "Quincenal", "Índice"),
    "inpc_subyacente_quincenal": Serie(
        "SP74632", "INPC subyacente quincenal", "Quincenal", "Índice"
    ),
    "inflacion_anual_quincenal": Serie(
        "SP74833", "INPC quincenal, variación anual", "Quincenal", "%"
    ),
    "media_truncada": Serie(
        "SP74831", "Indicador de media truncada, general (anual)", "Mensual", "%"
    ),
    "media_truncada_subyacente": Serie(
        "SP74832", "Indicador de media truncada, subyacente (anual)", "Mensual", "%"
    ),
    "udis": Serie("SP68257", "Valor de la UDI", "Diaria", "Pesos por UDI"),
    # ── Expectativas de inflación (encuesta de Banxico a especialistas, mediana) ──
    "expectativa_inflacion_12m": Serie(
        "SR14195", "Expectativa de inflación general, próximos 12 meses", "Mensual", "%"
    ),
    "expectativa_inflacion_cierre": Serie(
        "SR14139", "Expectativa de inflación general, cierre del año en curso", "Mensual", "%"
    ),
    "expectativa_inflacion_cierre_siguiente": Serie(
        "SR14146", "Expectativa de inflación general, cierre del año siguiente", "Mensual", "%"
    ),
    # ── Tipo de cambio ───────────────────────────────────────────────────────
    "fix": Serie("SF43718", "Tipo de cambio FIX, fecha de determinación", "Diaria", "MXN/USD"),
    "fix_liquidacion": Serie(
        "SF60653", "Tipo de cambio FIX, fecha de liquidación", "Diaria", "MXN/USD"
    ),
    "fix_promedio_mensual": Serie(
        "SF17908", "Tipo de cambio FIX, promedio del mes", "Mensual", "MXN/USD"
    ),
    "euro": Serie("SF46410", "Pesos por euro", "Diaria", "MXN/EUR"),
    # ── Tasas de interés ─────────────────────────────────────────────────────
    "tasa_objetivo": Serie("SF61745", "Tasa objetivo de Banxico", "Diaria", "% anual", "promedio"),
    "tiie_fondeo": Serie(
        "SF331451", "TIIE de fondeo a un día hábil", "Diaria", "% anual", "promedio"
    ),
    "tiie_28": Serie("SF43783", "TIIE a 28 días", "Diaria", "% anual", "promedio"),
    "cetes_28": Serie(
        "SF60633", "Cetes a 28 días, subasta semanal", "Diaria", "% anual", "promedio"
    ),
    "cetes_91": Serie(
        "SF60634", "Cetes a 91 días, subasta semanal", "Diaria", "% anual", "promedio"
    ),
    "bono_10a": Serie(
        "SF44071", "Bono M a 10 años, tasa de la subasta", "Diaria", "% anual", "promedio"
    ),
    "udibono_10a": Serie(
        "SF43924", "Udibono a 10 años, tasa real de la subasta", "Diaria", "% anual", "promedio"
    ),
    # ── Actividad, sector externo y dinero ───────────────────────────────────
    "igae": Serie("SR17692", "IGAE base 2018, serie original", "Mensual", "Índice"),
    "igae_desestacionalizado": Serie(
        "SR17693", "IGAE base 2018, serie desestacionalizada", "Mensual", "Índice"
    ),
    "reservas": Serie("SF43707", "Reserva internacional", "Diaria", "Millones de USD"),
    "remesas": Serie("SE27803", "Remesas familiares, total", "Mensual", "Millones de USD", "suma"),
    "m1": Serie("SF311408", "Agregado monetario M1", "Mensual", "Miles de pesos"),
    "m2": Serie("SF311418", "Agregado monetario M2", "Mensual", "Miles de pesos"),
    "salario_minimo": Serie("SL11298", "Salario mínimo general", "Mensual", "Pesos por día"),
}


def es_id(clave: str) -> bool:
    """``True`` si ``clave`` tiene forma de identificador del SIE (``SF43718``)."""
    return bool(_ID.match(clave.strip()))


def resolver(clave: str) -> tuple[str, str]:
    """Convierte un alias o un identificador en ``(id_serie, nombre_de_columna)``.

    Raises
    ------
    SerieNoEncontrada
        Si no es un identificador válido ni un alias del catálogo.
    """
    limpia = clave.strip()
    if limpia.lower() in CATALOGO:
        return CATALOGO[limpia.lower()].id, limpia.lower()
    if es_id(limpia):
        return limpia.upper(), limpia.upper()
    parecidas = difflib.get_close_matches(limpia.lower(), CATALOGO, n=3, cutoff=0.5)
    pista = f" ¿Quisiste decir {', '.join(map(repr, parecidas))}?" if parecidas else ""
    raise SerieNoEncontrada(
        f"{clave!r} no es un identificador del SIE (p. ej. 'SF43718') ni un alias conocido."
        f"{pista} Consulta siebanxico.catalogo() o usa siebanxico.buscar('texto')."
    )


def catalogo() -> pd.DataFrame:
    """Tabla con los alias disponibles."""
    filas = [
        {
            "alias": alias,
            "id": s.id,
            "descripcion": s.descripcion,
            "periodicidad": s.periodicidad,
            "unidad": s.unidad,
            "agregacion": s.agregacion,
        }
        for alias, s in CATALOGO.items()
    ]
    return pd.DataFrame(filas).set_index("alias")
