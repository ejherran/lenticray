import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class VisibilityLevel:
    def __init__(self, custom_vars=dict(), **kwargs):
        self.custom_vars = custom_vars
        self.inputs = kwargs
        self.available_vars = {k: v for k, v in self.inputs.items() if not np.isnan(v)}
        self.visibility_level = np.nan

        # Orden de prioridad de las vars
        self.priority_vars = ['TRANS', 'TURB']

        self.available_vars = {k: v for k, v in self.available_vars.items() if k in self.priority_vars}

        if not self.available_vars:
            raise ValueError("No se encontraron vars válidas para inferencia.")

        self._init_vars()
        self._create_fuzzy_system()

    def _init_vars(self):
        self.base_vars = dict(
            TRANS=dict(
                # Definición para Transparencia
                universe = np.arange(0, 10.1, 0.1),  # Profundidad en metros
                mf_definitions = {
                    'LOW': {'type': 'trapmf', 'params': [0, 0, 0.25, 0.6]},
                    'MODERATE': {'type': 'trimf', 'params': [0.5, 1.25, 2.1]},
                    'HIGH': {'type': 'trimf', 'params': [2, 3, 4.1]},
                    'VERY HIGH': {'type': 'trapmf', 'params': [4, 5, 10, 10]}
                }
            ),
            TURB=dict(
                # Definición para Turbidez
                universe = np.arange(0, 100.1, 0.1),  # Unidades de turbidez (NTU)
                mf_definitions = {
                    'LOW': {'type': 'trapmf', 'params': [0, 0, 5, 15]},
                    'MODERATE': {'type': 'trimf', 'params': [10, 30, 50]},
                    'HIGH': {'type': 'trimf', 'params': [40, 60, 80]},
                    'VERY HIGH': {'type': 'trapmf', 'params': [70, 90, 100, 100]}
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
        """
        Crea el sistema difuso basado en las vars disponibles y sus prioridades.
        Define las reglas y configura el sistema de control.
        """
        # Inicializar estructuras
        self.rules = []
        self.vars_fuzzy = {}
        self.calculation_method = None  # Método utilizado para el cálculo

        # Prioridad de las vars
        for var in self.priority_vars:
            if var in self.available_vars:
                self.calculation_method = var
                # Definir variable difusa para la variable seleccionada
                universe, mf_definitions = self._get_variable_definitions(var)
                antecedent = ctrl.Antecedent(universe, var)
                for label, params in mf_definitions.items():
                    if params['type'] == 'trapmf':
                        antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                    elif params['type'] == 'trimf':
                        antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
                self.vars_fuzzy[var] = antecedent
                break  # Solo usar la primera variable disponible según prioridad

        # Si ninguna variable de alta prioridad está disponible, usar combinaciones si es posible
        if not self.vars_fuzzy:
            # Ejemplo: Combinar TRANS y TURB para inferir visibility_level
            if all(var in self.available_vars for var in ['TRANS', 'TURB']):
                self.calculation_method = 'TRANS_TURB'
                # Definir vars difusas para TRANS y TURB
                universe_trans, mf_definitions_trans = self._get_variable_definitions('TRANS')
                antecedent_trans = ctrl.Antecedent(universe_trans, 'TRANS')
                for label, params in mf_definitions_trans.items():
                    if params['type'] == 'trapmf':
                        antecedent_trans[label] = fuzz.trapmf(antecedent_trans.universe, params['params'])
                    elif params['type'] == 'trimf':
                        antecedent_trans[label] = fuzz.trimf(antecedent_trans.universe, params['params'])
                self.vars_fuzzy['TRANS'] = antecedent_trans

                universe_turb, mf_definitions_turb = self._get_variable_definitions('TURB')
                antecedent_turb = ctrl.Antecedent(universe_turb, 'TURB')
                for label, params in mf_definitions_turb.items():
                    if params['type'] == 'trapmf':
                        antecedent_turb[label] = fuzz.trapmf(antecedent_turb.universe, params['params'])
                    elif params['type'] == 'trimf':
                        antecedent_turb[label] = fuzz.trimf(antecedent_turb.universe, params['params'])
                self.vars_fuzzy['TURB'] = antecedent_turb
            else:
                raise ValueError("No hay suficientes vars disponibles para crear el sistema difuso.")

        # Definir variable de salida
        self.visibility_level_universe = np.arange(0, 1.01, 0.01)
        self.visibility_level_var = ctrl.Consequent(self.visibility_level_universe, 'visibility_level')
        self.visibility_level_var['LOW'] = fuzz.trapmf(self.visibility_level_var.universe, [0, 0, 0.2, 0.4])
        self.visibility_level_var['MODERATE'] = fuzz.trimf(self.visibility_level_var.universe, [0.3, 0.5, 0.7])
        self.visibility_level_var['HIGH'] = fuzz.trimf(self.visibility_level_var.universe, [0.6, 0.8, 0.95])
        self.visibility_level_var['VERY HIGH'] = fuzz.trapmf(self.visibility_level_var.universe, [0.9, 0.95, 1, 1])

        # Definir reglas difusas basadas en la variable seleccionada
        if self.calculation_method in ['TRANS', 'TURB']:
            var = self.calculation_method
            antecedent = self.vars_fuzzy[var]
            if var == 'TRANS':
                # Reglas basadas en TRANS
                self.rules.append(ctrl.Rule(antecedent['LOW'], self.visibility_level_var['LOW']))
                self.rules.append(ctrl.Rule(antecedent['MODERATE'], self.visibility_level_var['MODERATE']))
                self.rules.append(ctrl.Rule(antecedent['HIGH'], self.visibility_level_var['HIGH']))
                self.rules.append(ctrl.Rule(antecedent['VERY HIGH'], self.visibility_level_var['VERY HIGH']))
            elif var == 'TURB':
                # Reglas basadas en TURB
                self.rules.append(ctrl.Rule(antecedent['LOW'], self.visibility_level_var['VERY HIGH']))
                self.rules.append(ctrl.Rule(antecedent['MODERATE'], self.visibility_level_var['HIGH']))
                self.rules.append(ctrl.Rule(antecedent['HIGH'], self.visibility_level_var['MODERATE']))
                self.rules.append(ctrl.Rule(antecedent['VERY HIGH'], self.visibility_level_var['LOW']))
        elif self.calculation_method == 'TRANS_TURB':
            # Reglas combinadas basadas en TRANS y TURB
            antecedent_trans = self.vars_fuzzy['TRANS']
            antecedent_turb = self.vars_fuzzy['TURB']

            # Reglas:
            # Si TRANS es VERY HIGH y TURB es LOW => VERY HIGH
            self.rules.append(ctrl.Rule(antecedent_trans['VERY HIGH'] & antecedent_turb['LOW'], self.visibility_level_var['VERY HIGH']))

            # Si TRANS es HIGH y TURB es LOW => HIGH
            self.rules.append(ctrl.Rule(antecedent_trans['HIGH'] & antecedent_turb['LOW'], self.visibility_level_var['HIGH']))

            # Si TRANS es MODERATE o TURB es MODERATE => MODERATE
            self.rules.append(ctrl.Rule(antecedent_trans['MODERATE'] | antecedent_turb['MODERATE'], self.visibility_level_var['MODERATE']))

            # Si TRANS es LOW o TURB es HIGH o VERY HIGH => LOW
            self.rules.append(ctrl.Rule(antecedent_trans['LOW'] | antecedent_turb['HIGH'] | antecedent_turb['VERY HIGH'], self.visibility_level_var['LOW']))
        else:
            raise ValueError("Método de cálculo no reconocido.")

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def calculate_inference(self):
        """
        Calcula la inferencia difusa para determinar el nivel de visibility_level.

        Retorna:
            calculation_method (str): Método utilizado para el cálculo.
        """
        if not hasattr(self, 'simulation'):
            raise ValueError("No ha sido posible crear el sistema de control.")

        try:
            if self.calculation_method == 'TRANS':
                trans_value = self.available_vars['TRANS']
                self.simulation.input['TRANS'] = trans_value

            elif self.calculation_method == 'TURB':
                turb_value = self.available_vars['TURB']
                self.simulation.input['TURB'] = turb_value

            elif self.calculation_method == 'TRANS_TURB':
                trans_value = self.available_vars['TRANS']
                turb_value = self.available_vars['TURB']
                self.simulation.input['TRANS'] = trans_value
                self.simulation.input['TURB'] = turb_value

            # Realizar la computación
            self.simulation.compute()
            self.visibility_level = self.simulation.output['visibility_level']

        except Exception as e:
            raise ValueError(f"Error al calcular la inferencia: {e}")

        return self.calculation_method

    def get_label(self):
        """
        Obtiene la label correspondiente al nivel de visibility_level inferido.

        Retorna:
            predicted_label (str): Etiqueta del nivel de visibility_level.
        """
        if np.isnan(self.visibility_level):
            raise ValueError("El nivel de visibility_level no está disponible.")

        # Crear un diccionario para almacenar los degrees de pertenencia
        membership_degrees = {}

        # Para cada label en la variable de salida
        for label in self.visibility_level_var.terms:
            # Obtener la función de pertenencia correspondiente
            membership_function = self.visibility_level_var[label].mf
            # Calcular el degree de pertenencia del value de salida en esta función
            degree = fuzz.interp_membership(self.visibility_level_var.universe, membership_function, self.visibility_level)
            # Almacenar el degree en el diccionario
            membership_degrees[label] = degree

        # Encontrar la label con el mayor degree de pertenencia
        predicted_label = max(membership_degrees, key=membership_degrees.get)

        return predicted_label
