import numpy as np
import io
import math
import contextlib

from ai.commons.enums import EutrophicationLevel

from ai.fuzzy.componentes.nitrogen import NivelNitrogeno
from ai.fuzzy.componentes.physical import CondicionesFisicas
from ai.fuzzy.componentes.nutrients import NivelNutrientes
from ai.fuzzy.componentes.aditional import CondicionesAdicionales
from ai.fuzzy.componentes.chemical import CondicionesQuimicas
from ai.fuzzy.componentes.eutrophication import NivelEutrofizacion
from ai.fuzzy.componentes.oxygen import BalanceOxigeno
from ai.fuzzy.componentes.solids import NivelSolidos
from ai.fuzzy.componentes.visibility import NivelVisibilidad
from ai.fuzzy.componentes.phosphorus import NivelFosforo

class MotorDifuso:
    def __init__(self, **kwargs) -> None:
        self.fase = 4
        self.variables = kwargs

        self.entradas = {}

        self.cadena = {
            'nitrogeno': {
                'variables': '-',
                'confianza': 0.0,
                'valor': np.nan,
                'etiqueta': 'DESCONOCIDO'
            },
            'fosforo': {
                'variables': '-',
                'confianza': 0.0,
                'valor': np.nan,
                'etiqueta': 'DESCONOCIDO'
            },
            'oxigeno': {
                'variables': '-',
                'confianza': 0.0,
                'valor': np.nan,
                'etiqueta': 'DESCONOCIDO'
            },
            'solidos': {
                'variables': '-',
                'confianza': 0.0,
                'valor': np.nan,
                'etiqueta': 'DESCONOCIDO'
            },
            'visibilidad': {
                'variables': '-',
                'confianza': 0.0,
                'valor': np.nan,
                'etiqueta': 'DESCONOCIDO'
            },
            'adicionales': {
                'variables': '-',
                'confianza': 0.0,
                'valor': np.nan,
                'etiqueta': 'DESCONOCIDO'
            },
            'fisicas': {
                'variables': '-',
                'confianza': 0.0,
                'valor': np.nan,
                'etiqueta': 'DESCONOCIDO'
            },
            'nutrientes': {
                'variables': '-',
                'confianza': 0.0,
                'valor': np.nan,
                'etiqueta': 'DESCONOCIDO'
            },
            'quimicas': {
                'variables': '-',
                'confianza': 0.0,
                'valor': np.nan,
                'etiqueta': 'DESCONOCIDO'
            },
            'eutrofizacion': {
                'variables': '-',
                'confianza': 0.0,
                'valor': np.nan,
                'etiqueta': 'DESCONOCIDO'
            }
        }

        self.errores = {}

    def fijar_fase(self, *, fase: int) -> None:
        self.fase = fase

    def ejecutar(self) -> None:
        if self.fase >= 1:
            self._inferir_nitrogeno()
            self._inferir_fosforo()
            self._inferir_oxigeno()
            self._inferir_solidos()
            self._inferir_visibilidad()
            self._inferir_adicionales()

            confianza_fase_1 = (
                self.cadena['nitrogeno']['confianza'] +
                self.cadena['fosforo']['confianza'] +
                self.cadena['oxigeno']['confianza'] +
                self.cadena['solidos']['confianza'] +
                self.cadena['visibilidad']['confianza'] +
                self.cadena['adicionales']['confianza']
            ) / 6.0

        if self.fase >= 2:

            self._inferir_nutrientes()
            confianza_fase_2 = self.cadena['nutrientes']['confianza']

        if self.fase >= 3:
            self._inferir_fisicas()
            self._inferir_quimicas()
            confianza_fase_3 = (
                self.cadena['fisicas']['confianza'] +
                self.cadena['quimicas']['confianza']
            ) / 2.0

        if self.fase >= 4:
            self._inferir_eutrofizacion()

            confianza_fase_4 = self.cadena['eutrofizacion']['confianza']
            confianza_final = (
                confianza_fase_1 +
                confianza_fase_2 +
                confianza_fase_3 +
                confianza_fase_4
            ) / 4.0

            self.cadena['eutrofizacion']['confianza'] = confianza_final

    def _inferir_nitrogeno(self) -> None:
        try:
            modelo = NivelNitrogeno(**self.variables)
            variables = modelo.calcular_inferencia()
            valor = modelo.nivel_nitrogeno
            etiqueta = modelo.obtener_etiqueta()

            self.entradas['nitrogeno'] = modelo.available_vars

            self.cadena['nitrogeno']['variables'] = variables
            self.cadena['nitrogeno']['confianza'] = 1.0
            self.cadena['nitrogeno']['valor'] = valor
            self.cadena['nitrogeno']['etiqueta'] = etiqueta

        except Exception as e:
            self.errores['nitrogeno'] = str(e)

    def _inferir_fosforo(self) -> None:
        try:
            modelo = NivelFosforo(**self.variables)
            variables = modelo.calcular_inferencia()
            valor = modelo.nivel_fosforo
            etiqueta = modelo.obtener_etiqueta()

            self.entradas['fosforo'] = modelo.available_vars

            self.cadena['fosforo']['variables'] = variables
            self.cadena['fosforo']['confianza'] = 1.0
            self.cadena['fosforo']['valor'] = valor
            self.cadena['fosforo']['etiqueta'] = etiqueta

        except Exception as e:
            self.errores['fosforo'] = str(e)

    def _inferir_oxigeno(self) -> None:
        try:
            modelo = BalanceOxigeno(**self.variables)
            variables = modelo.calcular_inferencia()
            valor = modelo.balance_oxigeno
            etiqueta = modelo.obtener_etiqueta()

            self.entradas['oxigeno'] = modelo.available_vars

            self.cadena['oxigeno']['variables'] = variables
            self.cadena['oxigeno']['confianza'] = 1.0
            self.cadena['oxigeno']['valor'] = valor
            self.cadena['oxigeno']['etiqueta'] = etiqueta

        except Exception as e:
            self.errores['oxigeno'] = str(e)

    def _inferir_solidos(self) -> None:
        try:
            modelo = NivelSolidos(**self.variables)
            variables = modelo.calcular_inferencia()
            valor = modelo.nivel_solidos
            etiqueta = modelo.obtener_etiqueta()

            self.entradas['solidos'] = modelo.available_vars

            self.cadena['solidos']['variables'] = variables
            self.cadena['solidos']['confianza'] = 1.0
            self.cadena['solidos']['valor'] = valor
            self.cadena['solidos']['etiqueta'] = etiqueta

        except Exception as e:
            self.errores['solidos'] = str(e)

    def _inferir_visibilidad(self) -> None:
        try:
            modelo = NivelVisibilidad(**self.variables)
            variables = modelo.calcular_inferencia()
            valor = modelo.nivel_visibilidad
            etiqueta = modelo.obtener_etiqueta()

            self.entradas['visibilidad'] = modelo.available_vars

            self.cadena['visibilidad']['variables'] = variables
            self.cadena['visibilidad']['confianza'] = 1.0
            self.cadena['visibilidad']['valor'] = valor
            self.cadena['visibilidad']['etiqueta'] = etiqueta

        except Exception as e:
            self.errores['visibilidad'] = str(e)

    def _inferir_adicionales(self) -> None:
        try:
            modelo = CondicionesAdicionales(**self.variables)

            variables, confianza = modelo.calcular_inferencia()
            valor = modelo.condiciones
            etiqueta = modelo.obtener_etiqueta()

            self.entradas['adicionales'] = modelo.available_vars

            self.cadena['adicionales']['variables'] = variables
            self.cadena['adicionales']['confianza'] = confianza
            self.cadena['adicionales']['valor'] = valor
            self.cadena['adicionales']['etiqueta'] = etiqueta

        except Exception as e:
            self.errores['adicionales'] = str(e)

    def _inferir_fisicas(self) -> None:
        try:
            modelo = CondicionesFisicas(
                nivel_solidos=self.cadena['solidos']['valor'],
                nivel_visibilidad=self.cadena['visibilidad']['valor']
            )

            variables, confianza = modelo.calcular_inferencia()
            valor = modelo.condiciones
            etiqueta = modelo.obtener_etiqueta()

            self.cadena['fisicas']['variables'] = variables
            self.cadena['fisicas']['confianza'] = confianza
            self.cadena['fisicas']['valor'] = valor
            self.cadena['fisicas']['etiqueta'] = etiqueta

        except Exception as e:
            self.errores['fisicas'] = str(e)

    def _inferir_nutrientes(self) -> None:
        try:
            modelo = NivelNutrientes(
                nivel_nitrogeno=self.cadena['nitrogeno']['valor'],
                nivel_fosforo=self.cadena['fosforo']['valor'],
            )

            variables, confianza = modelo.calcular_inferencia()
            valor = modelo.nivel_nutrientes
            etiqueta = modelo.obtener_etiqueta()

            self.cadena['nutrientes']['variables'] = variables
            self.cadena['nutrientes']['confianza'] = confianza
            self.cadena['nutrientes']['valor'] = valor
            self.cadena['nutrientes']['etiqueta'] = etiqueta

        except Exception as e:
            self.errores['nutrientes'] = str(e)

    def _inferir_quimicas(self) -> None:
        try:
            modelo = CondicionesQuimicas(
                nivel_nutrientes=self.cadena['nutrientes']['valor'],
                balance_oxigeno=self.cadena['oxigeno']['valor'],
            )

            variables, confianza = modelo.calcular_inferencia()
            valor = modelo.condiciones_quimicas
            etiqueta = modelo.obtener_etiqueta()

            self.cadena['quimicas']['variables'] = variables
            self.cadena['quimicas']['confianza'] = confianza
            self.cadena['quimicas']['valor'] = valor
            self.cadena['quimicas']['etiqueta'] = etiqueta

        except Exception as e:
            self.errores['quimicas'] = str(e)

    def _inferir_eutrofizacion(self) -> None:
        try:
            modelo = NivelEutrofizacion(
                condiciones_quimicas=self.cadena['quimicas']['valor'],
                condiciones_fisicas=self.cadena['fisicas']['valor'],
                condiciones_adicionales=self.cadena['adicionales']['valor']
            )

            variables, confianza = modelo.calcular_inferencia()
            valor = modelo.nivel_eutrofizacion
            etiqueta = modelo.obtener_etiqueta()

            self.cadena['eutrofizacion']['variables'] = variables
            self.cadena['eutrofizacion']['confianza'] = confianza
            self.cadena['eutrofizacion']['valor'] = valor
            self.cadena['eutrofizacion']['etiqueta'] = etiqueta

        except Exception as e:
            self.errores['eutrofizacion'] = str(e)


