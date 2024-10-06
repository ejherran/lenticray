import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class CondicionesAdicionales:
    def __init__(self, custom_vars=dict(), **kwargs):
        """
        Inicializa la clase CondicionesAdicionales.

        Parámetros:
            custom_vars (dict): Definiciones personalizadas de variables difusas.
            **kwargs: Variables de entrada como TEMP, pH, etc.
        """
        self.custom_vars = custom_vars
        self.inputs = kwargs
        self.available_vars = {k: v for k, v in self.inputs.items() if not np.isnan(v)}
        self.condiciones = np.nan

        # Verificar que al menos una variable esté disponible
        if not self.available_vars:
            raise ValueError("Se requiere al menos la TEMP o el pH para evaluar las condiciones adicionales.")

        # Definir el orden de prioridad de las variables si es necesario
        self.priority_variables = ['TEMP', 'pH']  # Puedes ajustar el orden según la lógica requerida

        # Filtrar las variables disponibles según la prioridad
        self.available_vars = {k: v for k, v in self.available_vars.items() if k in self.priority_variables}

        self._init_variable_definitions()
        self._crear_sistema_difuso()

    def _init_variable_definitions(self):
        self.base_vars = dict(
            TEMP=dict(
                universe = np.arange(0, 35.1, 0.1),
                mf_definitions = {
                    'MUY_BAJA': {'type': 'trapmf', 'params': [0, 0, 4, 6]},
                    'BAJA': {'type': 'trimf', 'params': [4, 8, 12]},
                    'MODERADA': {'type': 'trimf', 'params': [10, 18, 26]},
                    'ALTA': {'type': 'trapmf', 'params': [24, 28, 35, 35]}
                }
            ),
            pH=dict(
                universe = np.arange(5, 10.1, 0.1),
                mf_definitions = {
                    'ACIDO': {'type': 'trapmf', 'params': [5, 5, 6, 6.5]},
                    'NEUTRO': {'type': 'trimf', 'params': [6, 7, 8]},
                    'ALCALINO': {'type': 'trapmf', 'params': [7.5, 8.5, 10, 10]}
                }
            )
        )

        for var_name, var_content in self.custom_vars.items():
            self.base_vars[var_name] = var_content

    def _crear_sistema_difuso(self):
        """
        Crea el sistema difuso basado en las variables disponibles.
        Define las reglas y configura el sistema de control.
        """
        # Inicializar estructuras
        self.rules = []
        self.variables_fuzzy = {}
        self.variables_disponibles = list(self.available_vars.keys())

        # Definir variables difusas según las variables disponibles
        for var in self.available_vars:
            if var in self.base_vars:
                universe, mf_definitions = self.base_vars[var]['universe'], self.base_vars[var]['mf_definitions']
                antecedent = ctrl.Antecedent(universe, var)
                for label, params in mf_definitions.items():
                    if params['type'] == 'trapmf':
                        antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                    elif params['type'] == 'trimf':
                        antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
                self.variables_fuzzy[var] = antecedent
            else:
                raise ValueError(f"Definición de variable desconocida: {var}")

        # Definir la variable de salida
        self.condiciones_universe = np.arange(0, 1.01, 0.01)
        self.condiciones_var = ctrl.Consequent(self.condiciones_universe, 'condiciones')
        self.condiciones_var['DESFAVORABLES'] = fuzz.trapmf(self.condiciones_var.universe, [0, 0, 0.2, 0.4])
        self.condiciones_var['NEUTRALES'] = fuzz.trimf(self.condiciones_var.universe, [0.3, 0.5, 0.7])
        self.condiciones_var['FAVORABLES'] = fuzz.trapmf(self.condiciones_var.universe, [0.6, 0.8, 1, 1])

        # Definir reglas difusas basadas en las variables disponibles
        self._definir_reglas()

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def _definir_reglas(self):
        """
        Define las reglas difusas basadas en las variables disponibles.
        """
        if 'TEMP' in self.variables_fuzzy and 'pH' in self.variables_fuzzy:
            temp = self.variables_fuzzy['TEMP']
            ph = self.variables_fuzzy['pH']

            # Regla 1: Condiciones FAVORABLES
            rule1 = ctrl.Rule(
                antecedent=((temp['MODERADA'] | temp['ALTA']) & ph['NEUTRO']),
                consequent=self.condiciones_var['FAVORABLES']
            )

            # Regla 2: Condiciones NEUTRALES
            rule2 = ctrl.Rule(
                antecedent=((temp['BAJA'] & ph['NEUTRO']) | ((temp['MODERADA'] | temp['ALTA']) & (ph['ACIDO'] | ph['ALCALINO']))),
                consequent=self.condiciones_var['NEUTRALES']
            )

            # Regla 3: Condiciones DESFAVORABLES
            rule3 = ctrl.Rule(
                antecedent=(temp['MUY_BAJA'] | (temp['BAJA'] & (ph['ACIDO'] | ph['ALCALINO']))),
                consequent=self.condiciones_var['DESFAVORABLES']
            )

            self.rules.extend([rule1, rule2, rule3])

        elif 'TEMP' in self.variables_fuzzy:
            temp = self.variables_fuzzy['TEMP']

            # Regla 1: Condiciones FAVORABLES
            rule1 = ctrl.Rule(
                antecedent=(temp['MODERADA'] | temp['ALTA']),
                consequent=self.condiciones_var['FAVORABLES']
            )

            # Regla 2: Condiciones NEUTRALES
            rule2 = ctrl.Rule(
                antecedent=temp['BAJA'],
                consequent=self.condiciones_var['NEUTRALES']
            )

            # Regla 3: Condiciones DESFAVORABLES
            rule3 = ctrl.Rule(
                antecedent=temp['MUY_BAJA'],
                consequent=self.condiciones_var['DESFAVORABLES']
            )

            self.rules.extend([rule1, rule2, rule3])

        elif 'pH' in self.variables_fuzzy:
            ph = self.variables_fuzzy['pH']

            # Regla 1: Condiciones FAVORABLES
            rule1 = ctrl.Rule(
                antecedent=ph['NEUTRO'],
                consequent=self.condiciones_var['FAVORABLES']
            )

            # Regla 2: Condiciones NEUTRALES
            rule2 = ctrl.Rule(
                antecedent=ph['ALCALINO'],
                consequent=self.condiciones_var['NEUTRALES']
            )

            # Regla 3: Condiciones DESFAVORABLES
            rule3 = ctrl.Rule(
                antecedent=ph['ACIDO'],
                consequent=self.condiciones_var['DESFAVORABLES']
            )

            self.rules.extend([rule1, rule2, rule3])
        else:
            raise ValueError("No hay suficientes variables disponibles para definir reglas.")

    def calcular_inferencia(self):
        """
        Calcula la inferencia difusa para determinar las condiciones adicionales.

        Retorna:
            tuple: (variables_usadas (str), confianza (float))
        """
        # Asignar los valores de entrada disponibles
        for var in self.available_vars:
            self.simulation.input[var] = self.available_vars[var]

        try:
            # Realizar la inferencia
            self.simulation.compute()

            # Obtener el resultado
            self.condiciones = self.simulation.output['condiciones']
        except Exception as e:
            raise ValueError(f"Error al calcular la inferencia: {e}")

        # Determinar variables usadas y confianza
        if 'TEMP' in self.variables_fuzzy and 'pH' in self.variables_fuzzy:
            variables_usadas = 'TEMP_pH'
            confianza = 1.0
        elif 'TEMP' in self.variables_fuzzy:
            variables_usadas = 'TEMP'
            confianza = 0.5
        elif 'pH' in self.variables_fuzzy:
            variables_usadas = 'pH'
            confianza = 0.25
        else:
            variables_usadas = 'NONE'
            confianza = 0.0

        return (variables_usadas, confianza)

    def obtener_etiqueta(self):
        """
        Obtiene la etiqueta correspondiente a las condiciones inferidas.

        Retorna:
            str: Etiqueta de las condiciones ('DESFAVORABLES', 'NEUTRALES', 'FAVORABLES').
        """
        if np.isnan(self.condiciones):
            raise ValueError("No se ha calculado la inferencia de condiciones.")

        # Determinar la etiqueta con mayor grado de pertenencia
        grados_pertenencia = {}
        for etiqueta in self.condiciones_var.terms:
            funcion_pertenencia = self.condiciones_var[etiqueta].mf
            grado = fuzz.interp_membership(self.condiciones_var.universe, funcion_pertenencia, self.condiciones)
            grados_pertenencia[etiqueta] = grado

        etiqueta_predicha = max(grados_pertenencia, key=grados_pertenencia.get)
        return etiqueta_predicha
