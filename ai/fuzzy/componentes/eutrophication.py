import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class EutrophicationLevel:
    def __init__(
        self,
        chemical_conditions=np.nan,
        physical_conditions=np.nan,
        additional_conditions=np.nan,
    ):
        self.chemical_conditions = chemical_conditions
        self.physical_conditions = physical_conditions
        self.additional_conditions = additional_conditions
        self.eutrophication_level = np.nan

        # Verificar que al menos una variable esté disponible
        if np.isnan(self.chemical_conditions) and np.isnan(self.physical_conditions) and np.isnan(self.additional_conditions):
            raise ValueError("Se requiere al menos chemical_conditions, physical_conditions o additional_conditions para evaluar el nivel de eutrofización.")

        # Determinar vars disponibles
        self.available_vars = []
        if not np.isnan(self.chemical_conditions):
            self.available_vars.append('chemical_conditions')
        if not np.isnan(self.physical_conditions):
            self.available_vars.append('physical_conditions')
        if not np.isnan(self.additional_conditions):
            self.available_vars.append('additional_conditions')

        # Crear el sistema difuso según las vars disponibles
        self._create_fuzzy_system()

    def _create_fuzzy_system(self):
        # Definir la variable de salida
        self.eutrophication_level_universe = np.arange(0, 1.01, 0.01)
        self.eutrophication_level_var = ctrl.Consequent(self.eutrophication_level_universe, 'eutrophication_level')
        self.eutrophication_level_var['OLIGOTROPHIC'] = fuzz.trapmf(self.eutrophication_level_var.universe, [0, 0, 0.2, 0.3])
        self.eutrophication_level_var['MESOTROPHIC'] = fuzz.trimf(self.eutrophication_level_var.universe, [0.25, 0.4, 0.55])
        self.eutrophication_level_var['EUTROPHIC'] = fuzz.trimf(self.eutrophication_level_var.universe, [0.5, 0.65, 0.8])
        self.eutrophication_level_var['HYPEREUTROPHIC'] = fuzz.trapmf(self.eutrophication_level_var.universe, [0.75, 0.85, 1, 1])

        self.rules = []
        self.vars = {}

        # Definir vars difusas según las vars disponibles
        if 'chemical_conditions' in self.available_vars:
            # Definir el universo de discurso para chemical_conditions
            self.chemical_conditions_universe = np.arange(0, 1.01, 0.01)
            self.chemical_conditions_var = ctrl.Antecedent(self.chemical_conditions_universe, 'chemical_conditions')
            self.chemical_conditions_var['GOOD'] = fuzz.trapmf(self.chemical_conditions_var.universe, [0, 0, 0.2, 0.35])
            self.chemical_conditions_var['NEUTRALS'] = fuzz.trimf(self.chemical_conditions_var.universe, [0.3, 0.45, 0.6])
            self.chemical_conditions_var['BAD'] = fuzz.trimf(self.chemical_conditions_var.universe, [0.55, 0.7, 0.85])
            self.chemical_conditions_var['VERY BAD'] = fuzz.trapmf(self.chemical_conditions_var.universe, [0.8, 0.9, 1, 1])
            self.vars['chemical_conditions'] = self.chemical_conditions_var

        if 'physical_conditions' in self.available_vars:
            # Definir el universo de discurso para physical_conditions
            self.physical_conditions_universe = np.arange(0, 1.01, 0.01)
            self.physical_conditions_var = ctrl.Antecedent(self.physical_conditions_universe, 'physical_conditions')
            self.physical_conditions_var['GOOD'] = fuzz.trapmf(self.physical_conditions_var.universe, [0, 0, 0.2, 0.3])
            self.physical_conditions_var['NEUTRALS'] = fuzz.trimf(self.physical_conditions_var.universe, [0.25, 0.4, 0.55])
            self.physical_conditions_var['BAD'] = fuzz.trimf(self.physical_conditions_var.universe, [0.5, 0.65, 0.8])
            self.physical_conditions_var['VERY BAD'] = fuzz.trapmf(self.physical_conditions_var.universe, [0.75, 0.85, 1, 1])
            self.vars['physical_conditions'] = self.physical_conditions_var

        if 'additional_conditions' in self.available_vars:
            self.additional_conditions_universe = np.arange(0, 1.01, 0.01)
            self.additional_conditions_var = ctrl.Antecedent(self.additional_conditions_universe, 'additional_conditions')
            self.additional_conditions_var['UNFAVORABLE'] = fuzz.trapmf(self.additional_conditions_var.universe, [0, 0, 0.2, 0.4])
            self.additional_conditions_var['NEUTRALS'] = fuzz.trimf(self.additional_conditions_var.universe, [0.3, 0.5, 0.7])
            self.additional_conditions_var['FAVORABLE'] = fuzz.trapmf(self.additional_conditions_var.universe, [0.6, 0.8, 1, 1])
            self.vars['additional_conditions'] = self.additional_conditions_var


        # Definir las reglas difusas según las vars disponibles
        self._define_rules()

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def _define_rules(self):
        # Reglas basadas en las vars disponibles
        if 'chemical_conditions' in self.vars and 'physical_conditions' in self.vars and 'additional_conditions' in self.vars:
            # Todas las vars están disponibles
            chemical_conditions = self.vars['chemical_conditions']
            physical_conditions = self.vars['physical_conditions']
            additional_conditions = self.vars['additional_conditions']

            # Regla 1a
            self.rules.append(ctrl.Rule(
                chemical_conditions['GOOD'] & (physical_conditions['GOOD'] | physical_conditions['NEUTRALS'] | physical_conditions['BAD']) & additional_conditions['UNFAVORABLE'],
                self.eutrophication_level_var['OLIGOTROPHIC']
            ))

            # Regla 1b
            self.rules.append(ctrl.Rule(
                chemical_conditions['GOOD'] & (physical_conditions['GOOD'] | physical_conditions['NEUTRALS'] | physical_conditions['BAD']) & additional_conditions['NEUTRALS'],
                self.eutrophication_level_var['OLIGOTROPHIC']
            ))

            # Regla 1c
            self.rules.append(ctrl.Rule(
                chemical_conditions['GOOD'] & (physical_conditions['GOOD'] | physical_conditions['NEUTRALS'] | physical_conditions['BAD']) & additional_conditions['FAVORABLE'],
                self.eutrophication_level_var['MESOTROPHIC']
            ))

            # Regla 2a
            self.rules.append(ctrl.Rule(
                chemical_conditions['GOOD'] & physical_conditions['VERY BAD'] & additional_conditions['UNFAVORABLE'],
                self.eutrophication_level_var['OLIGOTROPHIC']
            ))

            # Regla 2b
            self.rules.append(ctrl.Rule(
                chemical_conditions['GOOD'] & physical_conditions['VERY BAD'] & additional_conditions['NEUTRALS'],
                self.eutrophication_level_var['MESOTROPHIC']
            ))

            # Regla 2c
            self.rules.append(ctrl.Rule(
                chemical_conditions['GOOD'] & physical_conditions['VERY BAD'] & additional_conditions['FAVORABLE'],
                self.eutrophication_level_var['EUTROPHIC']
            ))

            # Regla 3a
            self.rules.append(ctrl.Rule(
                chemical_conditions['NEUTRALS'] & physical_conditions['GOOD'] & additional_conditions['UNFAVORABLE'],
                self.eutrophication_level_var['OLIGOTROPHIC']
            ))

            # Regla 3b
            self.rules.append(ctrl.Rule(
                chemical_conditions['NEUTRALS'] & physical_conditions['GOOD'] & additional_conditions['NEUTRALS'],
                self.eutrophication_level_var['OLIGOTROPHIC']
            ))

            # Regla 3c
            self.rules.append(ctrl.Rule(
                chemical_conditions['NEUTRALS'] & physical_conditions['GOOD'] & additional_conditions['FAVORABLE'],
                self.eutrophication_level_var['MESOTROPHIC']
            ))

            # Regla 4a
            self.rules.append(ctrl.Rule(
                chemical_conditions['NEUTRALS'] & physical_conditions['NEUTRALS'] & additional_conditions['UNFAVORABLE'],
                self.eutrophication_level_var['OLIGOTROPHIC']
            ))

            # Regla 4b
            self.rules.append(ctrl.Rule(
                chemical_conditions['NEUTRALS'] & physical_conditions['NEUTRALS'] & additional_conditions['NEUTRALS'],
                self.eutrophication_level_var['MESOTROPHIC']
            ))

            # Regla 4c
            self.rules.append(ctrl.Rule(
                chemical_conditions['NEUTRALS'] & physical_conditions['NEUTRALS'] & additional_conditions['FAVORABLE'],
                self.eutrophication_level_var['EUTROPHIC']
            ))

            # Regla 5a
            self.rules.append(ctrl.Rule(
                chemical_conditions['NEUTRALS'] & (physical_conditions['BAD'] | physical_conditions['VERY BAD']) & additional_conditions['UNFAVORABLE'],
                self.eutrophication_level_var['MESOTROPHIC']
            ))

            # Regla 5b
            self.rules.append(ctrl.Rule(
                chemical_conditions['NEUTRALS'] & (physical_conditions['BAD'] | physical_conditions['VERY BAD']) & additional_conditions['NEUTRALS'],
                self.eutrophication_level_var['EUTROPHIC']
            ))

            # Regla 5c
            self.rules.append(ctrl.Rule(
                chemical_conditions['NEUTRALS'] & (physical_conditions['BAD'] | physical_conditions['VERY BAD']) & additional_conditions['FAVORABLE'],
                self.eutrophication_level_var['HYPEREUTROPHIC']
            ))

            # Regla 6a
            self.rules.append(ctrl.Rule(
                chemical_conditions['BAD'] & physical_conditions['GOOD'] & additional_conditions['UNFAVORABLE'],
                self.eutrophication_level_var['OLIGOTROPHIC']
            ))

            # Regla 6b
            self.rules.append(ctrl.Rule(
                chemical_conditions['BAD'] & physical_conditions['GOOD'] & additional_conditions['NEUTRALS'],
                self.eutrophication_level_var['MESOTROPHIC']
            ))

            # Regla 6c
            self.rules.append(ctrl.Rule(
                chemical_conditions['BAD'] & physical_conditions['GOOD'] & additional_conditions['FAVORABLE'],
                self.eutrophication_level_var['EUTROPHIC']
            ))

            # Regla 7a
            self.rules.append(ctrl.Rule(
                chemical_conditions['BAD'] & (physical_conditions['NEUTRALS'] | physical_conditions['BAD']) & additional_conditions['UNFAVORABLE'],
                self.eutrophication_level_var['MESOTROPHIC']
            ))

            # Regla 7b
            self.rules.append(ctrl.Rule(
                chemical_conditions['BAD'] & (physical_conditions['NEUTRALS'] | physical_conditions['BAD']) & additional_conditions['NEUTRALS'],
                self.eutrophication_level_var['EUTROPHIC']
            ))

            # Regla 7c
            self.rules.append(ctrl.Rule(
                chemical_conditions['BAD'] & (physical_conditions['NEUTRALS'] | physical_conditions['BAD']) & additional_conditions['FAVORABLE'],
                self.eutrophication_level_var['HYPEREUTROPHIC']
            ))

            # Regla 8a
            self.rules.append(ctrl.Rule(
                chemical_conditions['BAD'] & physical_conditions['VERY BAD'] & additional_conditions['UNFAVORABLE'],
                self.eutrophication_level_var['EUTROPHIC']
            ))

            # Regla 8b
            self.rules.append(ctrl.Rule(
                chemical_conditions['BAD'] & physical_conditions['VERY BAD'] & additional_conditions['NEUTRALS'],
                self.eutrophication_level_var['HYPEREUTROPHIC']
            ))

            # Regla 8c
            self.rules.append(ctrl.Rule(
                chemical_conditions['BAD'] & physical_conditions['VERY BAD'] & additional_conditions['FAVORABLE'],
                self.eutrophication_level_var['HYPEREUTROPHIC']
            ))

            # Regla 9a
            self.rules.append(ctrl.Rule(
                chemical_conditions['VERY BAD'] & (physical_conditions['GOOD'] | physical_conditions['NEUTRALS']) & additional_conditions['UNFAVORABLE'],
                self.eutrophication_level_var['MESOTROPHIC']
            ))

            # Regla 9b
            self.rules.append(ctrl.Rule(
                chemical_conditions['VERY BAD'] & (physical_conditions['GOOD'] | physical_conditions['NEUTRALS']) & additional_conditions['NEUTRALS'],
                self.eutrophication_level_var['EUTROPHIC']
            ))

            # Regla 9c
            self.rules.append(ctrl.Rule(
                chemical_conditions['VERY BAD'] & (physical_conditions['GOOD'] | physical_conditions['NEUTRALS']) & additional_conditions['FAVORABLE'],
                self.eutrophication_level_var['HYPEREUTROPHIC']
            ))

            # Regla 10a
            self.rules.append(ctrl.Rule(
                chemical_conditions['VERY BAD'] & (physical_conditions['BAD'] | physical_conditions['VERY BAD']) & additional_conditions['UNFAVORABLE'],
                self.eutrophication_level_var['EUTROPHIC']
            ))

            # Regla 10b
            self.rules.append(ctrl.Rule(
                chemical_conditions['VERY BAD'] & (physical_conditions['BAD'] | physical_conditions['VERY BAD']) & additional_conditions['NEUTRALS'],
                self.eutrophication_level_var['HYPEREUTROPHIC']
            ))

            # Regla 10c
            self.rules.append(ctrl.Rule(
                chemical_conditions['VERY BAD'] & (physical_conditions['BAD'] | physical_conditions['VERY BAD']) & additional_conditions['FAVORABLE'],
                self.eutrophication_level_var['HYPEREUTROPHIC']
            ))

        elif 'chemical_conditions' in self.vars and 'physical_conditions' in self.vars:
            # Ambas vars están disponibles
            chemical_conditions = self.vars['chemical_conditions']
            physical_conditions = self.vars['physical_conditions']

            self.rules.append(ctrl.Rule(chemical_conditions['GOOD'] & (physical_conditions['GOOD'] | physical_conditions['NEUTRALS'] | physical_conditions['BAD']), self.eutrophication_level_var['OLIGOTROPHIC']))
            self.rules.append(ctrl.Rule(chemical_conditions['GOOD'] & physical_conditions['VERY BAD'], self.eutrophication_level_var['MESOTROPHIC']))

            self.rules.append(ctrl.Rule(chemical_conditions['NEUTRALS'] & physical_conditions['GOOD'], self.eutrophication_level_var['OLIGOTROPHIC']))
            self.rules.append(ctrl.Rule(chemical_conditions['NEUTRALS'] & (physical_conditions['NEUTRALS']), self.eutrophication_level_var['MESOTROPHIC']))
            self.rules.append(ctrl.Rule(chemical_conditions['NEUTRALS'] & (physical_conditions['BAD'] | physical_conditions['VERY BAD']), self.eutrophication_level_var['EUTROPHIC']))

            self.rules.append(ctrl.Rule(chemical_conditions['BAD'] & physical_conditions['GOOD'], self.eutrophication_level_var['MESOTROPHIC']))
            self.rules.append(ctrl.Rule(chemical_conditions['BAD'] & (physical_conditions['NEUTRALS'] | physical_conditions['BAD']), self.eutrophication_level_var['EUTROPHIC']))
            self.rules.append(ctrl.Rule(chemical_conditions['BAD'] & physical_conditions['VERY BAD'], self.eutrophication_level_var['HYPEREUTROPHIC']))

            self.rules.append(ctrl.Rule(chemical_conditions['VERY BAD'] & (physical_conditions['GOOD'] | physical_conditions['NEUTRALS']), self.eutrophication_level_var['EUTROPHIC']))
            self.rules.append(ctrl.Rule(chemical_conditions['VERY BAD'] & (physical_conditions['BAD'] | physical_conditions['VERY BAD']), self.eutrophication_level_var['HYPEREUTROPHIC']))
        
        elif 'chemical_conditions' in self.vars:
            # Solo condiciones químicas están disponibles
            chemical_conditions = self.vars['chemical_conditions']
            self.rules.append(ctrl.Rule(chemical_conditions['GOOD'], self.eutrophication_level_var['OLIGOTROPHIC']))
            self.rules.append(ctrl.Rule(chemical_conditions['NEUTRALS'], self.eutrophication_level_var['MESOTROPHIC']))
            self.rules.append(ctrl.Rule(chemical_conditions['BAD'], self.eutrophication_level_var['EUTROPHIC']))
            self.rules.append(ctrl.Rule(chemical_conditions['VERY BAD'], self.eutrophication_level_var['HYPEREUTROPHIC']))

        elif 'physical_conditions' in self.vars:
            # Solo condiciones physical_conditions están disponibles
            physical_conditions = self.vars['physical_conditions']
            self.rules.append(ctrl.Rule(physical_conditions['GOOD'], self.eutrophication_level_var['OLIGOTROPHIC']))
            self.rules.append(ctrl.Rule(physical_conditions['NEUTRALS'], self.eutrophication_level_var['MESOTROPHIC']))
            self.rules.append(ctrl.Rule(physical_conditions['BAD'], self.eutrophication_level_var['EUTROPHIC']))
            self.rules.append(ctrl.Rule(physical_conditions['VERY BAD'], self.eutrophication_level_var['HYPEREUTROPHIC']))

        elif 'additional_conditions' in self.vars:
            additional_conditions = self.vars['additional_conditions']
            self.rules.append(ctrl.Rule(additional_conditions['UNFAVORABLE'], self.eutrophication_level_var['OLIGOTROPHIC']))
            self.rules.append(ctrl.Rule(additional_conditions['NEUTRALS'], self.eutrophication_level_var['MESOTROPHIC']))
            self.rules.append(ctrl.Rule(additional_conditions['FAVORABLE'], self.eutrophication_level_var['EUTROPHIC']))


    def calculate_inference(self):
        # Asignar los valuees de entrada disponibles
        if 'chemical_conditions' in self.vars:
            self.simulation.input['chemical_conditions'] = self.chemical_conditions
        if 'physical_conditions' in self.vars:
            self.simulation.input['physical_conditions'] = self.physical_conditions
        if 'additional_conditions' in self.vars:
            self.simulation.input['additional_conditions'] = self.additional_conditions

        try:
            # Realizar la inferencia
            self.simulation.compute()

            # Obtener el resultado
            self.eutrophication_level = self.simulation.output['eutrophication_level']
        except Exception as e:
            raise ValueError(f"Error al calcular la inferencia: {e}")

        # Determinar vars usadas y confidence
        if 'chemical_conditions' in self.vars and 'physical_conditions' in self.vars and 'additional_conditions' in self.vars:
            used_vars = 'CHEMICALS_PHYSICAL_ADDITIONALS'
            confidence = 1.0
        elif 'chemical_conditions' in self.vars and 'physical_conditions' in self.vars:
            used_vars = 'CHEMICALS_PHYSICAL'
            confidence = 0.9
        elif 'chemical_conditions' in self.vars:
            used_vars = 'CHEMICALS'
            confidence = 0.75
        elif 'physical_conditions' in self.vars:
            used_vars = 'PHYSICAL'
            confidence = 0.4
        elif 'additional_conditions' in self.vars:
            used_vars = 'ADDITIONALS'
            confidence = 0.1

        return (used_vars, confidence)

    def get_label(self):
        if np.isnan(self.eutrophication_level):
            raise ValueError("No se ha calculado la inferencia del nivel de eutrofización.")

        # Determinar la label con mayor degree de pertenencia
        membership_degrees = {}
        for label in self.eutrophication_level_var.terms:
            membership_function = self.eutrophication_level_var[label].mf
            degree = fuzz.interp_membership(self.eutrophication_level_var.universe, membership_function, self.eutrophication_level)
            membership_degrees[label] = degree

        predicted_label = max(membership_degrees, key=membership_degrees.get)
        return predicted_label
