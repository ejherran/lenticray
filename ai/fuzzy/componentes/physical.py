import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class CondicionesFisicas:
    def __init__(self, nivel_solidos=np.nan, nivel_visibilidad=np.nan):
        self.nivel_solidos = nivel_solidos
        self.nivel_visibilidad = nivel_visibilidad
        self.condiciones = np.nan

        # Verificar que al menos una variable esté disponible
        if np.isnan(self.nivel_solidos) and np.isnan(self.nivel_visibilidad):
            raise ValueError("Se requiere al menos nivel_solidos o nivel_visibilidad para evaluar las condiciones físicas.")

        # Determinar variables disponibles
        self.variables_disponibles = []
        if not np.isnan(self.nivel_solidos):
            self.variables_disponibles.append('nivel_solidos')
        if not np.isnan(self.nivel_visibilidad):
            self.variables_disponibles.append('nivel_visibilidad')

        # Crear el sistema difuso según las variables disponibles
        self._crear_sistema_difuso()

    def _crear_sistema_difuso(self):
        # Definir la variable de salida
        self.condiciones_universe = np.arange(0, 1.01, 0.01)
        self.condiciones_var = ctrl.Consequent(self.condiciones_universe, 'condiciones_fisicas')
        self.condiciones_var['BUENAS'] = fuzz.trapmf(self.condiciones_var.universe, [0, 0, 0.2, 0.3])
        self.condiciones_var['NEUTRALES'] = fuzz.trimf(self.condiciones_var.universe, [0.25, 0.4, 0.55])
        self.condiciones_var['MALAS'] = fuzz.trimf(self.condiciones_var.universe, [0.5, 0.65, 0.8])
        self.condiciones_var['MUY MALAS'] = fuzz.trapmf(self.condiciones_var.universe, [0.75, 0.85, 1, 1])

        self.rules = []
        self.variables = {}

        # Definir variables difusas según las variables disponibles
        if 'nivel_solidos' in self.variables_disponibles:
            # Definir el universo de discurso para nivel_solidos
            self.nivel_solidos_universe = np.arange(0, 1.01, 0.01)
            self.nivel_solidos_var = ctrl.Antecedent(self.nivel_solidos_universe, 'nivel_solidos')
            self.nivel_solidos_var['BAJO'] = fuzz.trapmf(self.nivel_solidos_var.universe, [0, 0, 0.2, 0.4])
            self.nivel_solidos_var['MODERADO'] = fuzz.trimf(self.nivel_solidos_var.universe, [0.3, 0.5, 0.7])
            self.nivel_solidos_var['ALTO'] = fuzz.trimf(self.nivel_solidos_var.universe, [0.6, 0.75, 0.9])
            self.nivel_solidos_var['MUY ALTO'] = fuzz.trapmf(self.nivel_solidos_var.universe, [0.85, 0.95, 1, 1])
            self.variables['nivel_solidos'] = self.nivel_solidos_var

        if 'nivel_visibilidad' in self.variables_disponibles:
            # Definir el universo de discurso para nivel_visibilidad
            self.nivel_visibilidad_universe = np.arange(0, 1.01, 0.01)
            self.nivel_visibilidad_var = ctrl.Antecedent(self.nivel_visibilidad_universe, 'nivel_visibilidad')
            self.nivel_visibilidad_var['BAJO'] = fuzz.trapmf(self.nivel_visibilidad_var.universe, [0, 0, 0.2, 0.4])
            self.nivel_visibilidad_var['MODERADO'] = fuzz.trimf(self.nivel_visibilidad_var.universe, [0.3, 0.5, 0.7])
            self.nivel_visibilidad_var['ALTO'] = fuzz.trimf(self.nivel_visibilidad_var.universe, [0.6, 0.75, 0.9])
            self.nivel_visibilidad_var['MUY ALTO'] = fuzz.trapmf(self.nivel_visibilidad_var.universe, [0.85, 0.95, 1, 1])
            self.variables['nivel_visibilidad'] = self.nivel_visibilidad_var

        # Definir las reglas difusas según las variables disponibles
        self._definir_reglas()

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def _definir_reglas(self):
        # Reglas basadas en las variables disponibles
        if 'nivel_solidos' in self.variables and 'nivel_visibilidad' in self.variables:
            # Ambas variables están disponibles
            solidos = self.variables['nivel_solidos']
            visibilidad = self.variables['nivel_visibilidad']

            self.rules.append(ctrl.Rule(visibilidad['MUY ALTO'] & (solidos['BAJO'] | solidos['MODERADO']), self.condiciones_var['BUENAS']))
            self.rules.append(ctrl.Rule(visibilidad['MUY ALTO'] & (solidos['ALTO'] | solidos['MUY ALTO']), self.condiciones_var['NEUTRALES']))

            self.rules.append(ctrl.Rule(visibilidad['ALTO'] & solidos['BAJO'], self.condiciones_var['BUENAS']))
            self.rules.append(ctrl.Rule(visibilidad['ALTO'] & (solidos['MODERADO'] | solidos['ALTO'] | solidos['MUY ALTO']), self.condiciones_var['NEUTRALES']))

            self.rules.append(ctrl.Rule(visibilidad['MODERADO'] & (solidos['BAJO'] | solidos['MODERADO']), self.condiciones_var['NEUTRALES']))
            self.rules.append(ctrl.Rule(visibilidad['MODERADO'] & (solidos['ALTO'] | solidos['MUY ALTO']), self.condiciones_var['MALAS']))

            self.rules.append(ctrl.Rule(visibilidad['BAJO'] & solidos['BAJO'], self.condiciones_var['NEUTRALES']))
            self.rules.append(ctrl.Rule(visibilidad['BAJO'] & (solidos['MODERADO'] | solidos['ALTO']), self.condiciones_var['MALAS']))
            self.rules.append(ctrl.Rule(visibilidad['BAJO'] & (solidos['MUY ALTO']), self.condiciones_var['MUY MALAS']))

        elif 'nivel_solidos' in self.variables:
            # Solo nivel_solidos está disponible
            solidos = self.variables['nivel_solidos']
            self.rules.append(ctrl.Rule(solidos['BAJO'], self.condiciones_var['BUENAS']))
            self.rules.append(ctrl.Rule(solidos['MODERADO'], self.condiciones_var['NEUTRALES']))
            self.rules.append(ctrl.Rule(solidos['ALTO'], self.condiciones_var['MALAS']))
            self.rules.append(ctrl.Rule(solidos['MUY ALTO'], self.condiciones_var['MUY MALAS']))

        elif 'nivel_visibilidad' in self.variables:
            # Solo nivel_visibilidad está disponible
            visibilidad = self.variables['nivel_visibilidad']
            self.rules.append(ctrl.Rule(visibilidad['MUY ALTO'], self.condiciones_var['BUENAS']))
            self.rules.append(ctrl.Rule(visibilidad['ALTO'], self.condiciones_var['NEUTRALES']))
            self.rules.append(ctrl.Rule(visibilidad['MODERADO'], self.condiciones_var['MALAS']))
            self.rules.append(ctrl.Rule(visibilidad['BAJO'], self.condiciones_var['MUY MALAS']))

    def calcular_inferencia(self):
        # Asignar los valores de entrada disponibles
        if 'nivel_solidos' in self.variables:
            self.simulation.input['nivel_solidos'] = self.nivel_solidos
        if 'nivel_visibilidad' in self.variables:
            self.simulation.input['nivel_visibilidad'] = self.nivel_visibilidad

        try:
            # Realizar la inferencia
            self.simulation.compute()

            # Obtener el resultado
            self.condiciones = self.simulation.output['condiciones_fisicas']
        except Exception as e:
            raise ValueError(f"Error al calcular la inferencia: {e}")

        # Determinar variables usadas y confianza
        if 'nivel_solidos' in self.variables and 'nivel_visibilidad' in self.variables:
            variables_usadas = 'SOLIDOS_VISIBILIDAD'
            confianza = 1.0
        elif 'nivel_solidos' in self.variables:
            variables_usadas = 'SOLIDOS'
            confianza = 0.5
        elif 'nivel_visibilidad' in self.variables:
            variables_usadas = 'VISIBILIDAD'
            confianza = 0.5

        return (variables_usadas, confianza)

    def obtener_etiqueta(self):
        if np.isnan(self.condiciones):
            raise ValueError("No se ha calculado la inferencia de condiciones físicas.")

        # Determinar la etiqueta con mayor grado de pertenencia
        grados_pertenencia = {}
        for etiqueta in self.condiciones_var.terms:
            funcion_pertenencia = self.condiciones_var[etiqueta].mf
            grado = fuzz.interp_membership(self.condiciones_var.universe, funcion_pertenencia, self.condiciones)
            grados_pertenencia[etiqueta] = grado

        etiqueta_predicha = max(grados_pertenencia, key=grados_pertenencia.get)
        return etiqueta_predicha
