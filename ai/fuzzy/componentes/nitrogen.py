import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class NivelNitrogeno:
    def __init__(self, custom_vars=dict(), **kwargs):
        self.custom_vars = custom_vars
        self.inputs = kwargs
        self.available_vars = {k: v for k, v in self.inputs.items() if not np.isnan(v)}
        self.nivel_nitrogeno = np.nan

        # Orden de prioridad de las variables
        self.priority_variables = [
            'TN', 'TDN', 'TKN', 'DIN', 'NOxN', 'NH4N', 'NO3N', 'NO2N',
            'DKN', 'NH3N', 'DON', 'PN', 'PON', 'TON'
        ]

        self.available_vars = {k: v for k, v in self.available_vars.items() if k in self.priority_variables}

        if not self.available_vars:
            raise ValueError(f"No se encontraron variables válidas para inferencia.")

        self._init_variables()
        self._crear_sistema_difuso()

    def _init_variables(self):
        self.base_vars = dict(
            DIN=dict(
                universe = np.arange(0, 5.1, 0.1),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.2, 0.5]},
                    'MODERADO': {'type': 'trimf', 'params': [0.3, 0.8, 1.3]},
                    'ALTO': {'type': 'trimf', 'params': [1, 1.8, 2.5]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [2, 3, 5, 5]}
                }
            ),
            DKN=dict(
                universe = np.arange(0, 5.1, 0.1),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.2, 0.5]},
                    'MODERADO': {'type': 'trimf', 'params': [0.3, 0.8, 1.3]},
                    'ALTO': {'type': 'trimf', 'params': [1, 1.8, 2.5]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [2, 3, 5, 5]}
                }
            ),
            NH3N=dict(
                universe = np.arange(0, 1.01, 0.01),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.02, 0.05]},
                    'MODERADO': {'type': 'trimf', 'params': [0.03, 0.1, 0.2]},
                    'ALTO': {'type': 'trimf', 'params': [0.15, 0.3, 0.5]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [0.4, 0.6, 1, 1]}
                }
            ),
            NH4N=dict(
                universe = np.arange(0, 2.1, 0.1),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.05, 0.1]},
                    'MODERADO': {'type': 'trimf', 'params': [0.08, 0.2, 0.4]},
                    'ALTO': {'type': 'trimf', 'params': [0.3, 0.6, 1]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [0.8, 1.5, 2, 2]}
                }
            ),
            NOxN=dict(
                universe = np.arange(0, 10.1, 0.1),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.5, 1]},
                    'MODERADO': {'type': 'trimf', 'params': [0.8, 2, 3.5]},
                    'ALTO': {'type': 'trimf', 'params': [3, 5, 7]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [6.5, 8, 10, 10]}
                }
            ),
            NO2N=dict(
                universe = np.arange(0, 1.01, 0.01),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.01, 0.03]},
                    'MODERADO': {'type': 'trimf', 'params': [0.02, 0.05, 0.1]},
                    'ALTO': {'type': 'trimf', 'params': [0.08, 0.2, 0.4]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [0.35, 0.6, 1, 1]}
                }
            ),
            NO3N=dict(
                universe = np.arange(0, 10.1, 0.1),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.5, 1]},
                    'MODERADO': {'type': 'trimf', 'params': [0.8, 2, 3.5]},
                    'ALTO': {'type': 'trimf', 'params': [3, 5, 7]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [6.5, 8, 10, 10]}
                }
            ),
            PN=dict(
                universe = np.arange(0, 5.1, 0.1),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.1, 0.3]},
                    'MODERADO': {'type': 'trimf', 'params': [0.2, 0.5, 1]},
                    'ALTO': {'type': 'trimf', 'params': [0.8, 1.5, 2.5]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [2, 3.5, 5, 5]}
                }
            ),
            PON=dict(
                universe = np.arange(0, 5.1, 0.1),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.1, 0.3]},
                    'MODERADO': {'type': 'trimf', 'params': [0.2, 0.5, 1]},
                    'ALTO': {'type': 'trimf', 'params': [0.8, 1.5, 2.5]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [2, 3.5, 5, 5]}
                }
            ),
            TDN=dict(
                universe = np.arange(0, 10.1, 0.1),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.5, 1]},
                    'MODERADO': {'type': 'trimf', 'params': [0.5, 1.5, 2.5]},
                    'ALTO': {'type': 'trimf', 'params': [2, 3.5, 5]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [4.5, 7, 10, 10]}
                }
            ),
            TKN=dict(
                universe = np.arange(0, 10.1, 0.1),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.3, 0.8]},
                    'MODERADO': {'type': 'trimf', 'params': [0.5, 1.5, 2.5]},
                    'ALTO': {'type': 'trimf', 'params': [2, 3.5, 5]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [4.5, 7, 10, 10]}
                }
            ),
            TN=dict(
                universe = np.arange(0, 10.1, 0.1),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.5, 1]},
                    'MODERADO': {'type': 'trimf', 'params': [0.5, 1.5, 2.5]},
                    'ALTO': {'type': 'trimf', 'params': [2, 3.5, 5]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [4.5, 7, 10, 10]}
                }
            ),
            TON=dict(
                universe = np.arange(0, 5.1, 0.1),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.1, 0.3]},
                    'MODERADO': {'type': 'trimf', 'params': [0.2, 0.5, 1]},
                    'ALTO': {'type': 'trimf', 'params': [0.8, 1.5, 2.5]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [2, 3.5, 5, 5]}
                }
            ),
            DON=dict(
                universe = np.arange(0, 5.1, 0.1),
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.1, 0.3]},
                    'MODERADO': {'type': 'trimf', 'params': [0.2, 0.5, 1]},
                    'ALTO': {'type': 'trimf', 'params': [0.8, 1.5, 2.5]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [2, 3.5, 5, 5]}
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

        # Opción 1: Variable ideal - TN (Total Nitrogen)
        if 'TN' in self.available_vars:
            self.calculation_method = 'TN'
            # Definir variable difusa para TN
            universe, mf_definitions = self._get_variable_definitions('TN')
            antecedent = ctrl.Antecedent(universe, 'TN')
            for label, params in mf_definitions.items():
                if params['type'] == 'trapmf':
                    antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
            self.variables['TN'] = antecedent

        # Opción 2: Calcular TN a partir de TDN y PN
        elif 'TDN' in self.available_vars and 'PN' in self.available_vars:
            self.calculation_method = 'TDN_PN'
            # Definir variable difusa para TN (calculado)
            universe, mf_definitions = self._get_variable_definitions('TN')
            antecedent = ctrl.Antecedent(universe, 'TN')
            for label, params in mf_definitions.items():
                if params['type'] == 'trapmf':
                    antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
            self.variables['TN'] = antecedent

        # Opción 3: Calcular TN a partir de TKN y NOxN
        elif 'TKN' in self.available_vars and 'NOxN' in self.available_vars:
            self.calculation_method = 'TKN_NOxN'
            # Definir variable difusa para TN (calculado)
            universe, mf_definitions = self._get_variable_definitions('TN')
            antecedent = ctrl.Antecedent(universe, 'TN')
            for label, params in mf_definitions.items():
                if params['type'] == 'trapmf':
                    antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
            self.variables['TN'] = antecedent

        # Opción 4: Usar variables individuales
        else:
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
                raise ValueError("No se encontraron variables válidas para inferencia.")

        # Definir variable de salida
        self.nivel_nitrogeno_universe = np.arange(0, 1.01, 0.01)
        self.nivel_nitrogeno_var = ctrl.Consequent(self.nivel_nitrogeno_universe, 'nivel_nitrogeno')
        self.nivel_nitrogeno_var['BAJO'] = fuzz.trapmf(self.nivel_nitrogeno_var.universe, [0, 0, 0.15, 0.3])
        self.nivel_nitrogeno_var['MODERADO'] = fuzz.trimf(self.nivel_nitrogeno_var.universe, [0.25, 0.4, 0.55])
        self.nivel_nitrogeno_var['ALTO'] = fuzz.trimf(self.nivel_nitrogeno_var.universe, [0.5, 0.65, 0.8])
        self.nivel_nitrogeno_var['MUY ALTO'] = fuzz.trapmf(self.nivel_nitrogeno_var.universe, [0.75, 0.85, 1, 1])

        # Definir reglas difusas
        if self.calculation_method in ['TN', 'TDN_PN', 'TKN_NOxN']:
            # Reglas basadas en TN
            self.rules.append(ctrl.Rule(self.variables['TN']['BAJO'], self.nivel_nitrogeno_var['BAJO']))
            self.rules.append(ctrl.Rule(self.variables['TN']['MODERADO'], self.nivel_nitrogeno_var['MODERADO']))
            self.rules.append(ctrl.Rule(self.variables['TN']['ALTO'], self.nivel_nitrogeno_var['ALTO']))
            self.rules.append(ctrl.Rule(self.variables['TN']['MUY ALTO'], self.nivel_nitrogeno_var['MUY ALTO']))
        else:
            # Reglas basadas en variables individuales
            var_name = self.calculation_method
            antecedent = self.variables[var_name]
            self.rules.append(ctrl.Rule(antecedent['BAJO'], self.nivel_nitrogeno_var['BAJO']))
            self.rules.append(ctrl.Rule(antecedent['MODERADO'], self.nivel_nitrogeno_var['MODERADO']))
            self.rules.append(ctrl.Rule(antecedent['ALTO'], self.nivel_nitrogeno_var['ALTO']))
            self.rules.append(ctrl.Rule(antecedent['MUY ALTO'], self.nivel_nitrogeno_var['MUY ALTO']))

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def calcular_inferencia(self):
        if not hasattr(self, 'simulation'):
            raise ValueError("No ha sido posible crear el sistema de control.")

        # Opción 1: Usando TN directamente
        if self.calculation_method == 'TN':
            tn_value = self.available_vars['TN']
            self.simulation.input['TN'] = tn_value

        # Opción 2: Calcular TN a partir de TDN y PN
        elif self.calculation_method == 'TDN_PN':
            tdn_value = self.available_vars['TDN']
            pn_value = self.available_vars['PN']
            tn_value = tdn_value + pn_value
            self.simulation.input['TN'] = tn_value

        # Opción 3: Calcular TN a partir de TKN y NOxN
        elif self.calculation_method == 'TKN_NOxN':
            tkn_value = self.available_vars['TKN']
            noxn_value = self.available_vars['NOxN']
            tn_value = tkn_value + noxn_value
            self.simulation.input['TN'] = tn_value

        # Opción 4: Usar variables individuales
        else:
            var_name = self.calculation_method
            self.simulation.input[var_name] = self.available_vars[var_name]

        # Realizar la computación
        try:
            self.simulation.compute()
            self.nivel_nitrogeno = self.simulation.output['nivel_nitrogeno']
        except Exception as e:
            raise ValueError(f"Error al calcular la inferencia: {e}")

        return self.calculation_method

    def obtener_etiqueta(self):
        if np.isnan(self.nivel_nitrogeno):
            raise ValueError("El nivel de nitrógeno no está disponible.")

        # Crear un diccionario para almacenar los grados de pertenencia
        grados_pertenencia = {}

        # Para cada etiqueta en la variable de salida
        for etiqueta in self.nivel_nitrogeno_var.terms:
            # Obtener la función de pertenencia correspondiente
            funcion_pertenencia = self.nivel_nitrogeno_var[etiqueta].mf
            # Calcular el grado de pertenencia del valor de salida en esta función
            grado = fuzz.interp_membership(self.nivel_nitrogeno_var.universe, funcion_pertenencia, self.nivel_nitrogeno)
            # Almacenar el grado en el diccionario
            grados_pertenencia[etiqueta] = grado

        # Encontrar la etiqueta con el mayor grado de pertenencia
        etiqueta_predicha = max(grados_pertenencia, key=grados_pertenencia.get)

        return etiqueta_predicha
