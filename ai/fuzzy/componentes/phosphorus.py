import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class NivelFosforo:
    def __init__(self, custom_vars=dict(), **kwargs):
        self.custom_vars = custom_vars
        self.inputs = kwargs
        self.available_vars = {k: v for k, v in self.inputs.items() if not np.isnan(v)}
        self.nivel_fosforo = np.nan

        # Orden de prioridad de las variables
        self.priority_variables = [
            'TP', 'TDP', 'TIP', 'DIP', 'TRP', 'DRP', 'TPP'
        ]

        self.available_vars = {k: v for k, v in self.available_vars.items() if k in self.priority_variables}

        if not self.available_vars:
            raise ValueError(f"No se encontraron variables válidas para inferencia.")

        self._init_variables()
        self._crear_sistema_difuso()

    def _init_variables(self):
        self.base_vars = dict(
            TP=dict(
                universe = np.arange(0, 0.1, 0.001),  # Rango de 0 a 1 mg/L
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.010, 0.015]},
                    'MODERADO': {'type': 'trimf', 'params': [0.012, 0.018, 0.024]},
                    'ALTO': {'type': 'trimf', 'params': [0.024, 0.06, 0.096]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [0.090, 0.096, 0.1, 0.1]}
                }
            ),
            TDP=dict(
                universe = np.arange(0, 0.51, 0.01),  # Rango de 0 a 0.5 mg/L
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.01, 0.03]},
                    'MODERADO': {'type': 'trimf', 'params': [0.02, 0.05, 0.1]},
                    'ALTO': {'type': 'trimf', 'params': [0.08, 0.15, 0.25]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [0.2, 0.35, 0.5, 0.5]}
                }
            ),
            TIP=dict(
                universe = np.arange(0, 0.51, 0.01),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.015, 0.035]},
                    'MODERADO': {'type': 'trimf', 'params': [0.025, 0.06, 0.1]},
                    'ALTO': {'type': 'trimf', 'params': [0.08, 0.15, 0.25]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [0.2, 0.35, 0.5, 0.5]}
                }
            ),
            DIP=dict(
                universe = np.arange(0, 0.26, 0.01),  # Rango de 0 a 0.25 mg/L
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.005, 0.015]},
                    'MODERADO': {'type': 'trimf', 'params': [0.01, 0.03, 0.06]},
                    'ALTO': {'type': 'trimf', 'params': [0.05, 0.1, 0.15]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [0.12, 0.18, 0.25, 0.25]}
                }
            ),
            TRP=dict(
                universe = np.arange(0, 0.51, 0.01),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.01, 0.03]},
                    'MODERADO': {'type': 'trimf', 'params': [0.02, 0.05, 0.1]},
                    'ALTO': {'type': 'trimf', 'params': [0.08, 0.15, 0.25]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [0.2, 0.35, 0.5, 0.5]}
                }
            ),
            DRP=dict(
                universe = np.arange(0, 0.26, 0.01),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.005, 0.015]},
                    'MODERADO': {'type': 'trimf', 'params': [0.01, 0.03, 0.06]},
                    'ALTO': {'type': 'trimf', 'params': [0.05, 0.1, 0.15]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [0.12, 0.18, 0.25, 0.25]}
                }
            ),
            TPP=dict(
                universe = np.arange(0, 0.51, 0.01),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.005, 0.02]},
                    'MODERADO': {'type': 'trimf', 'params': [0.015, 0.04, 0.08]},
                    'ALTO': {'type': 'trimf', 'params': [0.06, 0.12, 0.2]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [0.15, 0.25, 0.5, 0.5]}
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

    def _crear_sistema_difuso(self):
        # Inicializar estructuras
        self.rules = []
        self.variables = {}
        self.mf_definitions = {}
        self.calculation_method = None  # Método utilizado para el cálculo

        # Verificar la disponibilidad de variables en orden de prioridad
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
            self.variables['TP'] = antecedent

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
            self.variables['TP'] = antecedent

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
            self.variables['TP'] = antecedent

        else:
            # Usar variables individuales en orden de prioridad
            for var_name in self.priority_variables:
                if var_name in self.available_vars:
                    self.calculation_method = var_name
                    universe, mf_definitions = self._get_variable_definitions(var_name)
                    antecedent = ctrl.Antecedent(universe, var_name)
                    for label, params in mf_definitions.items():
                        if params['type'] == 'trapmf':
                            antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                        elif params['type'] == 'trimf':
                            antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
                    self.variables[var_name] = antecedent
                    break
            else:
                # Si no hay variables disponibles, error
                raise ValueError("No hay variables válidas disponibles para crear el sistema difuso.")

        # Definir variable de salida
        self.nivel_fosforo_universe = np.arange(0, 1.01, 0.01)
        self.nivel_fosforo_var = ctrl.Consequent(self.nivel_fosforo_universe, 'nivel_fosforo')
        self.nivel_fosforo_var['BAJO'] = fuzz.trapmf(self.nivel_fosforo_var.universe, [0, 0, 0.15, 0.3])
        self.nivel_fosforo_var['MODERADO'] = fuzz.trimf(self.nivel_fosforo_var.universe, [0.25, 0.4, 0.55])
        self.nivel_fosforo_var['ALTO'] = fuzz.trimf(self.nivel_fosforo_var.universe, [0.5, 0.65, 0.8])
        self.nivel_fosforo_var['MUY ALTO'] = fuzz.trapmf(self.nivel_fosforo_var.universe, [0.75, 0.85, 1, 1])

        # Definir reglas difusas basadas en la variable seleccionada
        if self.calculation_method in ['TP', 'TDP_TPP', 'TIP_TRP']:
            # Reglas basadas en TP
            self.rules.append(ctrl.Rule(self.variables['TP']['BAJO'], self.nivel_fosforo_var['BAJO']))
            self.rules.append(ctrl.Rule(self.variables['TP']['MODERADO'], self.nivel_fosforo_var['MODERADO']))
            self.rules.append(ctrl.Rule(self.variables['TP']['ALTO'], self.nivel_fosforo_var['ALTO']))
            self.rules.append(ctrl.Rule(self.variables['TP']['MUY ALTO'], self.nivel_fosforo_var['MUY ALTO']))
        else:
            # Reglas basadas en variables individuales
            var_name = self.calculation_method
            antecedent = self.variables[var_name]
            self.rules.append(ctrl.Rule(antecedent['BAJO'], self.nivel_fosforo_var['BAJO']))
            self.rules.append(ctrl.Rule(antecedent['MODERADO'], self.nivel_fosforo_var['MODERADO']))
            self.rules.append(ctrl.Rule(antecedent['ALTO'], self.nivel_fosforo_var['ALTO']))
            self.rules.append(ctrl.Rule(antecedent['MUY ALTO'], self.nivel_fosforo_var['MUY ALTO']))

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def calcular_inferencia(self):
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
            self.nivel_fosforo = self.simulation.output['nivel_fosforo']

        except Exception as e:
            raise ValueError(f"Error al calcular la inferencia: {e}")

        return self.calculation_method

    def obtener_etiqueta(self):
        if np.isnan(self.nivel_fosforo):
            raise ValueError("El nivel de nitrógeno no está disponible.")

        # Crear un diccionario para almacenar los grados de pertenencia
        grados_pertenencia = {}

        # Para cada etiqueta en la variable de salida
        for etiqueta in self.nivel_fosforo_var.terms:
            # Obtener la función de pertenencia correspondiente
            funcion_pertenencia = self.nivel_fosforo_var[etiqueta].mf
            # Calcular el grado de pertenencia del valor de salida en esta función
            grado = fuzz.interp_membership(self.nivel_fosforo_var.universe, funcion_pertenencia, self.nivel_fosforo)
            # Almacenar el grado en el diccionario
            grados_pertenencia[etiqueta] = grado

        # Encontrar la etiqueta con el mayor grado de pertenencia
        etiqueta_predicha = max(grados_pertenencia, key=grados_pertenencia.get)

        return etiqueta_predicha
