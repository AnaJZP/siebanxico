# siebanxico

Series del **Sistema de Información Económica (SIE) de Banco de México** en un
`DataFrame`, con el token fuera del código y las transformaciones habituales
para analizar inflación, tipo de cambio y tasas.

> Librería **no oficial**. No está afiliada ni respaldada por Banco de México.

```python
import siebanxico as sie

df = sie.descargar(["inpc", "fix", "tasa_objetivo"], inicio="2015-01-01")
sie.inflacion(df["inpc"]).tail()
```

## Instalación

Se instala directamente desde GitHub (también en Google Colab, anteponiendo `!`):

```bash
pip install "siebanxico[analisis] @ git+https://github.com/AnaJZP/BanxicoLab.git"
```

Para desarrollar, clona el repositorio e instala en modo editable:

```bash
pip install -e ".[dev]"
```

`[analisis]` agrega `statsmodels` (desestacionalización y prueba ADF) y `matplotlib`; sin ellos,
todo lo demás funciona igual. Requiere Python ≥ 3.10 y pandas ≥ 2.2.

## El token, sin exponerlo

El token gratuito se genera en
<https://www.banxico.org.mx/SieAPIRest/service/v1/token>. Guárdalo **una sola vez**:

```bash
siebanxico token
```

Se pide sin mostrarlo en pantalla y queda en un archivo que solo tu usuario
puede leer. A partir de ahí ningún notebook ni script necesita contenerlo. La
librería lo busca en este orden:

1. variable de entorno `BANXICO_TOKEN` (o `BMX_TOKEN`),
2. *Secrets* de Google Colab con ese mismo nombre,
3. el archivo guardado con `siebanxico token`,
4. si nada de lo anterior existe, lo pregunta con `getpass`.

Además, el token viaja en un encabezado HTTP y no en la URL, así que no aparece
en mensajes de error, y `repr(cliente)` solo muestra los últimos 4 caracteres.

## Descargar

```python
import siebanxico as sie

# Por alias, por identificador del SIE, o con nombres propios para las columnas
sie.descargar("inpc")
sie.descargar(["SP1", "SF43718"], "2000-01-01", "2026-12-31")
sie.descargar({"SF43718": "FIX", "SF61745": "Objetivo"}, inicio="2020-01-01")

sie.catalogo()  # alias disponibles
sie.buscar("subyacente")  # busca en el catálogo de Banxico (sin token)
sie.metadatos(["inpc", "fix"])  # periodicidad, unidad, cobertura
sie.oportuno(["fix", "tasa_objetivo"])  # último dato publicado
```

`descargar` devuelve un `DataFrame` con `DatetimeIndex` y valores `float`. Se
encarga de lo que suele fallar en silencio: fechas `dd/mm/aaaa`, `N/E`, comas
de miles, más de 20 series por consulta, reintentos y límite de consultas.

## Analizar

```python
diarias = sie.descargar(["fix", "tasa_objetivo", "cetes_28"], "2000-01-01")
mensual = sie.a_mensual(
    diarias, {"fix": "ultimo", "tasa_objetivo": "promedio", "cetes_28": "promedio"}
)
inpc = sie.serie("inpc", "2000-01-01")

sie.inflacion(inpc)  # mensual, anual, acumulada, anualizada
sie.a_pesos_de(1000, "2010-01-01", "2026-01-01", inpc)  # poder adquisitivo
sie.deflactar(mensual["fix"], inpc, base="2018-07-01")  # pesos constantes
sie.tasa_real(mensual["cetes_28"], sie.variacion_anual(inpc))  # Fisher exacta
sie.indice_base(mensual, "2018-01-01")  # base 100 para comparar
sie.prueba_adf({"nivel": inpc, "Δln": sie.variacion(inpc, log=True)})
```

## Inflación: mercado y pronósticos

```python
bmx = sie.Banxico()

bmx.inflacion_implicita(10, "2015-01-01")  # rendimiento de Bono M y Udibono, e implícita
sie.rendimiento_bono(90.63, cupon=8.0, plazo_dias=3426)  # convención mexicana 182/360

sie.impulso(sie.serie("inpc_subyacente"), 3)  # 3m/3m anualizado
sie.pronosticar_inflacion(inpc, 12)  # SARIMA con intervalo
sie.evaluar_pronosticos(inpc, desde="2012-01-01")  # error fuera de muestra vs. método ingenuo
```

## Documentación

La guía completa y la referencia de cada función están en `docs/`. Para verla
como sitio web:

```bash
pip install -e ".[docs]"
mkdocs serve
```

## Ejemplos

- `examples/inicio_rapido.ipynb`: descarga, inflación y tasa real en pocas celdas.
- `examples/seminario_transformaciones.ipynb`: el seminario completo de
  transformaciones, con cada una justificada y verificada con la prueba ADF.
- `examples/inflacion_mercado_y_pronosticos.ipynb`: medidas de tendencia, inflación
  implícita en Bonos M y Udibonos, y pronósticos evaluados fuera de muestra.

## Desarrollo

```bash
pip install -e ".[dev]"
pytest              # pruebas sin red
pytest -m red       # verifica el catálogo de alias contra Banxico (sin token)
```

## Autoría

Ana Lorena Jiménez Preciado · Escuela Superior de Economía, Instituto Politécnico Nacional.

## Licencia

MIT. Los datos pertenecen a Banco de México y están sujetos a sus
[términos de uso](https://www.banxico.org.mx/SieAPIRest/service/v1/doc/salvedad).
