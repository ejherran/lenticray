import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class ChemicalConditions:
    def __init__(self, nutrient_level=np.nan, oxygen_balance=np.nan):
        self.nutrient_level = nutrient_level
        self.oxygen_balance = oxygen_balance
        self.chemical_conditions = np.nan

        # Verificar que al menos una variable esté disponible
        if np.isnan(self.nutrient_level) and np.isnan(self.oxygen_balance):
            raise ValueError("Se requiere al menos nutrient_level o oxygen_balance para evaluar las condiciones químicas.")

        # Determinar vars disponibles
        self.available_vars = []
        if not np.isnan(self.nutrient_level):
            self.available_vars.append('nutrient_level')
        if not np.isnan(self.oxygen_balance):
            self.available_vars.append('oxygen_balance')

        # Crear el sistema difuso según las vars disponibles
        self._create_fuzzy_system()

    def _create_fuzzy_system(self):
        # Definir la variable de salida
        self.chemical_conditions_universe = np.arange(0, 1.01, 0.01)
        self.chemical_conditions_var = ctrl.Consequent(self.chemical_conditions_universe, 'chemical_conditions')
        self.chemical_conditions_var['GOOD'] = fuzz.trapmf(self.chemical_conditions_var.universe, [0, 0, 0.2, 0.35])
        self.chemical_conditions_var['NEUTRALS'] = fuzz.trimf(self.chemical_conditions_var.universe, [0.3, 0.45, 0.6])
        self.chemical_conditions_var['BAD'] = fuzz.trimf(self.chemical_conditions_var.universe, [0.55, 0.7, 0.85])
        self.chemical_conditions_var['VERY BAD'] = fuzz.trapmf(self.chemical_conditions_var.universe, [0.8, 0.9, 1, 1])

        self.rules = []
        self.vars = {}

        # Definir vars difusas según las vars disponibles
        if 'nutrient_level' in self.available_vars:
            # Definir el universo de discurso para nutrient_level
            self.nutrient_level_universe = np.arange(0, 1.01, 0.01)
            self.nutrient_level_var = ctrl.Antecedent(self.nutrient_level_universe, 'nutrient_level')
            self.nutrient_level_var['LOW'] = fuzz.trapmf(self.nutrient_level_var.universe, [0, 0, 0.2, 0.4])
            self.nutrient_level_var['MODERATE'] = fuzz.trimf(self.nutrient_level_var.universe, [0.3, 0.5, 0.7])
            self.nutrient_level_var['HIGH'] = fuzz.trimf(self.nutrient_level_var.universe, [0.6, 0.75, 0.9])
            self.nutrient_level_var['VERY HIGH'] = fuzz.trapmf(self.nutrient_level_var.universe, [0.85, 0.95, 1, 1])
            self.vars['nutrient_level'] = self.nutrient_level_var

        if 'oxygen_balance' in self.available_vars:
            # Definir el universo de discurso para oxygen_balance
            self.oxygen_balance_universe = np.arange(0, 1.01, 0.01)
            self.oxygen_balance_var = ctrl.Antecedent(self.oxygen_balance_universe, 'oxygen_balance')
            self.oxygen_balance_var['GOOD'] = fuzz.trapmf(self.oxygen_balance_var.universe, [0, 0, 0.2, 0.4])
            self.oxygen_balance_var['MODERATE'] = fuzz.trimf(self.oxygen_balance_var.universe, [0.3, 0.5, 0.7])
            self.oxygen_balance_var['BAD'] = fuzz.trimf(self.oxygen_balance_var.universe, [0.6, 0.75, 0.9])
            self.oxygen_balance_var['VERY BAD'] = fuzz.trapmf(self.oxygen_balance_var.universe, [0.85, 0.95, 1, 1])
            self.vars['oxygen_balance'] = self.oxygen_balance_var

        # Definir las reglas difusas según las vars disponibles
        self._define_rules()

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def _define_rules(self):
        # Reglas basadas en las vars disponibles
        if 'nutrient_level' in self.vars and 'oxygen_balance' in self.vars:
            # Ambas vars están disponibles
            nutrient_level = self.vars['nutrient_level']
            oxygen_balance = self.vars['oxygen_balance']

            # Regla 1
            self.rules.append(ctrl.Rule(nutrient_level['LOW'] & oxygen_balance['GOOD'], self.chemical_conditions_var['GOOD']))

            # Regla 2
            self.rules.append(ctrl.Rule(nutrient_level['LOW'] & oxygen_balance['MODERATE'], self.chemical_conditions_var['GOOD']))

            # Regla 3
            self.rules.append(ctrl.Rule(nutrient_level['LOW'] & (oxygen_balance['BAD'] | oxygen_balance['VERY BAD']), self.chemical_conditions_var['NEUTRALS']))

            # Regla 4
            self.rules.append(ctrl.Rule(nutrient_level['MODERATE'] & oxygen_balance['GOOD'], self.chemical_conditions_var['NEUTRALS']))

            # Regla 5
            self.rules.append(ctrl.Rule(nutrient_level['MODERATE'] & oxygen_balance['MODERATE'], self.chemical_conditions_var['NEUTRALS']))

            # Regla 6
            self.rules.append(ctrl.Rule(nutrient_level['MODERATE'] & (oxygen_balance['BAD'] | oxygen_balance['VERY BAD']), self.chemical_conditions_var['BAD']))

            # Regla 7
            self.rules.append(ctrl.Rule((nutrient_level['HIGH'] | nutrient_level['VERY HIGH']) & oxygen_balance['GOOD'], self.chemical_conditions_var['BAD']))

            # Regla 8
            self.rules.append(ctrl.Rule((nutrient_level['HIGH'] | nutrient_level['VERY HIGH']) & oxygen_balance['MODERATE'], self.chemical_conditions_var['BAD']))

            # Regla 9
            self.rules.append(ctrl.Rule((nutrient_level['HIGH'] | nutrient_level['VERY HIGH']) & (oxygen_balance['BAD'] | oxygen_balance['VERY BAD']), self.chemical_conditions_var['VERY BAD']))

        elif 'nutrient_level' in self.vars:
            # Solo nivel de nutrient_level está disponible
            nutrient_level = self.vars['nutrient_level']
            self.rules.append(ctrl.Rule(nutrient_level['LOW'], self.chemical_conditions_var['GOOD']))
            self.rules.append(ctrl.Rule(nutrient_level['MODERATE'], self.chemical_conditions_var['NEUTRALS']))
            self.rules.append(ctrl.Rule(nutrient_level['HIGH'], self.chemical_conditions_var['BAD']))
            self.rules.append(ctrl.Rule(nutrient_level['VERY HIGH'], self.chemical_conditions_var['VERY BAD']))

        elif 'oxygen_balance' in self.vars:
            # Solo balance de oxígeno está disponible
            oxygen_balance = self.vars['oxygen_balance']
            self.rules.append(ctrl.Rule(oxygen_balance['GOOD'], self.chemical_conditions_var['GOOD']))
            self.rules.append(ctrl.Rule(oxygen_balance['MODERATE'], self.chemical_conditions_var['NEUTRALS']))
            self.rules.append(ctrl.Rule(oxygen_balance['BAD'], self.chemical_conditions_var['BAD']))
            self.rules.append(ctrl.Rule(oxygen_balance['VERY BAD'], self.chemical_conditions_var['VERY BAD']))

    def calculate_inference(self):
        # Asignar los valuees de entrada disponibles
        if 'nutrient_level' in self.vars:
            self.simulation.input['nutrient_level'] = self.nutrient_level
        if 'oxygen_balance' in self.vars:
            self.simulation.input['oxygen_balance'] = self.oxygen_balance

        try:
            # Realizar la inferencia
            self.simulation.compute()

            # Obtener el resultado
            self.chemical_conditions = self.simulation.output['chemical_conditions']
        except Exception as e:
            raise ValueError(f"Error al calcular la inferencia: {e}")

        # Determinar vars usadas y confidence
        if 'nutrient_level' in self.vars and 'oxygen_balance' in self.vars:
            used_vars = 'NUTRIENTS_OXYGEN'
            confidence = 1.0
        elif 'nutrient_level' in self.vars:
            used_vars = 'NUTRIENTS'
            confidence = 0.8
        elif 'oxygen_balance' in self.vars:
            used_vars = 'OXYGEN'
            confidence = 0.3

        return (used_vars, confidence)

    def get_label(self):
        if np.isnan(self.chemical_conditions):
            raise ValueError("No se ha calculado la inferencia de condiciones químicas.")

        # Determinar la label con mayor degree de pertenencia
        membership_degrees = {}
        for label in self.chemical_conditions_var.terms:
            membership_function = self.chemical_conditions_var[label].mf
            degree = fuzz.interp_membership(self.chemical_conditions_var.universe, membership_function, self.chemical_conditions)
            membership_degrees[label] = degree

        predicted_label = max(membership_degrees, key=membership_degrees.get)
        return predicted_label