def ejecutar_motor(df):
    resultados = []
    entradas = []
    errores = []

    for index, row in df.iterrows():
        motor = MotorDifuso(**row.to_dict())
        motor.ejecutar()

        resultados.append(motor.cadena)
        entradas.append(motor.entradas)
        errores.append(motor.errores)

    return resultados, entradas, errores


def calculate_tsi_individual(transparency: float, total_phosphorus: float, chlorophyll_a: float):
    """
    Calcula los valores del Índice del Estado Trófico (TSI) para cada parámetro proporcionado
    y determina el nivel de eutrofización correspondiente a cada uno.

    Parámetros:
    - transparency (float o np.nan): Profundidad del Disco Secchi en metros.
    - total_phosphorus (float o np.nan): Concentración de fósforo total en µg/L.
    - chlorophyll_a (float o np.nan): Concentración de clorofila-a en µg/L.

    Retorna:
    - Un diccionario que contiene:
        - 'TSI_SD': Valor TSI de la transparencia (o np.nan).
        - 'Level_SD': Nivel de eutrofización correspondiente a 'TSI_SD' (o None).
        - 'TSI_Chl_a': Valor TSI de la clorofila-a (o np.nan).
        - 'Level_Chl_a': Nivel de eutrofización correspondiente a 'TSI_Chl_a' (o None).
        - 'TSI_TP': Valor TSI del fósforo total (o np.nan).
        - 'Level_TP': Nivel de eutrofización correspondiente a 'TSI_TP' (o None).
    """
    tsi_sd = np.nan
    tsi_chl_a = np.nan
    tsi_tp = np.nan

    level_sd = EutrophicationLevel.UNKNOWN.value
    level_chl_a = EutrophicationLevel.UNKNOWN.value
    level_tp = EutrophicationLevel.UNKNOWN.value

    # Calcular TSI y nivel de eutrofización a partir de la transparencia
    if not np.isnan(transparency) and transparency > 0:
            tsi_sd = 60 - 14.41 * math.log(transparency)
            level_sd = determine_eutrophication_level(tsi_sd)

    # Calcular TSI y nivel de eutrofización a partir de la clorofila-a
    if not np.isnan(chlorophyll_a) and chlorophyll_a > 0:
            tsi_chl_a = 9.81 * math.log(chlorophyll_a) + 30.6
            level_chl_a = determine_eutrophication_level(tsi_chl_a)

    # Calcular TSI y nivel de eutrofización a partir del fósforo total
    if not np.isnan(total_phosphorus) and total_phosphorus > 0:
            tsi_tp = 14.42 * math.log(total_phosphorus) + 4.15
            level_tp = determine_eutrophication_level(tsi_tp)

    # Retornar los resultados
    return {
        'TSI_SD': tsi_sd,
        'Level_SD': level_sd,
        'TSI_Chl_a': tsi_chl_a,
        'Level_Chl_a': level_chl_a,
        'TSI_TP': tsi_tp,
        'Level_TP': level_tp
    }


