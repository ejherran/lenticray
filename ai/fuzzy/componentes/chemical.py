import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class CondicionesQuimicas:
    def __init__(self, nivel_nutrientes=np.nan, balance_oxigeno=np.nan):
        self.nivel_nutrientes = nivel_nutrientes
        self.balance_oxigeno = balance_oxigeno
        self.condiciones_quimicas = np.nan

        # Verificar que al menos una variable esté disponible
        if np.isnan(self.nivel_nutrientes) and np.isnan(self.balance_oxigeno):
            raise ValueError("Se requiere al menos nivel_nutrientes o balance_oxigeno para evaluar las condiciones químicas.")

        # Determinar variables disponibles
        self.variables_disponibles = []
        if not np.isnan(self.nivel_nutrientes):
            self.variables_disponibles.append('nivel_nutrientes')
        if not np.isnan(self.balance_oxigeno):
            self.variables_disponibles.append('balance_oxigeno')

        # Crear el sistema difuso según las variables disponibles
        self._crear_sistema_difuso()

    def _crear_sistema_difuso(self):
        # Definir la variable de salida
        self.condiciones_quimicas_universe = np.arange(0, 1.01, 0.01)
        self.condiciones_quimicas_var = ctrl.Consequent(self.condiciones_quimicas_universe, 'condiciones_quimicas')
        self.condiciones_quimicas_var['BUENAS'] = fuzz.trapmf(self.condiciones_quimicas_var.universe, [0, 0, 0.2, 0.35])
        self.condiciones_quimicas_var['NEUTRALES'] = fuzz.trimf(self.condiciones_quimicas_var.universe, [0.3, 0.45, 0.6])
        self.condiciones_quimicas_var['MALAS'] = fuzz.trimf(self.condiciones_quimicas_var.universe, [0.55, 0.7, 0.85])
        self.condiciones_quimicas_var['MUY MALAS'] = fuzz.trapmf(self.condiciones_quimicas_var.universe, [0.8, 0.9, 1, 1])

        self.rules = []
        self.variables = {}

        # Definir variables difusas según las variables disponibles
        if 'nivel_nutrientes' in self.variables_disponibles:
            # Definir el universo de discurso para nivel_nutrientes
            self.nivel_nutrientes_universe = np.arange(0, 1.01, 0.01)
            self.nivel_nutrientes_var = ctrl.Antecedent(self.nivel_nutrientes_universe, 'nivel_nutrientes')
            self.nivel_nutrientes_var['BAJO'] = fuzz.trapmf(self.nivel_nutrientes_var.universe, [0, 0, 0.2, 0.4])
            self.nivel_nutrientes_var['MODERADO'] = fuzz.trimf(self.nivel_nutrientes_var.universe, [0.3, 0.5, 0.7])
            self.nivel_nutrientes_var['ALTO'] = fuzz.trimf(self.nivel_nutrientes_var.universe, [0.6, 0.75, 0.9])
            self.nivel_nutrientes_var['MUY ALTO'] = fuzz.trapmf(self.nivel_nutrientes_var.universe, [0.85, 0.95, 1, 1])
            self.variables['nivel_nutrientes'] = self.nivel_nutrientes_var

        if 'balance_oxigeno' in self.variables_disponibles:
            # Definir el universo de discurso para balance_oxigeno
            self.balance_oxigeno_universe = np.arange(0, 1.01, 0.01)
            self.balance_oxigeno_var = ctrl.Antecedent(self.balance_oxigeno_universe, 'balance_oxigeno')
            self.balance_oxigeno_var['BUENO'] = fuzz.trapmf(self.balance_oxigeno_var.universe, [0, 0, 0.2, 0.4])
            self.balance_oxigeno_var['MODERADO'] = fuzz.trimf(self.balance_oxigeno_var.universe, [0.3, 0.5, 0.7])
            self.balance_oxigeno_var['MALO'] = fuzz.trimf(self.balance_oxigeno_var.universe, [0.6, 0.75, 0.9])
            self.balance_oxigeno_var['MUY_MALO'] = fuzz.trapmf(self.balance_oxigeno_var.universe, [0.85, 0.95, 1, 1])
            self.variables['balance_oxigeno'] = self.balance_oxigeno_var

        # Definir las reglas difusas según las variables disponibles
        self._definir_reglas()

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def _definir_reglas(self):
        # Reglas basadas en las variables disponibles
        if 'nivel_nutrientes' in self.variables and 'balance_oxigeno' in self.variables:
            # Ambas variables están disponibles
            nutrientes = self.variables['nivel_nutrientes']
            oxigeno = self.variables['balance_oxigeno']

            # Regla 1
            self.rules.append(ctrl.Rule(nutrientes['BAJO'] & oxigeno['BUENO'], self.condiciones_quimicas_var['BUENAS']))

            # Regla 2
            self.rules.append(ctrl.Rule(nutrientes['BAJO'] & oxigeno['MODERADO'], self.condiciones_quimicas_var['BUENAS']))

            # Regla 3
            self.rules.append(ctrl.Rule(nutrientes['BAJO'] & (oxigeno['MALO'] | oxigeno['MUY_MALO']), self.condiciones_quimicas_var['NEUTRALES']))

            # Regla 4
            self.rules.append(ctrl.Rule(nutrientes['MODERADO'] & oxigeno['BUENO'], self.condiciones_quimicas_var['NEUTRALES']))

            # Regla 5
            self.rules.append(ctrl.Rule(nutrientes['MODERADO'] & oxigeno['MODERADO'], self.condiciones_quimicas_var['NEUTRALES']))

            # Regla 6
            self.rules.append(ctrl.Rule(nutrientes['MODERADO'] & (oxigeno['MALO'] | oxigeno['MUY_MALO']), self.condiciones_quimicas_var['MALAS']))

            # Regla 7
            self.rules.append(ctrl.Rule((nutrientes['ALTO'] | nutrientes['MUY ALTO']) & oxigeno['BUENO'], self.condiciones_quimicas_var['MALAS']))

            # Regla 8
            self.rules.append(ctrl.Rule((nutrientes['ALTO'] | nutrientes['MUY ALTO']) & oxigeno['MODERADO'], self.condiciones_quimicas_var['MALAS']))

            # Regla 9
            self.rules.append(ctrl.Rule((nutrientes['ALTO'] | nutrientes['MUY ALTO']) & (oxigeno['MALO'] | oxigeno['MUY_MALO']), self.condiciones_quimicas_var['MUY MALAS']))

        elif 'nivel_nutrientes' in self.variables:
            # Solo nivel de nutrientes está disponible
            nutrientes = self.variables['nivel_nutrientes']
            self.rules.append(ctrl.Rule(nutrientes['BAJO'], self.condiciones_quimicas_var['BUENAS']))
            self.rules.append(ctrl.Rule(nutrientes['MODERADO'], self.condiciones_quimicas_var['NEUTRALES']))
            self.rules.append(ctrl.Rule(nutrientes['ALTO'], self.condiciones_quimicas_var['MALAS']))
            self.rules.append(ctrl.Rule(nutrientes['MUY ALTO'], self.condiciones_quimicas_var['MUY MALAS']))

        elif 'balance_oxigeno' in self.variables:
            # Solo balance de oxígeno está disponible
            oxigeno = self.variables['balance_oxigeno']
            self.rules.append(ctrl.Rule(oxigeno['BUENO'], self.condiciones_quimicas_var['BUENAS']))
            self.rules.append(ctrl.Rule(oxigeno['MODERADO'], self.condiciones_quimicas_var['NEUTRALES']))
            self.rules.append(ctrl.Rule(oxigeno['MALO'], self.condiciones_quimicas_var['MALAS']))
            self.rules.append(ctrl.Rule(oxigeno['MUY_MALO'], self.condiciones_quimicas_var['MUY MALAS']))

    def calcular_inferencia(self):
        # Asignar los valores de entrada disponibles
        if 'nivel_nutrientes' in self.variables:
            self.simulation.input['nivel_nutrientes'] = self.nivel_nutrientes
        if 'balance_oxigeno' in self.variables:
            self.simulation.input['balance_oxigeno'] = self.balance_oxigeno

        try:
            # Realizar la inferencia
            self.simulation.compute()

            # Obtener el resultado
            self.condiciones_quimicas = self.simulation.output['condiciones_quimicas']
        except Exception as e:
            raise ValueError(f"Error al calcular la inferencia: {e}")

        # Determinar variables usadas y confianza
        if 'nivel_nutrientes' in self.variables and 'balance_oxigeno' in self.variables:
            variables_usadas = 'NUTRIENTES_OXIGENO'
            confianza = 1.0
        elif 'nivel_nutrientes' in self.variables:
            variables_usadas = 'NUTRIENTES'
            confianza = 0.8
        elif 'balance_oxigeno' in self.variables:
            variables_usadas = 'OXIGENO'
            confianza = 0.3

        return (variables_usadas, confianza)

    def obtener_etiqueta(self):
        if np.isnan(self.condiciones_quimicas):
            raise ValueError("No se ha calculado la inferencia de condiciones químicas.")

        # Determinar la etiqueta con mayor grado de pertenencia
        grados_pertenencia = {}
        for etiqueta in self.condiciones_quimicas_var.terms:
            funcion_pertenencia = self.condiciones_quimicas_var[etiqueta].mf
            grado = fuzz.interp_membership(self.condiciones_quimicas_var.universe, funcion_pertenencia, self.condiciones_quimicas)
            grados_pertenencia[etiqueta] = grado

        etiqueta_predicha = max(grados_pertenencia, key=grados_pertenencia.get)
        return etiqueta_predicha

