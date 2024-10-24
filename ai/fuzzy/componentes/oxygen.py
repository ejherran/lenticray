import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class OxygenBalance:
    def __init__(self, custom_vars=dict(), **kwargs):
        self.custom_vars = custom_vars
        self.inputs = kwargs
        self.available_vars = {k: v for k, v in self.inputs.items() if not np.isnan(v)}
        self.oxygen_balance = np.nan

        # Orden de prioridad de las vars
        self.priority_vars = [
            'O2_Dis', 'BOD', 'COD', 'PV'
        ]

        self.available_vars = {k: v for k, v in self.available_vars.items() if k in self.priority_vars}

        if not self.available_vars:
            raise ValueError(f"No se encontraron vars válidas para inferencia.")

        self._init_vars()
        self._create_fuzzy_system()

    def _init_vars(self):
        self.base_vars = dict(
            O2_Dis=dict(
                universe = np.arange(0, 15.1, 0.1),  # Rango típico de 0 a 15 mg/L
                mf_definitions = {
                    'LOW': {'type': 'trapmf', 'params': [0, 0, 2, 5]},
                    'MODERATE': {'type': 'trimf', 'params': [4, 6, 8]},
                    'HIGH': {'type': 'trimf', 'params': [7, 9, 11]},
                    'VERY HIGH': {'type': 'trapmf', 'params': [10, 12, 15, 15]}
                }
            ),
            BOD=dict(
                universe = np.arange(0, 30.1, 0.1),  # Rango típico de 0 a 30 mg/L
                mf_definitions = {
                    'LOW': {'type': 'trapmf', 'params': [0, 0, 2, 5]},
                    'MODERATE': {'type': 'trimf', 'params': [4, 7, 10]},
                    'HIGH': {'type': 'trimf', 'params': [9, 15, 20]},
                    'VERY HIGH': {'type': 'trapmf', 'params': [18, 25, 30, 30]}
                }
            ),
            COD=dict(
                universe = np.arange(0, 100.1, 0.1),  # Rango típico de 0 a 100 mg/L
                mf_definitions = {
                    'LOW': {'type': 'trapmf', 'params': [0, 0, 5, 15]},
                    'MODERATE': {'type': 'trimf', 'params': [10, 25, 40]},
                    'HIGH': {'type': 'trimf', 'params': [35, 55, 75]},
                    'VERY HIGH': {'type': 'trapmf', 'params': [70, 85, 100, 100]}
                }
            ),
            PV=dict(
                universe = np.arange(0, 50.1, 0.1),  # Rango típico de 0 a 50 mg/L
                mf_definitions = {
                    'LOW': {'type': 'trapmf', 'params': [0, 0, 2, 8]},
                    'MODERATE': {'type': 'trimf', 'params': [6, 12, 20]},
                    'HIGH': {'type': 'trimf', 'params': [18, 25, 35]},
                    'VERY HIGH': {'type': 'trapmf', 'params': [30, 40, 50, 50]}
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
        if 'O2_Dis' in self.available_vars:
            self.calculation_method = 'O2_Dis'
            # Definir variable difusa para O2_Dis
            universe, mf_definitions = self._get_variable_definitions('O2_Dis')
            antecedent = ctrl.Antecedent(universe, 'O2_Dis')
            for label, params in mf_definitions.items():
                if params['type'] == 'trapmf':
                    antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
            self.vars['O2_Dis'] = antecedent

        elif 'BOD' in self.available_vars and 'COD' in self.available_vars:
            self.calculation_method = 'BOD_COD'
            # Definir vars difusas para BOD y COD
            universe_bod, mf_definitions_bod = self._get_variable_definitions('BOD')
            antecedent_bod = ctrl.Antecedent(universe_bod, 'BOD')
            for label, params in mf_definitions_bod.items():
                if params['type'] == 'trapmf':
                    antecedent_bod[label] = fuzz.trapmf(antecedent_bod.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent_bod[label] = fuzz.trimf(antecedent_bod.universe, params['params'])
            self.vars['BOD'] = antecedent_bod

            universe_cod, mf_definitions_cod = self._get_variable_definitions('COD')
            antecedent_cod = ctrl.Antecedent(universe_cod, 'COD')
            for label, params in mf_definitions_cod.items():
                if params['type'] == 'trapmf':
                    antecedent_cod[label] = fuzz.trapmf(antecedent_cod.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent_cod[label] = fuzz.trimf(antecedent_cod.universe, params['params'])
            self.vars['COD'] = antecedent_cod

        elif 'BOD' in self.available_vars and 'PV' in self.available_vars:
            self.calculation_method = 'BOD_PV'
            # Definir vars difusas para BOD y PV
            universe_bod, mf_definitions_bod = self._get_variable_definitions('BOD')
            antecedent_bod = ctrl.Antecedent(universe_bod, 'BOD')
            for label, params in mf_definitions_bod.items():
                if params['type'] == 'trapmf':
                    antecedent_bod[label] = fuzz.trapmf(antecedent_bod.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent_bod[label] = fuzz.trimf(antecedent_bod.universe, params['params'])
            self.vars['BOD'] = antecedent_bod

            universe_pv, mf_definitions_pv = self._get_variable_definitions('PV')
            antecedent_pv = ctrl.Antecedent(universe_pv, 'PV')
            for label, params in mf_definitions_pv.items():
                if params['type'] == 'trapmf':
                    antecedent_pv[label] = fuzz.trapmf(antecedent_pv.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent_pv[label] = fuzz.trimf(antecedent_pv.universe, params['params'])
            self.vars['PV'] = antecedent_pv

        else:
            # Usar vars individuales en orden de prioridad
            for var in self.priority_vars:
                if var in self.available_vars:
                    self.calculation_method = var
                    universe, mf_definitions = self._get_variable_definitions(var)
                    antecedent = ctrl.Antecedent(universe, var)
                    for label, params in mf_definitions.items():
                        if params['type'] == 'trapmf':
                            antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                        elif params['type'] == 'trimf':
                            antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
                    self.vars[var] = antecedent
                    break
            else:
                # Si no hay vars disponibles, error
                raise ValueError("No hay vars válidas disponibles para crear el sistema difuso.")

        # Definir variable de salida
        self.oxygen_balance_universe = np.arange(0, 1.01, 0.01)
        self.oxygen_balance_var = ctrl.Consequent(self.oxygen_balance_universe, 'oxygen_balance')
        self.oxygen_balance_var['GOOD'] = fuzz.trapmf(self.oxygen_balance_var.universe, [0, 0, 0.2, 0.4])
        self.oxygen_balance_var['MODERATE'] = fuzz.trimf(self.oxygen_balance_var.universe, [0.3, 0.5, 0.7])
        self.oxygen_balance_var['BAD'] = fuzz.trimf(self.oxygen_balance_var.universe, [0.6, 0.75, 0.9])
        self.oxygen_balance_var['VERY BAD'] = fuzz.trapmf(self.oxygen_balance_var.universe, [0.85, 0.95, 1, 1])

        # Definir reglas difusas basadas en la variable seleccionada
        if self.calculation_method == 'O2_Dis':
            # Reglas basadas en O2_Dis (a mayor oxígeno disuelto, mejor balance)
            antecedent = self.vars['O2_Dis']
            self.rules.append(ctrl.Rule(antecedent['LOW'], self.oxygen_balance_var['VERY BAD']))
            self.rules.append(ctrl.Rule(antecedent['MODERATE'], self.oxygen_balance_var['BAD']))
            self.rules.append(ctrl.Rule(antecedent['HIGH'], self.oxygen_balance_var['MODERATE']))
            self.rules.append(ctrl.Rule(antecedent['VERY HIGH'], self.oxygen_balance_var['GOOD']))
        elif self.calculation_method == 'BOD_COD':
            # Reglas combinadas basadas en BOD y COD
            antecedent_bod = self.vars['BOD']
            antecedent_cod = self.vars['COD']
            self.rules.append(ctrl.Rule(antecedent_bod['LOW'] & antecedent_cod['LOW'], self.oxygen_balance_var['GOOD']))
            self.rules.append(ctrl.Rule(antecedent_bod['MODERATE'] | antecedent_cod['MODERATE'], self.oxygen_balance_var['MODERATE']))
            self.rules.append(ctrl.Rule(antecedent_bod['HIGH'] | antecedent_cod['HIGH'], self.oxygen_balance_var['BAD']))
            self.rules.append(ctrl.Rule(antecedent_bod['VERY HIGH'] | antecedent_cod['VERY HIGH'], self.oxygen_balance_var['VERY BAD']))
        elif self.calculation_method == 'BOD_PV':
            # Reglas combinadas basadas en BOD y PV
            antecedent_bod = self.vars['BOD']
            antecedent_pv = self.vars['PV']
            self.rules.append(ctrl.Rule(antecedent_bod['LOW'] & antecedent_pv['LOW'], self.oxygen_balance_var['GOOD']))
            self.rules.append(ctrl.Rule(antecedent_bod['MODERATE'] | antecedent_pv['MODERATE'], self.oxygen_balance_var['MODERATE']))
            self.rules.append(ctrl.Rule(antecedent_bod['HIGH'] | antecedent_pv['HIGH'], self.oxygen_balance_var['BAD']))
            self.rules.append(ctrl.Rule(antecedent_bod['VERY HIGH'] | antecedent_pv['VERY HIGH'], self.oxygen_balance_var['VERY BAD']))
        else:
            # Reglas basadas en la variable individual seleccionada
            var_name = self.calculation_method
            antecedent = self.vars[var_name]
            # Para BOD, COD y PV, mayor value implica peor balance
            self.rules.append(ctrl.Rule(antecedent['LOW'], self.oxygen_balance_var['GOOD']))
            self.rules.append(ctrl.Rule(antecedent['MODERATE'], self.oxygen_balance_var['MODERATE']))
            self.rules.append(ctrl.Rule(antecedent['HIGH'], self.oxygen_balance_var['BAD']))
            self.rules.append(ctrl.Rule(antecedent['VERY HIGH'], self.oxygen_balance_var['VERY BAD']))

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def calculate_inference(self):
        if not hasattr(self, 'simulation'):
            raise ValueError("No ha sido posible crear el sistema de control.")

        try:
            if self.calculation_method == 'O2_Dis':
                o2_value = self.available_vars['O2_Dis']
                self.simulation.input['O2_Dis'] = o2_value

            elif self.calculation_method == 'BOD_COD':
                bod_value = self.available_vars['BOD']
                cod_value = self.available_vars['COD']
                self.simulation.input['BOD'] = bod_value
                self.simulation.input['COD'] = cod_value

            elif self.calculation_method == 'BOD_PV':
                bod_value = self.available_vars['BOD']
                pv_value = self.available_vars['PV']
                self.simulation.input['BOD'] = bod_value
                self.simulation.input['PV'] = pv_value

            else:
                var_name = self.calculation_method
                var_value = self.available_vars[var_name]
                self.simulation.input[var_name] = var_value

            # Realizar la computación
            self.simulation.compute()
            self.oxygen_balance = self.simulation.output['oxygen_balance']

        except Exception as e:
            raise ValueError(f"Error al calcular la inferencia: {e}")

        return self.calculation_method

    def get_label(self):
        if np.isnan(self.oxygen_balance):
            raise ValueError("El balance de oxígeno no está disponible.")

        # Crear un diccionario para almacenar los degrees de pertenencia
        membership_degrees = {}

        # Para cada label en la variable de salida
        for label in self.oxygen_balance_var.terms:
            # Obtener la función de pertenencia correspondiente
            membership_function = self.oxygen_balance_var[label].mf
            # Calcular el degree de pertenencia del value de salida en esta función
            degree = fuzz.interp_membership(self.oxygen_balance_var.universe, membership_function, self.oxygen_balance)
            # Almacenar el degree en el diccionario
            membership_degrees[label] = degree

        # Encontrar la label con el mayor degree de pertenencia
        predicted_label = max(membership_degrees, key=membership_degrees.get)

        return predicted_label
