import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class AdditionalConditions:
    def __init__(self, custom_vars=dict(), **kwargs):
        """
        Inicializa la clase CondicionesAdicionales.

        Parámetros:
            custom_vars (dict): Definiciones personalizadas de vars difusas.
            **kwargs: Variables de entrada como TEMP, pH, etc.
        """
        self.custom_vars = custom_vars
        self.inputs = kwargs
        self.available_vars = {k: v for k, v in self.inputs.items() if not np.isnan(v)}
        self.additional_conditions = np.nan

        # Verificar que al menos una variable esté disponible
        if not self.available_vars:
            raise ValueError("Se requiere al menos la TEMP o el pH para evaluar las condiciones additional_conditions.")

        # Definir el orden de prioridad de las vars si es necesario
        self.priority_vars = ['TEMP', 'pH']  # Puedes ajustar el orden según la lógica requerida

        # Filtrar las vars disponibles según la prioridad
        self.available_vars = {k: v for k, v in self.available_vars.items() if k in self.priority_vars}

        self._init_variable_definitions()
        self._create_fuzzy_system()

    def _init_variable_definitions(self):
        self.base_vars = dict(
            TEMP=dict(
                universe = np.arange(0, 35.1, 0.1),
                mf_definitions = {
                    'VERY LOW': {'type': 'trapmf', 'params': [0, 0, 4, 6]},
                    'LOW': {'type': 'trimf', 'params': [4, 8, 12]},
                    'MODERATE': {'type': 'trimf', 'params': [10, 18, 26]},
                    'HIGH': {'type': 'trapmf', 'params': [24, 28, 35, 35]}
                }
            ),
            pH=dict(
                universe = np.arange(5, 10.1, 0.1),
                mf_definitions = {
                    'ACID': {'type': 'trapmf', 'params': [5, 5, 6, 6.5]},
                    'NEUTRAL': {'type': 'trimf', 'params': [6, 7, 8]},
                    'ALKALINE': {'type': 'trapmf', 'params': [7.5, 8.5, 10, 10]}
                }
            )
        )

        for var_name, var_content in self.custom_vars.items():
            self.base_vars[var_name] = var_content

    def _create_fuzzy_system(self):
        """
        Crea el sistema difuso basado en las vars disponibles.
        Define las reglas y configura el sistema de control.
        """
        # Inicializar estructuras
        self.rules = []
        self.vars_fuzzy = {}
        
        # Definir vars difusas según las vars disponibles
        for var in self.available_vars:
            if var in self.base_vars:
                universe, mf_definitions = self.base_vars[var]['universe'], self.base_vars[var]['mf_definitions']
                antecedent = ctrl.Antecedent(universe, var)
                for label, params in mf_definitions.items():
                    if params['type'] == 'trapmf':
                        antecedent[label] = fuzz.trapmf(antecedent.universe, params['params'])
                    elif params['type'] == 'trimf':
                        antecedent[label] = fuzz.trimf(antecedent.universe, params['params'])
                self.vars_fuzzy[var] = antecedent
            else:
                raise ValueError(f"Definición de variable desconocida: {var}")

        # Definir la variable de salida
        self.additional_conditions_universe = np.arange(0, 1.01, 0.01)
        self.additional_conditions_var = ctrl.Consequent(self.additional_conditions_universe, 'condiciones')
        self.additional_conditions_var['UNFAVORABLE'] = fuzz.trapmf(self.additional_conditions_var.universe, [0, 0, 0.2, 0.4])
        self.additional_conditions_var['NEUTRALS'] = fuzz.trimf(self.additional_conditions_var.universe, [0.3, 0.5, 0.7])
        self.additional_conditions_var['FAVORABLE'] = fuzz.trapmf(self.additional_conditions_var.universe, [0.6, 0.8, 1, 1])

        # Definir reglas difusas basadas en las vars disponibles
        self._define_rules()

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def _define_rules(self):
        """
        Define las reglas difusas basadas en las vars disponibles.
        """
        if 'TEMP' in self.vars_fuzzy and 'pH' in self.vars_fuzzy:
            temp = self.vars_fuzzy['TEMP']
            ph = self.vars_fuzzy['pH']

            # Regla 1: Condiciones FAVORABLE
            rule1 = ctrl.Rule(
                antecedent=((temp['MODERATE'] | temp['HIGH']) & ph['NEUTRAL']),
                consequent=self.additional_conditions_var['FAVORABLE']
            )

            # Regla 2: Condiciones NEUTRALS
            rule2 = ctrl.Rule(
                antecedent=((temp['LOW'] & ph['NEUTRAL']) | ((temp['MODERATE'] | temp['HIGH']) & (ph['ACID'] | ph['ALKALINE']))),
                consequent=self.additional_conditions_var['NEUTRALS']
            )

            # Regla 3: Condiciones UNFAVORABLE
            rule3 = ctrl.Rule(
                antecedent=(temp['VERY LOW'] | (temp['LOW'] & (ph['ACID'] | ph['ALKALINE']))),
                consequent=self.additional_conditions_var['UNFAVORABLE']
            )

            self.rules.extend([rule1, rule2, rule3])

        elif 'TEMP' in self.vars_fuzzy:
            temp = self.vars_fuzzy['TEMP']

            # Regla 1: Condiciones FAVORABLE
            rule1 = ctrl.Rule(
                antecedent=(temp['MODERATE'] | temp['HIGH']),
                consequent=self.additional_conditions_var['FAVORABLE']
            )

            # Regla 2: Condiciones NEUTRALS
            rule2 = ctrl.Rule(
                antecedent=temp['LOW'],
                consequent=self.additional_conditions_var['NEUTRALS']
            )

            # Regla 3: Condiciones UNFAVORABLE
            rule3 = ctrl.Rule(
                antecedent=temp['VERY LOW'],
                consequent=self.additional_conditions_var['UNFAVORABLE']
            )

            self.rules.extend([rule1, rule2, rule3])

        elif 'pH' in self.vars_fuzzy:
            ph = self.vars_fuzzy['pH']

            # Regla 1: Condiciones FAVORABLE
            rule1 = ctrl.Rule(
                antecedent=ph['NEUTRAL'],
                consequent=self.additional_conditions_var['FAVORABLE']
            )

            # Regla 2: Condiciones NEUTRALS
            rule2 = ctrl.Rule(
                antecedent=ph['ALKALINE'],
                consequent=self.additional_conditions_var['NEUTRALS']
            )

            # Regla 3: Condiciones UNFAVORABLE
            rule3 = ctrl.Rule(
                antecedent=ph['ACID'],
                consequent=self.additional_conditions_var['UNFAVORABLE']
            )

            self.rules.extend([rule1, rule2, rule3])
        else:
            raise ValueError("No hay suficientes vars disponibles para definir reglas.")

    def calculate_inference(self):
        """
        Calcula la inferencia difusa para determinar las condiciones additional_conditions.

        Retorna:
            tuple: (used_vars (str), confidence (float))
        """
        # Asignar los valuees de entrada disponibles
        for var in self.available_vars:
            self.simulation.input[var] = self.available_vars[var]

        try:
            # Realizar la inferencia
            self.simulation.compute()

            # Obtener el resultado
            self.additional_conditions = self.simulation.output['condiciones']
        except Exception as e:
            raise ValueError(f"Error al calcular la inferencia: {e}")

        # Determinar vars usadas y confidence
        if 'TEMP' in self.vars_fuzzy and 'pH' in self.vars_fuzzy:
            used_vars = 'TEMP_pH'
            confidence = 1.0
        elif 'TEMP' in self.vars_fuzzy:
            used_vars = 'TEMP'
            confidence = 0.5
        elif 'pH' in self.vars_fuzzy:
            used_vars = 'pH'
            confidence = 0.25
        else:
            used_vars = 'NONE'
            confidence = 0.0

        return (used_vars, confidence)

    def get_label(self):
        """
        Obtiene la label correspondiente a las condiciones inferidas.

        Retorna:
            str: Etiqueta de las condiciones ('UNFAVORABLE', 'NEUTRALS', 'FAVORABLE').
        """
        if np.isnan(self.additional_conditions):
            raise ValueError("No se ha calculado la inferencia de condiciones.")

        # Determinar la label con mayor degree de pertenencia
        membership_degrees = {}
        for label in self.additional_conditions_var.terms:
            membership_function = self.additional_conditions_var[label].mf
            degree = fuzz.interp_membership(self.additional_conditions_var.universe, membership_function, self.additional_conditions)
            membership_degrees[label] = degree

        predicted_label = max(membership_degrees, key=membership_degrees.get)
        return predicted_label
