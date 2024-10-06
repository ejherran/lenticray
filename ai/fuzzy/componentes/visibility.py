import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class NivelVisibilidad:
    def __init__(self, custom_vars=dict(), **kwargs):
        self.custom_vars = custom_vars
        self.inputs = kwargs
        self.available_vars = {k: v for k, v in self.inputs.items() if not np.isnan(v)}
        self.nivel_visibilidad = np.nan

        # Orden de prioridad de las variables
        self.priority_variables = ['TRANS', 'TURB']

        self.available_vars = {k: v for k, v in self.available_vars.items() if k in self.priority_variables}

        if not self.available_vars:
            raise ValueError("No se encontraron variables válidas para inferencia.")

        self._init_variables()
        self._crear_sistema_difuso()

    def _init_variables(self):
        self.base_vars = dict(
            TRANS=dict(
                # Definición para Transparencia
                universe = np.arange(0, 10.1, 0.1),  # Profundidad en metros
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 0.25, 0.6]},
                    'MODERADO': {'type': 'trimf', 'params': [0.5, 1.25, 2.1]},
                    'ALTO': {'type': 'trimf', 'params': [2, 3, 4.1]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [4, 5, 10, 10]}
                }
            ),
            TURB=dict(
                # Definición para Turbidez
                universe = np.arange(0, 100.1, 0.1),  # Unidades de turbidez (NTU)
                mf_definitions = {
                    'BAJO': {'type': 'trapmf', 'params': [0, 0, 5, 15]},
                    'MODERADO': {'type': 'trimf', 'params': [10, 30, 50]},
                    'ALTO': {'type': 'trimf', 'params': [40, 60, 80]},
                    'MUY ALTO': {'type': 'trapmf', 'params': [70, 90, 100, 100]}
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
        """
        Crea el sistema difuso basado en las variables disponibles y sus prioridades.
        Define las reglas y configura el sistema de control.
        """
        # Inicializar estructuras
        self.rules = []
        self.variables_fuzzy = {}
        self.calculation_method = None  # Método utilizado para el cálculo

        # Prioridad de las variables
        for var in self.priority_variables:
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
                self.variables_fuzzy[var] = antecedent
                break  # Solo usar la primera variable disponible según prioridad

        # Si ninguna variable de alta prioridad está disponible, usar combinaciones si es posible
        if not self.variables_fuzzy:
            # Ejemplo: Combinar TRANS y TURB para inferir visibilidad
            if all(var in self.available_vars for var in ['TRANS', 'TURB']):
                self.calculation_method = 'TRANS_TURB'
                # Definir variables difusas para TRANS y TURB
                universe_trans, mf_definitions_trans = self._get_variable_definitions('TRANS')
                antecedent_trans = ctrl.Antecedent(universe_trans, 'TRANS')
                for label, params in mf_definitions_trans.items():
                    if params['type'] == 'trapmf':
                        antecedent_trans[label] = fuzz.trapmf(antecedent_trans.universe, params['params'])
                    elif params['type'] == 'trimf':
                        antecedent_trans[label] = fuzz.trimf(antecedent_trans.universe, params['params'])
                self.variables_fuzzy['TRANS'] = antecedent_trans

                universe_turb, mf_definitions_turb = self._get_variable_definitions('TURB')
                antecedent_turb = ctrl.Antecedent(universe_turb, 'TURB')
                for label, params in mf_definitions_turb.items():
                    if params['type'] == 'trapmf':
                        antecedent_turb[label] = fuzz.trapmf(antecedent_turb.universe, params['params'])
                    elif params['type'] == 'trimf':
                        antecedent_turb[label] = fuzz.trimf(antecedent_turb.universe, params['params'])
                self.variables_fuzzy['TURB'] = antecedent_turb
            else:
                raise ValueError("No hay suficientes variables disponibles para crear el sistema difuso.")

        # Definir variable de salida
        self.nivel_visibilidad_universe = np.arange(0, 1.01, 0.01)
        self.nivel_visibilidad_var = ctrl.Consequent(self.nivel_visibilidad_universe, 'nivel_visibilidad')
        self.nivel_visibilidad_var['BAJO'] = fuzz.trapmf(self.nivel_visibilidad_var.universe, [0, 0, 0.2, 0.4])
        self.nivel_visibilidad_var['MODERADO'] = fuzz.trimf(self.nivel_visibilidad_var.universe, [0.3, 0.5, 0.7])
        self.nivel_visibilidad_var['ALTO'] = fuzz.trimf(self.nivel_visibilidad_var.universe, [0.6, 0.8, 0.95])
        self.nivel_visibilidad_var['MUY ALTO'] = fuzz.trapmf(self.nivel_visibilidad_var.universe, [0.9, 0.95, 1, 1])

        # Definir reglas difusas basadas en la variable seleccionada
        if self.calculation_method in ['TRANS', 'TURB']:
            var = self.calculation_method
            antecedent = self.variables_fuzzy[var]
            if var == 'TRANS':
                # Reglas basadas en TRANS
                self.rules.append(ctrl.Rule(antecedent['BAJO'], self.nivel_visibilidad_var['BAJO']))
                self.rules.append(ctrl.Rule(antecedent['MODERADO'], self.nivel_visibilidad_var['MODERADO']))
                self.rules.append(ctrl.Rule(antecedent['ALTO'], self.nivel_visibilidad_var['ALTO']))
                self.rules.append(ctrl.Rule(antecedent['MUY ALTO'], self.nivel_visibilidad_var['MUY ALTO']))
            elif var == 'TURB':
                # Reglas basadas en TURB
                self.rules.append(ctrl.Rule(antecedent['BAJO'], self.nivel_visibilidad_var['MUY ALTO']))
                self.rules.append(ctrl.Rule(antecedent['MODERADO'], self.nivel_visibilidad_var['ALTO']))
                self.rules.append(ctrl.Rule(antecedent['ALTO'], self.nivel_visibilidad_var['MODERADO']))
                self.rules.append(ctrl.Rule(antecedent['MUY ALTO'], self.nivel_visibilidad_var['BAJO']))
        elif self.calculation_method == 'TRANS_TURB':
            # Reglas combinadas basadas en TRANS y TURB
            antecedent_trans = self.variables_fuzzy['TRANS']
            antecedent_turb = self.variables_fuzzy['TURB']

            # Reglas:
            # Si TRANS es MUY ALTO y TURB es BAJO => MUY ALTO
            self.rules.append(ctrl.Rule(antecedent_trans['MUY ALTO'] & antecedent_turb['BAJO'], self.nivel_visibilidad_var['MUY ALTO']))

            # Si TRANS es ALTO y TURB es BAJO => ALTO
            self.rules.append(ctrl.Rule(antecedent_trans['ALTO'] & antecedent_turb['BAJO'], self.nivel_visibilidad_var['ALTO']))

            # Si TRANS es MODERADO o TURB es MODERADO => MODERADO
            self.rules.append(ctrl.Rule(antecedent_trans['MODERADO'] | antecedent_turb['MODERADO'], self.nivel_visibilidad_var['MODERADO']))

            # Si TRANS es BAJO o TURB es ALTO o MUY ALTO => BAJO
            self.rules.append(ctrl.Rule(antecedent_trans['BAJO'] | antecedent_turb['ALTO'] | antecedent_turb['MUY ALTO'], self.nivel_visibilidad_var['BAJO']))
        else:
            raise ValueError("Método de cálculo no reconocido.")

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def calcular_inferencia(self):
        """
        Calcula la inferencia difusa para determinar el nivel de visibilidad.

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
            self.nivel_visibilidad = self.simulation.output['nivel_visibilidad']

        except Exception as e:
            print(f"Método de cálculo: {self.calculation_method}")
            print(f"Inputs: {self.simulation.input}")
            raise ValueError(f"Error al calcular la inferencia: {e}")

        return self.calculation_method

    def obtener_etiqueta(self):
        """
        Obtiene la etiqueta correspondiente al nivel de visibilidad inferido.

        Retorna:
            etiqueta_predicha (str): Etiqueta del nivel de visibilidad.
        """
        if np.isnan(self.nivel_visibilidad):
            raise ValueError("El nivel de visibilidad no está disponible.")

        # Crear un diccionario para almacenar los grados de pertenencia
        grados_pertenencia = {}

        # Para cada etiqueta en la variable de salida
        for etiqueta in self.nivel_visibilidad_var.terms:
            # Obtener la función de pertenencia correspondiente
            funcion_pertenencia = self.nivel_visibilidad_var[etiqueta].mf
            # Calcular el grado de pertenencia del valor de salida en esta función
            grado = fuzz.interp_membership(self.nivel_visibilidad_var.universe, funcion_pertenencia, self.nivel_visibilidad)
            # Almacenar el grado en el diccionario
            grados_pertenencia[etiqueta] = grado

        # Encontrar la etiqueta con el mayor grado de pertenencia
        etiqueta_predicha = max(grados_pertenencia, key=grados_pertenencia.get)

        return etiqueta_predicha
