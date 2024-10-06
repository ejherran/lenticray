import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class NivelSolidos:
    def __init__(self, custom_vars=dict(), **kwargs):
        self.custom_vars = custom_vars
        self.inputs = kwargs
        self.available_vars = {k: v for k, v in self.inputs.items() if not np.isnan(v)}
        self.nivel_solidos = np.nan

        # Orden de prioridad de las variables
        self.priority_variables = ['TS', 'TDS', 'TSS', 'FDS', 'VDS', 'FS', 'VS']

        self.available_vars = {k: v for k, v in self.available_vars.items() if k in self.priority_variables}

        if not self.available_vars:
            raise ValueError("No se encontraron variables válidas para inferencia.")

        self._init_variables()
        self._crear_sistema_difuso()

    def _init_variables(self):
        self.base_vars = dict(
            TS=dict(
                # Definición para Total Solids
                universe = np.arange(0, 2001, 1),  # Rango de 0 a 2000 mg/L
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 200, 500]},
                    'MODERADO': {'type': 'trimf', 'params': [400, 700, 1000]},
                    'ALTO': {'type': 'trimf', 'params': [900, 1200, 1500]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [1400, 1700, 2000, 2000]}
                }
            ),
            TDS=dict(
                # Definición para Total Dissolved Solids
                universe = np.arange(0, 1501, 1),  # Rango de 0 a 1500 mg/L
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 150, 300]},
                    'MODERADO': {'type': 'trimf', 'params': [250, 500, 750]},
                    'ALTO': {'type': 'trimf', 'params': [700, 900, 1100]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [1000, 1250, 1500, 1500]}
                }
            ),
            TSS=dict(
                # Definición para Total Suspended Solids
                universe = np.arange(0, 500.1, 0.1),  # Rango de 0 a 500 mg/L
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 20, 50]},
                    'MODERADO': {'type': 'trimf', 'params': [40, 100, 200]},
                    'ALTO': {'type': 'trimf', 'params': [150, 250, 350]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [300, 400, 500, 500]}
                }
            ),
            FS=dict(
                # Definición para Fixed Solids
                universe = np.arange(0, 1001, 1),  # Rango de 0 a 1000 mg/L
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 100, 250]},
                    'MODERADO': {'type': 'trimf', 'params': [200, 350, 500]},
                    'ALTO': {'type': 'trimf', 'params': [450, 600, 750]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [700, 850, 1000, 1000]}
                }
            ),
            VS=dict(
                # Definición para Volatile Solids
                universe = np.arange(0, 1001, 1),  # Rango de 0 a 1000 mg/L
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 100, 250]},
                    'MODERADO': {'type': 'trimf', 'params': [200, 350, 500]},
                    'ALTO': {'type': 'trimf', 'params': [450, 600, 750]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [700, 850, 1000, 1000]}
                }
            ),
            FDS=dict(
                # Definición para Fixed Dissolved Solids
                universe = np.arange(0, 1001, 1),  # Rango de 0 a 1000 mg/L
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 100, 250]},
                    'MODERADO': {'type': 'trimf', 'params': [200, 350, 500]},
                    'ALTO': {'type': 'trimf', 'params': [450, 600, 750]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [700, 850, 1000, 1000]}
                }
            ),
            VDS=dict(
                # Definición para Volatile Dissolved Solids
                universe = np.arange(0, 1001, 1),  # Rango de 0 a 1000 mg/L
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 100, 250]},
                    'MODERADO': {'type': 'trimf', 'params': [200, 350, 500]},
                    'ALTO': {'type': 'trimf', 'params': [450, 600, 750]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [700, 850, 1000, 1000]}
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
        if 'TS' in self.available_vars:
            self.calculation_method = 'TS'
            # Definir variable difusa para TS
            universe, mf_definitions = self._get_variable_definitions('TS')
            antecedent = ctrl.Antecedent(universe, 'TS')
            for label, params in mf_definitions.items():
                if params['type'] == 'trapmf':
                    antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
            self.variables['TS'] = antecedent

        elif 'TDS' in self.available_vars and 'TSS' in self.available_vars:
            self.calculation_method = 'TDS_TSS'
            # Definir variable difusa para TS (calculado)
            universe, mf_definitions = self._get_variable_definitions('TS')
            antecedent = ctrl.Antecedent(universe, 'TS')
            for label, params in mf_definitions.items():
                if params['type'] == 'trapmf':
                    antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
            self.variables['TS'] = antecedent

        elif 'FS' in self.available_vars and 'VS' in self.available_vars:
            self.calculation_method = 'FS_VS'
            # Definir variable difusa para TS (estimado)
            universe, mf_definitions = self._get_variable_definitions('TS')
            antecedent = ctrl.Antecedent(universe, 'TS')
            for label, params in mf_definitions.items():
                if params['type'] == 'trapmf':
                    antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
            self.variables['TS'] = antecedent

        elif 'TDS' in self.available_vars:
            self.calculation_method = 'TDS'
            universe, mf_definitions = self._get_variable_definitions('TDS')
            antecedent = ctrl.Antecedent(universe, 'TDS')
            for label, params in mf_definitions.items():
                if params['type'] == 'trapmf':
                    antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
            self.variables['TDS'] = antecedent

        elif 'TSS' in self.available_vars:
            self.calculation_method = 'TSS'
            universe, mf_definitions = self._get_variable_definitions('TSS')
            antecedent = ctrl.Antecedent(universe, 'TSS')
            for label, params in mf_definitions.items():
                if params['type'] == 'trapmf':
                    antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
            self.variables['TSS'] = antecedent

        elif 'FDS' in self.available_vars and 'VDS' in self.available_vars:
            self.calculation_method = 'FDS_VDS'
            # Definir variable difusa para TDS (estimado)
            universe, mf_definitions = self._get_variable_definitions('TDS')
            antecedent = ctrl.Antecedent(universe, 'TDS')
            for label, params in mf_definitions.items():
                if params['type'] == 'trapmf':
                    antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
            self.variables['TDS'] = antecedent

        elif 'FDS' in self.available_vars:
            self.calculation_method = 'FDS'
            universe, mf_definitions = self._get_variable_definitions('FDS')
            antecedent = ctrl.Antecedent(universe, 'FDS')
            for label, params in mf_definitions.items():
                if params['type'] == 'trapmf':
                    antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
            self.variables['FDS'] = antecedent

        elif 'VDS' in self.available_vars:
            self.calculation_method = 'VDS'
            universe, mf_definitions = self._get_variable_definitions('VDS')
            antecedent = ctrl.Antecedent(universe, 'VDS')
            for label, params in mf_definitions.items():
                if params['type'] == 'trapmf':
                    antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
            self.variables['VDS'] = antecedent

        elif 'FS' in self.available_vars:
            self.calculation_method = 'FS'
            universe, mf_definitions = self._get_variable_definitions('FS')
            antecedent = ctrl.Antecedent(universe, 'FS')
            for label, params in mf_definitions.items():
                if params['type'] == 'trapmf':
                    antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
            self.variables['FS'] = antecedent

        elif 'VS' in self.available_vars:
            self.calculation_method = 'VS'
            universe, mf_definitions = self._get_variable_definitions('VS')
            antecedent = ctrl.Antecedent(universe, 'VS')
            for label, params in mf_definitions.items():
                if params['type'] == 'trapmf':
                    antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                elif params['type'] == 'trimf':
                    antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
            self.variables['VS'] = antecedent

        else:
            # Si no hay variables disponibles, error
            raise ValueError("No hay variables válidas disponibles para crear el sistema difuso.")

        # Definir variable de salida
        self.nivel_solidos_universe = np.arange(0, 1.01, 0.01)
        self.nivel_solidos_var = ctrl.Consequent(self.nivel_solidos_universe, 'nivel_solidos')
        self.nivel_solidos_var['BAJO'] = fuzz.trapmf(self.nivel_solidos_var.universe, [0, 0, 0.2, 0.4])
        self.nivel_solidos_var['MODERADO'] = fuzz.trimf(self.nivel_solidos_var.universe, [0.3, 0.5, 0.7])
        self.nivel_solidos_var['ALTO'] = fuzz.trimf(self.nivel_solidos_var.universe, [0.6, 0.75, 0.9])
        self.nivel_solidos_var['MUY ALTO'] = fuzz.trapmf(self.nivel_solidos_var.universe, [0.85, 0.95, 1, 1])

        # Definir reglas difusas basadas en la variable seleccionada
        if self.calculation_method in ['TS', 'TDS_TSS', 'FS_VS']:
            # Reglas basadas en TS
            self.rules.append(ctrl.Rule(self.variables['TS']['BAJO'], self.nivel_solidos_var['BAJO']))
            self.rules.append(ctrl.Rule(self.variables['TS']['MODERADO'], self.nivel_solidos_var['MODERADO']))
            self.rules.append(ctrl.Rule(self.variables['TS']['ALTO'], self.nivel_solidos_var['ALTO']))
            self.rules.append(ctrl.Rule(self.variables['TS']['MUY ALTO'], self.nivel_solidos_var['MUY ALTO']))
        elif self.calculation_method == 'FDS_VDS':
            # Reglas basadas en TDS estimado
            self.rules.append(ctrl.Rule(self.variables['TDS']['BAJO'], self.nivel_solidos_var['BAJO']))
            self.rules.append(ctrl.Rule(self.variables['TDS']['MODERADO'], self.nivel_solidos_var['MODERADO']))
            self.rules.append(ctrl.Rule(self.variables['TDS']['ALTO'], self.nivel_solidos_var['ALTO']))
            self.rules.append(ctrl.Rule(self.variables['TDS']['MUY ALTO'], self.nivel_solidos_var['MUY ALTO']))
        else:
            # Reglas basadas en la variable individual seleccionada
            var_name = self.calculation_method
            antecedent = self.variables[var_name]
            self.rules.append(ctrl.Rule(antecedent['BAJO'], self.nivel_solidos_var['BAJO']))
            self.rules.append(ctrl.Rule(antecedent['MODERADO'], self.nivel_solidos_var['MODERADO']))
            self.rules.append(ctrl.Rule(antecedent['ALTO'], self.nivel_solidos_var['ALTO']))
            self.rules.append(ctrl.Rule(antecedent['MUY ALTO'], self.nivel_solidos_var['MUY ALTO']))

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def calcular_inferencia(self):
        if not hasattr(self, 'simulation'):
            raise ValueError("No ha sido posible crear el sistema de control.")

        try:
            if self.calculation_method == 'TS':
                ts_value = self.available_vars['TS']
                self.simulation.input['TS'] = ts_value

            elif self.calculation_method == 'TDS_TSS':
                tds_value = self.available_vars['TDS']
                tss_value = self.available_vars['TSS']
                ts_value = tds_value + tss_value
                self.simulation.input['TS'] = ts_value

            elif self.calculation_method == 'FS_VS':
                fs_value = self.available_vars['FS']
                vs_value = self.available_vars['VS']
                ts_value = fs_value + vs_value
                self.simulation.input['TS'] = ts_value

            elif self.calculation_method == 'FDS_VDS':
                fds_value = self.available_vars['FDS']
                vds_value = self.available_vars['VDS']
                tds_value = fds_value + vds_value
                self.simulation.input['TDS'] = tds_value

            else:
                var_name = self.calculation_method
                var_value = self.available_vars[var_name]
                self.simulation.input[var_name] = var_value

            # Realizar la computación
            self.simulation.compute()
            self.nivel_solidos = self.simulation.output['nivel_solidos']

        except Exception as e:
            raise ValueError(f"Error al calcular la inferencia: {e}")

        return self.calculation_method

    def obtener_etiqueta(self):
        if np.isnan(self.nivel_solidos):
            raise ValueError("El nivel de sólidos no está disponible.")

        # Crear un diccionario para almacenar los grados de pertenencia
        grados_pertenencia = {}

        # Para cada etiqueta en la variable de salida
        for etiqueta in self.nivel_solidos_var.terms:
            # Obtener la función de pertenencia correspondiente
            funcion_pertenencia = self.nivel_solidos_var[etiqueta].mf
            # Calcular el grado de pertenencia del valor de salida en esta función
            grado = fuzz.interp_membership(self.nivel_solidos_var.universe, funcion_pertenencia, self.nivel_solidos)
            # Almacenar el grado en el diccionario
            grados_pertenencia[etiqueta] = grado

        # Encontrar la etiqueta con el mayor grado de pertenencia
        etiqueta_predicha = max(grados_pertenencia, key=grados_pertenencia.get)

        return etiqueta_predicha
