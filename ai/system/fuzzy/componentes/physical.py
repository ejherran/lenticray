import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class PhysicalConditions:
    def __init__(self, solids_level=np.nan, visibility_level=np.nan):
        self.solids_level = solids_level
        self.visibility_level = visibility_level
        self.physical_conditions = np.nan

        # Verificar que al menos una variable esté disponible
        if np.isnan(self.solids_level) and np.isnan(self.visibility_level):
            raise ValueError("Se requiere al menos solids_level o visibility_level para evaluar las condiciones físicas.")

        # Determinar vars disponibles
        self.available_vars = []
        if not np.isnan(self.solids_level):
            self.available_vars.append('solids_level')
        if not np.isnan(self.visibility_level):
            self.available_vars.append('visibility_level')

        # Crear el sistema difuso según las vars disponibles
        self._create_fuzzy_system()

    def _create_fuzzy_system(self):
        # Definir la variable de salida
        self.physical_conditions_universe = np.arange(0, 1.01, 0.01)
        self.physical_conditions_var = ctrl.Consequent(self.physical_conditions_universe, 'physical_conditions')
        self.physical_conditions_var['GOOD'] = fuzz.trapmf(self.physical_conditions_var.universe, [0, 0, 0.2, 0.3])
        self.physical_conditions_var['NEUTRALS'] = fuzz.trimf(self.physical_conditions_var.universe, [0.25, 0.4, 0.55])
        self.physical_conditions_var['BAD'] = fuzz.trimf(self.physical_conditions_var.universe, [0.5, 0.65, 0.8])
        self.physical_conditions_var['VERY BAD'] = fuzz.trapmf(self.physical_conditions_var.universe, [0.75, 0.85, 1, 1])

        self.rules = []
        self.vars = {}

        # Definir vars difusas según las vars disponibles
        if 'solids_level' in self.available_vars:
            # Definir el universo de discurso para solids_level
            self.solids_level_universe = np.arange(0, 1.01, 0.01)
            self.solids_level_var = ctrl.Antecedent(self.solids_level_universe, 'solids_level')
            self.solids_level_var['LOW'] = fuzz.trapmf(self.solids_level_var.universe, [0, 0, 0.2, 0.4])
            self.solids_level_var['MODERATE'] = fuzz.trimf(self.solids_level_var.universe, [0.3, 0.5, 0.7])
            self.solids_level_var['HIGH'] = fuzz.trimf(self.solids_level_var.universe, [0.6, 0.75, 0.9])
            self.solids_level_var['VERY HIGH'] = fuzz.trapmf(self.solids_level_var.universe, [0.85, 0.95, 1, 1])
            self.vars['solids_level'] = self.solids_level_var

        if 'visibility_level' in self.available_vars:
            # Definir el universo de discurso para visibility_level
            self.visibility_level_universe = np.arange(0, 1.01, 0.01)
            self.visibility_level_var = ctrl.Antecedent(self.visibility_level_universe, 'visibility_level')
            self.visibility_level_var['LOW'] = fuzz.trapmf(self.visibility_level_var.universe, [0, 0, 0.2, 0.4])
            self.visibility_level_var['MODERATE'] = fuzz.trimf(self.visibility_level_var.universe, [0.3, 0.5, 0.7])
            self.visibility_level_var['HIGH'] = fuzz.trimf(self.visibility_level_var.universe, [0.6, 0.75, 0.9])
            self.visibility_level_var['VERY HIGH'] = fuzz.trapmf(self.visibility_level_var.universe, [0.85, 0.95, 1, 1])
            self.vars['visibility_level'] = self.visibility_level_var

        # Definir las reglas difusas según las vars disponibles
        self._define_rules()

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def _define_rules(self):
        # Reglas basadas en las vars disponibles
        if 'solids_level' in self.vars and 'visibility_level' in self.vars:
            # Ambas vars están disponibles
            solids_level = self.vars['solids_level']
            visibility_level = self.vars['visibility_level']

            self.rules.append(ctrl.Rule(visibility_level['VERY HIGH'] & (solids_level['LOW'] | solids_level['MODERATE']), self.physical_conditions_var['GOOD']))
            self.rules.append(ctrl.Rule(visibility_level['VERY HIGH'] & (solids_level['HIGH'] | solids_level['VERY HIGH']), self.physical_conditions_var['NEUTRALS']))

            self.rules.append(ctrl.Rule(visibility_level['HIGH'] & solids_level['LOW'], self.physical_conditions_var['GOOD']))
            self.rules.append(ctrl.Rule(visibility_level['HIGH'] & (solids_level['MODERATE'] | solids_level['HIGH'] | solids_level['VERY HIGH']), self.physical_conditions_var['NEUTRALS']))

            self.rules.append(ctrl.Rule(visibility_level['MODERATE'] & (solids_level['LOW'] | solids_level['MODERATE']), self.physical_conditions_var['NEUTRALS']))
            self.rules.append(ctrl.Rule(visibility_level['MODERATE'] & (solids_level['HIGH'] | solids_level['VERY HIGH']), self.physical_conditions_var['BAD']))

            self.rules.append(ctrl.Rule(visibility_level['LOW'] & solids_level['LOW'], self.physical_conditions_var['NEUTRALS']))
            self.rules.append(ctrl.Rule(visibility_level['LOW'] & (solids_level['MODERATE'] | solids_level['HIGH']), self.physical_conditions_var['BAD']))
            self.rules.append(ctrl.Rule(visibility_level['LOW'] & (solids_level['VERY HIGH']), self.physical_conditions_var['VERY BAD']))

        elif 'solids_level' in self.vars:
            # Solo solids_level está disponible
            solids_level = self.vars['solids_level']
            self.rules.append(ctrl.Rule(solids_level['LOW'], self.physical_conditions_var['GOOD']))
            self.rules.append(ctrl.Rule(solids_level['MODERATE'], self.physical_conditions_var['NEUTRALS']))
            self.rules.append(ctrl.Rule(solids_level['HIGH'], self.physical_conditions_var['BAD']))
            self.rules.append(ctrl.Rule(solids_level['VERY HIGH'], self.physical_conditions_var['VERY BAD']))

        elif 'visibility_level' in self.vars:
            # Solo visibility_level está disponible
            visibility_level = self.vars['visibility_level']
            self.rules.append(ctrl.Rule(visibility_level['VERY HIGH'], self.physical_conditions_var['GOOD']))
            self.rules.append(ctrl.Rule(visibility_level['HIGH'], self.physical_conditions_var['NEUTRALS']))
            self.rules.append(ctrl.Rule(visibility_level['MODERATE'], self.physical_conditions_var['BAD']))
            self.rules.append(ctrl.Rule(visibility_level['LOW'], self.physical_conditions_var['VERY BAD']))

    def calculate_inference(self):
        # Asignar los valuees de entrada disponibles
        if 'solids_level' in self.vars:
            self.simulation.input['solids_level'] = self.solids_level
        if 'visibility_level' in self.vars:
            self.simulation.input['visibility_level'] = self.visibility_level

        try:
            # Realizar la inferencia
            self.simulation.compute()

            # Obtener el resultado
            self.physical_conditions = self.simulation.output['physical_conditions']
        except Exception as e:
            raise ValueError(f"Error al calcular la inferencia: {e}")

        # Determinar vars usadas y confidence
        if 'solids_level' in self.vars and 'visibility_level' in self.vars:
            used_vars = 'SOLIDS_VISIBILITY'
            confidence = 1.0
        elif 'solids_level' in self.vars:
            used_vars = 'SOLIDS'
            confidence = 0.5
        elif 'visibility_level' in self.vars:
            used_vars = 'VISIBILITY'
            confidence = 0.5

        return (used_vars, confidence)

    def get_label(self):
        if np.isnan(self.physical_conditions):
            raise ValueError("No se ha calculado la inferencia de condiciones físicas.")

        # Determinar la label con mayor degree de pertenencia
        membership_degrees = {}
        for label in self.physical_conditions_var.terms:
            membership_function = self.physical_conditions_var[label].mf
            degree = fuzz.interp_membership(self.physical_conditions_var.universe, membership_function, self.physical_conditions)
            membership_degrees[label] = degree

        predicted_label = max(membership_degrees, key=membership_degrees.get)
        return predicted_label
