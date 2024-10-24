import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class PhosphorusLevel:
    def __init__(self, custom_vars=dict(), **kwargs):
        self.custom_vars = custom_vars
        self.inputs = kwargs
        self.available_vars = {k: v for k, v in self.inputs.items() if not np.isnan(v)}
        self.phosphorus_level = np.nan

        # Orden de prioridad de las vars
        self.priority_vars = [
            'TP', 'TDP', 'TIP', 'DIP', 'TRP', 'DRP', 'TPP'
        ]

        self.available_vars = {k: v for k, v in self.available_vars.items() if k in self.priority_vars}

        if not self.available_vars:
            raise ValueError(f"No se encontraron vars válidas para inferencia.")

        self._init_vars()
        self._create_fuzzy_system()

    def _init_vars(self):
        self.base_vars = dict(
            TP=dict(
                universe = np.arange(0, 0.1, 0.001),  # Rango de 0 a 1 mg/L
                mf_definitions = {
                    'LOW': {'type': 'trapmf', 'params': [0, 0, 0.010, 0.015]},
                    'MODERATE': {'type': 'trimf', 'params': [0.012, 0.018, 0.024]},
                    'HIGH': {'type': 'trimf', 'params': [0.024, 0.06, 0.096]},
                    'VERY HIGH': {'type': 'trapmf', 'params': [0.090, 0.096, 0.1, 0.1]}
                }
            ),
            TDP=dict(
                universe = np.arange(0, 0.51, 0.01),  # Rango de 0 a 0.5 mg/L
                mf_definitions = {
                    'LOW': {'type': 'trapmf', 'params': [0, 0, 0.01, 0.03]},
                    'MODERATE': {'type': 'trimf', 'params': [0.02, 0.05, 0.1]},
                    'HIGH': {'type': 'trimf', 'params': [0.08, 0.15, 0.25]},
                    'VERY HIGH': {'type': 'trapmf', 'params': [0.2, 0.35, 0.5, 0.5]}
                }
            ),
            TIP=dict(
                universe = np.arange(0, 0.51, 0.01),
                mf_definitions = {
                    'LOW': {'type': 'trapmf', 'params': [0, 0, 0.015, 0.035]},
                    'MODERATE': {'type': 'trimf', 'params': [0.025, 0.06, 0.1]},
                    'HIGH': {'type': 'trimf', 'params': [0.08, 0.15, 0.25]},
                    'VERY HIGH': {'type': 'trapmf', 'params': [0.2, 0.35, 0.5, 0.5]}
                }
            ),
            DIP=dict(
                universe = np.arange(0, 0.26, 0.01),  # Rango de 0 a 0.25 mg/L
                mf_definitions = {
                    'LOW': {'type': 'trapmf', 'params': [0, 0, 0.005, 0.015]},
                    'MODERATE': {'type': 'trimf', 'params': [0.01, 0.03, 0.06]},
                    'HIGH': {'type': 'trimf', 'params': [0.05, 0.1, 0.15]},
                    'VERY HIGH': {'type': 'trapmf', 'params': [0.12, 0.18, 0.25, 0.25]}
                }
            ),
            TRP=dict(
                universe = np.arange(0, 0.51, 0.01),
                mf_definitions = {
                    'LOW': {'type': 'trapmf', 'params': [0, 0, 0.01, 0.03]},
                    'MODERATE': {'type': 'trimf', 'params': [0.02, 0.05, 0.1]},
                    'HIGH': {'type': 'trimf', 'params': [0.08, 0.15, 0.25]},
                    'VERY HIGH': {'type': 'trapmf', 'params': [0.2, 0.35, 0.5, 0.5]}
                }
            ),
            DRP=dict(
                universe = np.arange(0, 0.26, 0.01),
                mf_definitions = {
                    'LOW': {'type': 'trapmf', 'params': [0, 0, 0.005, 0.015]},
                    'MODERATE': {'type': 'trimf', 'params': [0.01, 0.03, 0.06]},
                    'HIGH': {'type': 'trimf', 'params': [0.05, 0.1, 0.15]},
                    'VERY HIGH': {'type': 'trapmf', 'params': [0.12, 0.18, 0.25, 0.25]}
                }
            ),
            TPP=dict(
                universe = np.arange(0, 0.51, 0.01),
                mf_definitions = {
                    'LOW': {'type': 'trapmf', 'params': [0, 0, 0.005, 0.02]},
                    'MODERATE': {'type': 'trimf', 'params': [0.015, 0.04, 0.08]},
                    'HIGH': {'type': 'trimf', 'params': [0.06, 0.12, 0.2]},
                    'VERY HIGH': {'type': 'trapmf', 'params': [0.15, 0.25, 0.5, 0.5]}
                }
            )
        )

        for var_name, var_content in self.custom_vars.items():
            self.base_vars[var_name] = var_content

    def _get_variable_definitions(self, var_name):
        var_content = self.base_vars.get(var_name, None)

        if var_content:
            universe = var_content['universe']
            mf_definitions = var_content['mf_definitions']
        else:
            raise ValueError(f"Variable desconocida: {var_name}")

        return universe, mf_definitions

    def _create_fuzzy_system(self):
        # Inicializar estructuras
        self.rules = []
        self.vars = {}
        self.mf_definitions = {}
        self.calculation_method = None  # Método utilizado para el cálculo

        # Verificar la disponibilidad de vars en orden de prioridad
        if 'TP' in self.available_vars:
            self.calculation_method = 'TP'
            # Definir variable difusa para TP
            universe, mf_definitions = self._get_variable_definitions('TP')
            antecedent = ctrl.Antecedent(universe, 'TP')
            for label, params in mf_definitions.items():
                if params['type'] == 'trapmf':
                    antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
            self.vars['TP'] = antecedent

        elif 'TDP' in self.available_vars and 'TPP' in self.available_vars:
            self.calculation_method = 'TDP_TPP'
            # Definir variable difusa para TP (calculado)
            universe, mf_definitions = self._get_variable_definitions('TP')
            antecedent = ctrl.Antecedent(universe, 'TP')
            for label, params in mf_definitions.items():
                if params['type'] == 'trapmf':
                    antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
            self.vars['TP'] = antecedent

        elif 'TIP' in self.available_vars and 'TRP' in self.available_vars:
            self.calculation_method = 'TIP_TRP'
            # Definir variable difusa para TP (calculado)
            universe, mf_definitions = self._get_variable_definitions('TP')
            antecedent = ctrl.Antecedent(universe, 'TP')
            for label, params in mf_definitions.items():
                if params['type'] == 'trapmf':
                    antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
            self.vars['TP'] = antecedent

        else:
            # Usar vars individuales en orden de prioridad
            for var_name in self.priority_vars:
                if var_name in self.available_vars:
                    self.calculation_method = var_name
                    universe, mf_definitions = self._get_variable_definitions(var_name)
                    antecedent = ctrl.Antecedent(universe, var_name)
                    for label, params in mf_definitions.items():
                        if params['type'] == 'trapmf':
                            antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                        elif params['type'] == 'trimf':
                            antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
                    self.vars[var_name] = antecedent
                    break
            else:
                # Si no hay vars disponibles, error
                raise ValueError("No hay vars válidas disponibles para crear el sistema difuso.")

        # Definir variable de salida
        self.phosphorus_level_universe = np.arange(0, 1.01, 0.01)
        self.phosphorus_level_var = ctrl.Consequent(self.phosphorus_level_universe, 'phosphorus_level')
        self.phosphorus_level_var['LOW'] = fuzz.trapmf(self.phosphorus_level_var.universe, [0, 0, 0.15, 0.3])
        self.phosphorus_level_var['MODERATE'] = fuzz.trimf(self.phosphorus_level_var.universe, [0.25, 0.4, 0.55])
        self.phosphorus_level_var['HIGH'] = fuzz.trimf(self.phosphorus_level_var.universe, [0.5, 0.65, 0.8])
        self.phosphorus_level_var['VERY HIGH'] = fuzz.trapmf(self.phosphorus_level_var.universe, [0.75, 0.85, 1, 1])

        # Definir reglas difusas basadas en la variable seleccionada
        if self.calculation_method in ['TP', 'TDP_TPP', 'TIP_TRP']:
            # Reglas basadas en TP
            self.rules.append(ctrl.Rule(self.vars['TP']['LOW'], self.phosphorus_level_var['LOW']))
            self.rules.append(ctrl.Rule(self.vars['TP']['MODERATE'], self.phosphorus_level_var['MODERATE']))
            self.rules.append(ctrl.Rule(self.vars['TP']['HIGH'], self.phosphorus_level_var['HIGH']))
            self.rules.append(ctrl.Rule(self.vars['TP']['VERY HIGH'], self.phosphorus_level_var['VERY HIGH']))
        else:
            # Reglas basadas en vars individuales
            var_name = self.calculation_method
            antecedent = self.vars[var_name]
            self.rules.append(ctrl.Rule(antecedent['LOW'], self.phosphorus_level_var['LOW']))
            self.rules.append(ctrl.Rule(antecedent['MODERATE'], self.phosphorus_level_var['MODERATE']))
            self.rules.append(ctrl.Rule(antecedent['HIGH'], self.phosphorus_level_var['HIGH']))
            self.rules.append(ctrl.Rule(antecedent['VERY HIGH'], self.phosphorus_level_var['VERY HIGH']))

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def calculate_inference(self):
        if not hasattr(self, 'simulation'):
            raise ValueError("No ha sido posible crear el sistema de control.")

        try:
            if self.calculation_method == 'TP':
                tp_value = self.available_vars['TP']
                self.simulation.input['TP'] = tp_value

            elif self.calculation_method == 'TDP_TPP':
                tdp_value = self.available_vars['TDP']
                tpp_value = self.available_vars['TPP']
                tp_value = tdp_value + tpp_value
                self.simulation.input['TP'] = tp_value

            elif self.calculation_method == 'TIP_TRP':
                tip_value = self.available_vars['TIP']
                trp_value = self.available_vars['TRP']
                tp_value = tip_value + trp_value
                self.simulation.input['TP'] = tp_value

            else:
                var_name = self.calculation_method
                var_value = self.available_vars[var_name]
                self.simulation.input[var_name] = var_value

            # Realizar la computación
            self.simulation.compute()
            self.phosphorus_level = self.simulation.output['phosphorus_level']

        except Exception as e:
            raise ValueError(f"Error al calcular la inferencia: {e}")

        return self.calculation_method

    def get_label(self):
        if np.isnan(self.phosphorus_level):
            raise ValueError("El nivel de nitrógeno no está disponible.")

        # Crear un diccionario para almacenar los degrees de pertenencia
        membership_degrees = {}

        # Para cada label en la variable de salida
        for label in self.phosphorus_level_var.terms:
            # Obtener la función de pertenencia correspondiente
            membership_function = self.phosphorus_level_var[label].mf
            # Calcular el degree de pertenencia del value de salida en esta función
            degree = fuzz.interp_membership(self.phosphorus_level_var.universe, membership_function, self.phosphorus_level)
            # Almacenar el degree en el diccionario
            membership_degrees[label] = degree

        # Encontrar la label con el mayor degree de pertenencia
        predicted_label = max(membership_degrees, key=membership_degrees.get)

        return predicted_label