def determine_eutrophication_level(tsi_value: float) -> EutrophicationLevel:
    """
    Determina el nivel de eutrofización basado en el valor TSI proporcionado.

    Parámetros:
    - tsi_value (float): Valor TSI.

    Retorna:
    - EutrophicationLevel: Nivel de eutrofización correspondiente.
    """
    if tsi_value < 40:
        return EutrophicationLevel.OLIGOTROPHIC.value
    elif tsi_value < 50:
        return EutrophicationLevel.MESOTROPHIC.value
    elif tsi_value < 70:
        return EutrophicationLevel.EUTROPHIC.value
    else:
        return EutrophicationLevel.HYPEREUTROPHIC.value


def evaluar_motor(df, resultados):
    validacion = []
    inferencia = []
    tsi = []
    reals = 0
    exacts = 0

    for i in range(df.shape[0]):
        chl_a = np.nan
        tp = np.nan
        trans = np.nan

        if 'Chl_a' in df.columns:
            chl_a = df.iloc[i]['Chl_a'] * 1000

        if 'TP' in df.columns:
            tp = df.iloc[i]['TP'] * 1000

        if 'TRANS' in df.columns:
            trans = df.iloc[i]['TRANS']

        tsi_results = calculate_tsi_individual(trans, tp, chl_a)

        tag_sd = tsi_results['Level_SD']
        tag_tp = tsi_results['Level_TP']
        tag_chl_a = tsi_results['Level_Chl_a']

        val_sd = tsi_results['TSI_SD']
        val_tp = tsi_results['TSI_TP']
        val_chl_a = tsi_results['TSI_Chl_a']

        if all([np.isnan(val_sd), np.isnan(val_tp), np.isnan(val_chl_a)]):
            continue

        tag_motor = resultados[i]['eutrofizacion']['etiqueta']

        if tag_motor != EutrophicationLevel.UNKNOWN.value:

            reals += 1
            inferencia.append(tag_motor)

            if tag_motor == tag_chl_a:
                exacts += 1
                validacion.append(tag_motor)
                tsi.append('Chl-a')
            elif tag_motor == tag_tp:
                exacts += 1
                validacion.append(tag_motor)
                tsi.append('TP')
            elif tag_motor == tag_sd:
                exacts += 1
                validacion.append(tag_motor)
                tsi.append('SD')
            else:
                tsi.append('FAIL')
                if tag_chl_a != EutrophicationLevel.UNKNOWN.value:
                    validacion.append(tag_chl_a)
                elif tag_tp != EutrophicationLevel.UNKNOWN.value:
                    validacion.append(tag_tp)
                else:
                    validacion.append(tag_sd)

        #print(f"{reals}\t{i}\t{tag_sd}\t{tag_tp}\t{tag_chl_a}\t{tag_motor}\t{trans:.2f}\t{tp:.2f}\t{chl_a:.2f}")

    puntaje = np.round(exacts / reals, 3)

    aptitud = 'INSUFICIENTE'
    if puntaje >= 0.5 and puntaje < 0.75:
        aptitud = 'ACEPTABLE'
    elif puntaje >= 0.75 and puntaje < 0.9:
        aptitud = 'BUENO'
    elif puntaje >= 0.9:
        aptitud = 'EXCELENTE'

    return {
        'validacion': validacion,
        'inferencia': inferencia,
        'tsi': tsi,
        'reals': reals,
        'exacts': exacts,
        'fails': reals - exacts,
        'precision': puntaje,
        'aptitud': aptitud
    }


