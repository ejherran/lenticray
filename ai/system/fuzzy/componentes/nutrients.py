import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class NutrientLevel:
    def __init__(self, nitrogen_level=np.nan, phosphorus_level=np.nan):
        self.nitrogen_level = nitrogen_level
        self.phosphorus_level = phosphorus_level
        self.nutrient_level = np.nan

        # Verificar que al menos una variable esté disponible
        if np.isnan(self.nitrogen_level) and np.isnan(self.phosphorus_level):
            raise ValueError("Se requiere al menos nitrogen_level o phosphorus_level para evaluar el nivel de nutrient_level.")

        # Determinar vars disponibles
        self.available_vars = []
        if not np.isnan(self.nitrogen_level):
            self.available_vars.append('nitrogen_level')
        if not np.isnan(self.phosphorus_level):
            self.available_vars.append('phosphorus_level')

        # Crear el sistema difuso según las vars disponibles
        self._create_fuzzy_system()

    def _create_fuzzy_system(self):
        # Definir la variable de salida
        self.nutrient_level_universe = np.arange(0, 1.01, 0.01)
        self.nutrient_level_var = ctrl.Consequent(self.nutrient_level_universe, 'nutrient_level')
        self.nutrient_level_var['LOW'] = fuzz.trapmf(self.nutrient_level_var.universe, [0, 0, 0.2, 0.4])
        self.nutrient_level_var['MODERATE'] = fuzz.trimf(self.nutrient_level_var.universe, [0.3, 0.5, 0.7])
        self.nutrient_level_var['HIGH'] = fuzz.trimf(self.nutrient_level_var.universe, [0.6, 0.75, 0.9])
        self.nutrient_level_var['VERY HIGH'] = fuzz.trapmf(self.nutrient_level_var.universe, [0.85, 0.95, 1, 1])

        self.rules = []
        self.vars = {}

        # Definir vars difusas según las vars disponibles
        if 'nitrogen_level' in self.available_vars:
            # Definir el universo de discurso para nitrogen_level
            self.nitrogen_level_universe = np.arange(0, 1.01, 0.01)
            self.nitrogen_level_var = ctrl.Antecedent(self.nitrogen_level_universe, 'nitrogen_level')
            self.nitrogen_level_var['LOW'] = fuzz.trapmf(self.nitrogen_level_var.universe, [0, 0, 0.15, 0.3])
            self.nitrogen_level_var['MODERATE'] = fuzz.trimf(self.nitrogen_level_var.universe, [0.25, 0.4, 0.55])
            self.nitrogen_level_var['HIGH'] = fuzz.trimf(self.nitrogen_level_var.universe, [0.5, 0.65, 0.8])
            self.nitrogen_level_var['VERY HIGH'] = fuzz.trapmf(self.nitrogen_level_var.universe, [0.75, 0.85, 1, 1])
            self.vars['nitrogen_level'] = self.nitrogen_level_var

        if 'phosphorus_level' in self.available_vars:
            # Definir el universo de discurso para phosphorus_level
            self.phosphorus_level_universe = np.arange(0, 1.01, 0.01)
            self.phosphorus_level_var = ctrl.Antecedent(self.phosphorus_level_universe, 'phosphorus_level')
            self.phosphorus_level_var['LOW'] = fuzz.trapmf(self.phosphorus_level_var.universe, [0, 0, 0.15, 0.3])
            self.phosphorus_level_var['MODERATE'] = fuzz.trimf(self.phosphorus_level_var.universe, [0.25, 0.4, 0.55])
            self.phosphorus_level_var['HIGH'] = fuzz.trimf(self.phosphorus_level_var.universe, [0.5, 0.65, 0.8])
            self.phosphorus_level_var['VERY HIGH'] = fuzz.trapmf(self.phosphorus_level_var.universe, [0.75, 0.85, 1, 1])
            self.vars['phosphorus_level'] = self.phosphorus_level_var

        # Definir las reglas difusas según las vars disponibles
        self._define_rules()

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def _define_rules(self):
        # Reglas basadas en las vars disponibles
        if 'nitrogen_level' in self.vars and 'phosphorus_level' in self.vars:
            # Ambas vars están disponibles
            nitrogen_level = self.vars['nitrogen_level']
            phosphorus_level = self.vars['phosphorus_level']

            # Reglas detalladas
            # Ambos LOW
            self.rules.append(ctrl.Rule(nitrogen_level['LOW'] & phosphorus_level['LOW'], self.nutrient_level_var['LOW']))

            # Ambos MODERATE
            self.rules.append(ctrl.Rule(nitrogen_level['MODERATE'] & phosphorus_level['MODERATE'], self.nutrient_level_var['MODERATE']))

            # Ambos HIGH
            self.rules.append(ctrl.Rule(nitrogen_level['HIGH'] & phosphorus_level['HIGH'], self.nutrient_level_var['VERY HIGH']))

            # Ambos VERY_HIGH
            self.rules.append(ctrl.Rule(nitrogen_level['VERY HIGH'] & phosphorus_level['VERY HIGH'], self.nutrient_level_var['VERY HIGH']))

            # Uno HIGH y otro MODERATE
            self.rules.append(ctrl.Rule(
                (nitrogen_level['HIGH'] & phosphorus_level['MODERATE']) | (nitrogen_level['MODERATE'] & phosphorus_level['HIGH']),
                self.nutrient_level_var['HIGH']
            ))

            # Uno VERY_HIGH y otro HIGH
            self.rules.append(ctrl.Rule(
                (nitrogen_level['VERY HIGH'] & phosphorus_level['HIGH']) | (nitrogen_level['HIGH'] & phosphorus_level['VERY HIGH']),
                self.nutrient_level_var['VERY HIGH']
            ))

            # Uno MODERATE y otro LOW
            self.rules.append(ctrl.Rule(
                (nitrogen_level['MODERATE'] & phosphorus_level['LOW']) | (nitrogen_level['LOW'] & phosphorus_level['MODERATE']),
                self.nutrient_level_var['MODERATE']
            ))

            # Uno HIGH y otro LOW
            self.rules.append(ctrl.Rule(
                (nitrogen_level['HIGH'] & phosphorus_level['LOW']) | (nitrogen_level['LOW'] & phosphorus_level['HIGH']),
                self.nutrient_level_var['MODERATE']
            ))

            # Uno VERY_HIGH y otro LOW
            self.rules.append(ctrl.Rule(
                (nitrogen_level['VERY HIGH'] & phosphorus_level['LOW']) | (nitrogen_level['LOW'] & phosphorus_level['VERY HIGH']),
                self.nutrient_level_var['MODERATE']
            ))

            # Uno VERY_HIGH y otro MODERATE
            self.rules.append(ctrl.Rule(
                (nitrogen_level['VERY HIGH'] & phosphorus_level['MODERATE']) | (nitrogen_level['MODERATE'] & phosphorus_level['VERY HIGH']),
                self.nutrient_level_var['HIGH']
            ))

            # Si la diferencia es más de un nivel, el nivel es el más bajo
            self.rules.append(ctrl.Rule(
                (nitrogen_level['VERY HIGH'] & phosphorus_level['LOW']) | (nitrogen_level['LOW'] & phosphorus_level['VERY HIGH']),
                self.nutrient_level_var['MODERATE']
            ))

        else:
            # Si solo una variable está disponible, el nivel de nutrient_level es el mismo que la variable disponible
            for var_name in ['nitrogen_level', 'phosphorus_level']:
                if var_name in self.vars:
                    antecedent = self.vars[var_name]
                    self.rules.append(ctrl.Rule(antecedent['LOW'], self.nutrient_level_var['LOW']))
                    self.rules.append(ctrl.Rule(antecedent['MODERATE'], self.nutrient_level_var['MODERATE']))
                    self.rules.append(ctrl.Rule(antecedent['HIGH'], self.nutrient_level_var['HIGH']))
                    self.rules.append(ctrl.Rule(antecedent['VERY HIGH'], self.nutrient_level_var['VERY HIGH']))

    def calculate_inference(self):
        # Asignar los valuees de entrada disponibles
        if 'nitrogen_level' in self.vars:
            self.simulation.input['nitrogen_level'] = self.nitrogen_level
        if 'phosphorus_level' in self.vars:
            self.simulation.input['phosphorus_level'] = self.phosphorus_level

        try:
            # Realizar la inferencia
            self.simulation.compute()

            # Obtener el resultado
            self.nutrient_level = self.simulation.output['nutrient_level']
        except Exception as e:
            raise ValueError(f"Error al calcular la inferencia: {e}")

        # Determinar vars usadas y confidence
        if 'nitrogen_level' in self.vars and 'phosphorus_level' in self.vars:
            used_vars = 'NITROGEN_PHOSPHORUS'
            confidence = 1.0
        else:
            used_vars = 'NITROGEN' if 'nitrogen_level' in self.vars else 'PHOSPHORUS'
            confidence = 0.5

        return (used_vars, confidence)

    def get_label(self):
        if np.isnan(self.nutrient_level):
            raise ValueError("No se ha calculado la inferencia de nivel de nutrient_level.")

        # Determinar la label con mayor degree de pertenencia
        membership_degrees = {}
        for label in self.nutrient_level_var.terms:
            membership_function = self.nutrient_level_var[label].mf
            degree = fuzz.interp_membership(self.nutrient_level_var.universe, membership_function, self.nutrient_level)
            membership_degrees[label] = degree

        predicted_label = max(membership_degrees, key=membership_degrees.get)
        return predicted_label
