import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class NivelNutrientes:
    def __init__(self, nivel_nitrogeno=np.nan, nivel_fosforo=np.nan):
        self.nivel_nitrogeno = nivel_nitrogeno
        self.nivel_fosforo = nivel_fosforo
        self.nivel_nutrientes = np.nan

        # Verificar que al menos una variable esté disponible
        if np.isnan(self.nivel_nitrogeno) and np.isnan(self.nivel_fosforo):
            raise ValueError("Se requiere al menos nivel_nitrogeno o nivel_fosforo para evaluar el nivel de nutrientes.")

        # Determinar variables disponibles
        self.variables_disponibles = []
        if not np.isnan(self.nivel_nitrogeno):
            self.variables_disponibles.append('nivel_nitrogeno')
        if not np.isnan(self.nivel_fosforo):
            self.variables_disponibles.append('nivel_fosforo')

        # Crear el sistema difuso según las variables disponibles
        self._crear_sistema_difuso()

    def _crear_sistema_difuso(self):
        # Definir la variable de salida
        self.nivel_nutrientes_universe = np.arange(0, 1.01, 0.01)
        self.nivel_nutrientes_var = ctrl.Consequent(self.nivel_nutrientes_universe, 'nivel_nutrientes')
        self.nivel_nutrientes_var['BAJO'] = fuzz.trapmf(self.nivel_nutrientes_var.universe, [0, 0, 0.2, 0.4])
        self.nivel_nutrientes_var['MODERADO'] = fuzz.trimf(self.nivel_nutrientes_var.universe, [0.3, 0.5, 0.7])
        self.nivel_nutrientes_var['ALTO'] = fuzz.trimf(self.nivel_nutrientes_var.universe, [0.6, 0.75, 0.9])
        self.nivel_nutrientes_var['MUY ALTO'] = fuzz.trapmf(self.nivel_nutrientes_var.universe, [0.85, 0.95, 1, 1])

        self.rules = []
        self.variables = {}

        # Definir variables difusas según las variables disponibles
        if 'nivel_nitrogeno' in self.variables_disponibles:
            # Definir el universo de discurso para nivel_nitrogeno
            self.nivel_nitrogeno_universe = np.arange(0, 1.01, 0.01)
            self.nivel_nitrogeno_var = ctrl.Antecedent(self.nivel_nitrogeno_universe, 'nivel_nitrogeno')
            self.nivel_nitrogeno_var['BAJO'] = fuzz.trapmf(self.nivel_nitrogeno_var.universe, [0, 0, 0.15, 0.3])
            self.nivel_nitrogeno_var['MODERADO'] = fuzz.trimf(self.nivel_nitrogeno_var.universe, [0.25, 0.4, 0.55])
            self.nivel_nitrogeno_var['ALTO'] = fuzz.trimf(self.nivel_nitrogeno_var.universe, [0.5, 0.65, 0.8])
            self.nivel_nitrogeno_var['MUY ALTO'] = fuzz.trapmf(self.nivel_nitrogeno_var.universe, [0.75, 0.85, 1, 1])
            self.variables['nivel_nitrogeno'] = self.nivel_nitrogeno_var

        if 'nivel_fosforo' in self.variables_disponibles:
            # Definir el universo de discurso para nivel_fosforo
            self.nivel_fosforo_universe = np.arange(0, 1.01, 0.01)
            self.nivel_fosforo_var = ctrl.Antecedent(self.nivel_fosforo_universe, 'nivel_fosforo')
            self.nivel_fosforo_var['BAJO'] = fuzz.trapmf(self.nivel_fosforo_var.universe, [0, 0, 0.15, 0.3])
            self.nivel_fosforo_var['MODERADO'] = fuzz.trimf(self.nivel_fosforo_var.universe, [0.25, 0.4, 0.55])
            self.nivel_fosforo_var['ALTO'] = fuzz.trimf(self.nivel_fosforo_var.universe, [0.5, 0.65, 0.8])
            self.nivel_fosforo_var['MUY ALTO'] = fuzz.trapmf(self.nivel_fosforo_var.universe, [0.75, 0.85, 1, 1])
            self.variables['nivel_fosforo'] = self.nivel_fosforo_var

        # Definir las reglas difusas según las variables disponibles
        self._definir_reglas()

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def _definir_reglas(self):
        # Reglas basadas en las variables disponibles
        if 'nivel_nitrogeno' in self.variables and 'nivel_fosforo' in self.variables:
            # Ambas variables están disponibles
            nitrogeno = self.variables['nivel_nitrogeno']
            fosforo = self.variables['nivel_fosforo']

            # Reglas detalladas
            # Ambos BAJO
            self.rules.append(ctrl.Rule(nitrogeno['BAJO'] & fosforo['BAJO'], self.nivel_nutrientes_var['BAJO']))

            # Ambos MODERADO
            self.rules.append(ctrl.Rule(nitrogeno['MODERADO'] & fosforo['MODERADO'], self.nivel_nutrientes_var['MODERADO']))

            # Ambos ALTO
            self.rules.append(ctrl.Rule(nitrogeno['ALTO'] & fosforo['ALTO'], self.nivel_nutrientes_var['MUY ALTO']))

            # Ambos MUY_ALTO
            self.rules.append(ctrl.Rule(nitrogeno['MUY ALTO'] & fosforo['MUY ALTO'], self.nivel_nutrientes_var['MUY ALTO']))

            # Uno ALTO y otro MODERADO
            self.rules.append(ctrl.Rule(
                (nitrogeno['ALTO'] & fosforo['MODERADO']) | (nitrogeno['MODERADO'] & fosforo['ALTO']),
                self.nivel_nutrientes_var['ALTO']
            ))

            # Uno MUY_ALTO y otro ALTO
            self.rules.append(ctrl.Rule(
                (nitrogeno['MUY ALTO'] & fosforo['ALTO']) | (nitrogeno['ALTO'] & fosforo['MUY ALTO']),
                self.nivel_nutrientes_var['MUY ALTO']
            ))

            # Uno MODERADO y otro BAJO
            self.rules.append(ctrl.Rule(
                (nitrogeno['MODERADO'] & fosforo['BAJO']) | (nitrogeno['BAJO'] & fosforo['MODERADO']),
                self.nivel_nutrientes_var['MODERADO']
            ))

            # Uno ALTO y otro BAJO
            self.rules.append(ctrl.Rule(
                (nitrogeno['ALTO'] & fosforo['BAJO']) | (nitrogeno['BAJO'] & fosforo['ALTO']),
                self.nivel_nutrientes_var['MODERADO']
            ))

            # Uno MUY_ALTO y otro BAJO
            self.rules.append(ctrl.Rule(
                (nitrogeno['MUY ALTO'] & fosforo['BAJO']) | (nitrogeno['BAJO'] & fosforo['MUY ALTO']),
                self.nivel_nutrientes_var['MODERADO']
            ))

            # Uno MUY_ALTO y otro MODERADO
            self.rules.append(ctrl.Rule(
                (nitrogeno['MUY ALTO'] & fosforo['MODERADO']) | (nitrogeno['MODERADO'] & fosforo['MUY ALTO']),
                self.nivel_nutrientes_var['ALTO']
            ))

            # Si la diferencia es más de un nivel, el nivel es el más bajo
            self.rules.append(ctrl.Rule(
                (nitrogeno['MUY ALTO'] & fosforo['BAJO']) | (nitrogeno['BAJO'] & fosforo['MUY ALTO']),
                self.nivel_nutrientes_var['MODERADO']
            ))

        else:
            # Si solo una variable está disponible, el nivel de nutrientes es el mismo que la variable disponible
            for var_name in ['nivel_nitrogeno', 'nivel_fosforo']:
                if var_name in self.variables:
                    antecedent = self.variables[var_name]
                    self.rules.append(ctrl.Rule(antecedent['BAJO'], self.nivel_nutrientes_var['BAJO']))
                    self.rules.append(ctrl.Rule(antecedent['MODERADO'], self.nivel_nutrientes_var['MODERADO']))
                    self.rules.append(ctrl.Rule(antecedent['ALTO'], self.nivel_nutrientes_var['ALTO']))
                    self.rules.append(ctrl.Rule(antecedent['MUY ALTO'], self.nivel_nutrientes_var['MUY ALTO']))

    def calcular_inferencia(self):
        # Asignar los valores de entrada disponibles
        if 'nivel_nitrogeno' in self.variables:
            self.simulation.input['nivel_nitrogeno'] = self.nivel_nitrogeno
        if 'nivel_fosforo' in self.variables:
            self.simulation.input['nivel_fosforo'] = self.nivel_fosforo

        try:
            # Realizar la inferencia
            self.simulation.compute()

            # Obtener el resultado
            self.nivel_nutrientes = self.simulation.output['nivel_nutrientes']
        except Exception as e:
            raise ValueError(f"Error al calcular la inferencia: {e}")

        # Determinar variables usadas y confianza
        if 'nivel_nitrogeno' in self.variables and 'nivel_fosforo' in self.variables:
            variables_usadas = 'NITROGENO_FOSFORO'
            confianza = 1.0
        else:
            variables_usadas = 'NITROGENO' if 'nivel_nitrogeno' in self.variables else 'FOSFORO'
            confianza = 0.5

        return (variables_usadas, confianza)

    def obtener_etiqueta(self):
        if np.isnan(self.nivel_nutrientes):
            raise ValueError("No se ha calculado la inferencia de nivel de nutrientes.")

        # Determinar la etiqueta con mayor grado de pertenencia
        grados_pertenencia = {}
        for etiqueta in self.nivel_nutrientes_var.terms:
            funcion_pertenencia = self.nivel_nutrientes_var[etiqueta].mf
            grado = fuzz.interp_membership(self.nivel_nutrientes_var.universe, funcion_pertenencia, self.nivel_nutrientes)
            grados_pertenencia[etiqueta] = grado

        etiqueta_predicha = max(grados_pertenencia, key=grados_pertenencia.get)
        return etiqueta_predicha