def reporte_motor(entradas, cadena):
    pimarias = ['nitrogeno', 'fosforo', 'oxigeno', 'solidos', 'visibilidad', 'adicionales']

    _l = {
        'nitrogeno': 'NIVEL DE NITRÓGENO',
        'fosforo': 'NIVEL DE FÓSFORO',
        'oxigeno': 'BALANCE DE OXÍGENO',
        'solidos': 'NIVEL DE SOLIDOS',
        'visibilidad': 'NIVEL DE VISIBILIDAD',
        'adicionales': 'CONDICIONES ADICIONALES',
        'fisicas': 'CONDICIONES FÍSICAS',
        'nutrientes': 'NIVEL DE NUTRIENTES',
        'quimicas': 'CONDICIONES QUÍMICAS',
        'eutrofizacion': 'NIVEL DE EUTRÓFIZACION'
    }

    for k, v in cadena.items():
        print(f"\n{_l.get(k)}")
        if k in pimarias:
            if k in entradas:
                cell_entradas = []
                for kv, vv in entradas[k].items():
                    cell_entradas.append(f"({kv}: {vv:.3f})")
                cell_entradas = '\t'.join(cell_entradas)

                print(f"\tENTRADAS: {cell_entradas}")
            else:
                print(f"\tENTRADAS: NO DISPONIBLES")

        if k == 'fisicas':
            solidos = f"{_l.get('solidos')}: {cadena['solidos']['etiqueta']}"
            visibilidad = f"{_l.get('visibilidad')}: {cadena['visibilidad']['etiqueta']}"
            print(f"\tENTRADAS: ({solidos})\t({visibilidad})")

        if k == 'nutrientes':
            nitrogeno = f"{_l.get('nitrogeno')}: {cadena['nitrogeno']['etiqueta']}"
            fosforo = f"{_l.get('fosforo')}: {cadena['fosforo']['etiqueta']}"
            print(f"\tENTRADAS: ({nitrogeno})\t({fosforo})")

        if k == 'quimicas':
            nutrientes = f"{_l.get('nutrientes')}: {cadena['nutrientes']['etiqueta']}"
            oxigeno = f"{_l.get('oxigeno')}: {cadena['oxigeno']['etiqueta']}"
            print(f"\tENTRADAS: ({nutrientes})\t({oxigeno})")

        if k == 'eutrofizacion':
            quimicas = f"{_l.get('quimicas')}: {cadena['quimicas']['etiqueta']}"
            fisicas = f"{_l.get('fisicas')}: {cadena['fisicas']['etiqueta']}"
            adicionales = f"{_l.get('adicionales')}: {cadena['adicionales']['etiqueta']}"
            print(f"\tENTRADAS: ({quimicas})\t({fisicas})\t({adicionales})")

        print(f"\tVALOR: {v['valor']:.3f}")
        print(f"\tETIQUETA: {v['etiqueta']}")
        print(f"\tCONFIANZA: {(v['confianza']*100):.3f} %")


def generar_reporte(entradas, resultados):
    reporte = []
    for i in range(len(entradas)):
        captura = io.StringIO()
        with contextlib.redirect_stdout(captura):
            print("---------------------------------------------------------------")
            print(f"MUESTRA: {i+1}")
            print("---------------------------------------------------------------")
            reporte_motor(entradas[i], resultados[i])
        reporte.append(captura.getvalue())
    return reporte