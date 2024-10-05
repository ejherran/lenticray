import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class BalanceOxigeno:
    def __init__(self, custom_vars=dict(), **kwargs):
        self.custom_vars = custom_vars
        self.inputs = kwargs
        self.available_vars = {k: v for k, v in self.inputs.items() if not np.isnan(v)}
        self.balance_oxigeno = np.nan

        # Orden de prioridad de las variables
        self.priority_variables = [
            'O2_Dis', 'BOD', 'COD', 'PV'
        ]

        self.available_vars = {k: v for k, v in self.available_vars.items() if k in self.priority_variables}

        if not self.available_vars:
            raise ValueError(f"No se encontraron variables válidas para inferencia.")

        self._init_variables()
        self._crear_sistema_difuso()

    def _init_variables(self):
        self.base_vars = dict(
            O2_Dis=dict(
                universe = np.arange(0, 15.1, 0.1),  # Rango típico de 0 a 15 mg/L
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 2, 5]},
                    'MODERADO': {'type': 'trimf', 'params': [4, 6, 8]},
                    'ALTO': {'type': 'trimf', 'params': [7, 9, 11]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [10, 12, 15, 15]}
                }
            ),
            BOD=dict(
                universe = np.arange(0, 30.1, 0.1),  # Rango típico de 0 a 30 mg/L
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 2, 5]},
                    'MODERADO': {'type': 'trimf', 'params': [4, 7, 10]},
                    'ALTO': {'type': 'trimf', 'params': [9, 15, 20]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [18, 25, 30, 30]}
                }
            ),
            COD=dict(
                universe = np.arange(0, 100.1, 0.1),  # Rango típico de 0 a 100 mg/L
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 5, 15]},
                    'MODERADO': {'type': 'trimf', 'params': [10, 25, 40]},
                    'ALTO': {'type': 'trimf', 'params': [35, 55, 75]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [70, 85, 100, 100]}
                }
            ),
            PV=dict(
                universe = np.arange(0, 50.1, 0.1),  # Rango típico de 0 a 50 mg/L
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 2, 8]},
                    'MODERADO': {'type': 'trimf', 'params': [6, 12, 20]},
                    'ALTO': {'type': 'trimf', 'params': [18, 25, 35]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [30, 40, 50, 50]}
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
            self.variables['O2_Dis'] = antecedent

        elif 'BOD' in self.available_vars and 'COD' in self.available_vars:
            self.calculation_method = 'BOD_COD'
            # Definir variables difusas para BOD y COD
            universe_bod, mf_definitions_bod = self._get_variable_definitions('BOD')
            antecedent_bod = ctrl.Antecedent(universe_bod, 'BOD')
            for label, params in mf_definitions_bod.items():
                if params['type'] == 'trapmf':
                    antecedent_bod[label] = fuzz.trapmf(antecedent_bod.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent_bod[label] = fuzz.trimf(antecedent_bod.universe, params['params'])
            self.variables['BOD'] = antecedent_bod

            universe_cod, mf_definitions_cod = self._get_variable_definitions('COD')
            antecedent_cod = ctrl.Antecedent(universe_cod, 'COD')
            for label, params in mf_definitions_cod.items():
                if params['type'] == 'trapmf':
                    antecedent_cod[label] = fuzz.trapmf(antecedent_cod.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent_cod[label] = fuzz.trimf(antecedent_cod.universe, params['params'])
            self.variables['COD'] = antecedent_cod

        elif 'BOD' in self.available_vars and 'PV' in self.available_vars:
            self.calculation_method = 'BOD_PV'
            # Definir variables difusas para BOD y PV
            universe_bod, mf_definitions_bod = self._get_variable_definitions('BOD')
            antecedent_bod = ctrl.Antecedent(universe_bod, 'BOD')
            for label, params in mf_definitions_bod.items():
                if params['type'] == 'trapmf':
                    antecedent_bod[label] = fuzz.trapmf(antecedent_bod.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent_bod[label] = fuzz.trimf(antecedent_bod.universe, params['params'])
            self.variables['BOD'] = antecedent_bod

            universe_pv, mf_definitions_pv = self._get_variable_definitions('PV')
            antecedent_pv = ctrl.Antecedent(universe_pv, 'PV')
            for label, params in mf_definitions_pv.items():
                if params['type'] == 'trapmf':
                    antecedent_pv[label] = fuzz.trapmf(antecedent_pv.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent_pv[label] = fuzz.trimf(antecedent_pv.universe, params['params'])
            self.variables['PV'] = antecedent_pv

        else:
            # Usar variables individuales en orden de prioridad
            for var in self.priority_variables:
                if var in self.available_vars:
                    self.calculation_method = var
                    universe, mf_definitions = self._get_variable_definitions(var)
                    antecedent = ctrl.Antecedent(universe, var)
                    for label, params in mf_definitions.items():
                        if params['type'] == 'trapmf':
                            antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                        elif params['type'] == 'trimf':
                            antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
                    self.variables[var] = antecedent
                    break
            else:
                # Si no hay variables disponibles, error
                raise ValueError("No hay variables válidas disponibles para crear el sistema difuso.")

        # Definir variable de salida
        self.balance_oxigeno_universe = np.arange(0, 1.01, 0.01)
        self.balance_oxigeno_var = ctrl.Consequent(self.balance_oxigeno_universe, 'balance_oxigeno')
        self.balance_oxigeno_var['BUENO'] = fuzz.trapmf(self.balance_oxigeno_var.universe, [0, 0, 0.2, 0.4])
        self.balance_oxigeno_var['MODERADO'] = fuzz.trimf(self.balance_oxigeno_var.universe, [0.3, 0.5, 0.7])
        self.balance_oxigeno_var['MALO'] = fuzz.trimf(self.balance_oxigeno_var.universe, [0.6, 0.75, 0.9])
        self.balance_oxigeno_var['MUY MALO'] = fuzz.trapmf(self.balance_oxigeno_var.universe, [0.85, 0.95, 1, 1])

        # Definir reglas difusas basadas en la variable seleccionada
        if self.calculation_method == 'O2_Dis':
            # Reglas basadas en O2_Dis (a mayor oxígeno disuelto, mejor balance)
            antecedent = self.variables['O2_Dis']
            self.rules.append(ctrl.Rule(antecedent['BAJO'], self.balance_oxigeno_var['MUY MALO']))
            self.rules.append(ctrl.Rule(antecedent['MODERADO'], self.balance_oxigeno_var['MALO']))
            self.rules.append(ctrl.Rule(antecedent['ALTO'], self.balance_oxigeno_var['MODERADO']))
            self.rules.append(ctrl.Rule(antecedent['MUY ALTO'], self.balance_oxigeno_var['BUENO']))
        elif self.calculation_method == 'BOD_COD':
            # Reglas combinadas basadas en BOD y COD
            antecedent_bod = self.variables['BOD']
            antecedent_cod = self.variables['COD']
            self.rules.append(ctrl.Rule(antecedent_bod['BAJO'] & antecedent_cod['BAJO'], self.balance_oxigeno_var['BUENO']))
            self.rules.append(ctrl.Rule(antecedent_bod['MODERADO'] | antecedent_cod['MODERADO'], self.balance_oxigeno_var['MODERADO']))
            self.rules.append(ctrl.Rule(antecedent_bod['ALTO'] | antecedent_cod['ALTO'], self.balance_oxigeno_var['MALO']))
            self.rules.append(ctrl.Rule(antecedent_bod['MUY ALTO'] | antecedent_cod['MUY ALTO'], self.balance_oxigeno_var['MUY MALO']))
        elif self.calculation_method == 'BOD_PV':
            # Reglas combinadas basadas en BOD y PV
            antecedent_bod = self.variables['BOD']
            antecedent_pv = self.variables['PV']
            self.rules.append(ctrl.Rule(antecedent_bod['BAJO'] & antecedent_pv['BAJO'], self.balance_oxigeno_var['BUENO']))
            self.rules.append(ctrl.Rule(antecedent_bod['MODERADO'] | antecedent_pv['MODERADO'], self.balance_oxigeno_var['MODERADO']))
            self.rules.append(ctrl.Rule(antecedent_bod['ALTO'] | antecedent_pv['ALTO'], self.balance_oxigeno_var['MALO']))
            self.rules.append(ctrl.Rule(antecedent_bod['MUY ALTO'] | antecedent_pv['MUY ALTO'], self.balance_oxigeno_var['MUY MALO']))
        else:
            # Reglas basadas en la variable individual seleccionada
            var_name = self.calculation_method
            antecedent = self.variables[var_name]
            # Para BOD, COD y PV, mayor valor implica peor balance
            self.rules.append(ctrl.Rule(antecedent['BAJO'], self.balance_oxigeno_var['BUENO']))
            self.rules.append(ctrl.Rule(antecedent['MODERADO'], self.balance_oxigeno_var['MODERADO']))
            self.rules.append(ctrl.Rule(antecedent['ALTO'], self.balance_oxigeno_var['MALO']))
            self.rules.append(ctrl.Rule(antecedent['MUY ALTO'], self.balance_oxigeno_var['MUY MALO']))

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def calcular_inferencia(self):
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
            self.balance_oxigeno = self.simulation.output['balance_oxigeno']

        except Exception as e:
            raise ValueError(f"Error al calcular la inferencia: {e}")

        return self.calculation_method

    def obtener_etiqueta(self):
        if np.isnan(self.balance_oxigeno):
            raise ValueError("El balance de oxígeno no está disponible.")

        # Crear un diccionario para almacenar los grados de pertenencia
        grados_pertenencia = {}

        # Para cada etiqueta en la variable de salida
        for etiqueta in self.balance_oxigeno_var.terms:
            # Obtener la función de pertenencia correspondiente
            funcion_pertenencia = self.balance_oxigeno_var[etiqueta].mf
            # Calcular el grado de pertenencia del valor de salida en esta función
            grado = fuzz.interp_membership(self.balance_oxigeno_var.universe, funcion_pertenencia, self.balance_oxigeno)
            # Almacenar el grado en el diccionario
            grados_pertenencia[etiqueta] = grado

        # Encontrar la etiqueta con el mayor grado de pertenencia
        etiqueta_predicha = max(grados_pertenencia, key=grados_pertenencia.get)

        return etiqueta_predicha
